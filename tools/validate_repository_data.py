#!/usr/bin/env python3
"""Validate the repository definitions under data/.

Offline checks (always run):

* a repository file describes exactly one repository
* the file name matches the repository key, so a repository is easy to find
  and a typo in the file name cannot hide a definition
* a private repository declares both ``private: true`` and
  ``visibility: private``, and neither contradicts the other

Online check (only when GITHUB_TOKEN is set):

* a repository that is private on GitHub declares both keys

The online check guards the case that made a private repository public: an
undeclared attribute is not managed, so the repository silently depends on
whatever the tooling defaults to instead of on this data. ``visibility`` is
sent alongside ``private`` and overrides it, so a lone ``private: true`` is
not enough.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

import yaml

ORGS_DIR = os.path.join("data", "github", "orgs")
GITHUB_API = "https://api.github.com"


def repository_files(root):
    orgs_dir = os.path.join(root, ORGS_DIR)
    for org in sorted(os.listdir(orgs_dir)):
        repos_dir = os.path.join(orgs_dir, org, "repositories")
        if not os.path.isdir(repos_dir):
            continue
        for name in sorted(os.listdir(repos_dir)):
            if name.endswith((".yml", ".yaml")):
                yield org, os.path.join(repos_dir, name)


def check_offline(root):
    errors = []
    for org, path in repository_files(root):
        name = os.path.basename(path)
        stem = name.rsplit(".", 1)[0]
        with open(path) as fd:
            document = yaml.safe_load(fd) or {}

        if len(document) != 1:
            errors.append(
                f"{path}: expected exactly one repository, got "
                f"{sorted(document)}")
            continue

        repo, config = next(iter(document.items()))
        if repo != stem:
            errors.append(
                f"{path}: file name does not match repository "
                f"{repo!r}; rename it to {repo}.yml")
        if not isinstance(config, dict):
            errors.append(f"{path}: {repo} must be a mapping")
            continue

        private = config.get("private")
        visibility = config.get("visibility")
        wants_private = private is True or visibility == "private"
        declared_both = private is True and visibility == "private"
        if wants_private and not declared_both:
            errors.append(
                f"{path}: a private repository must declare both "
                f"'private: true' and 'visibility: private'; got "
                f"private={private!r} visibility={visibility!r}")
        elif private is False and visibility not in (None, "public",
                                                     "internal"):
            errors.append(
                f"{path}: private=false contradicts "
                f"visibility={visibility!r}")
    return errors


def github_private_repos(org, token):
    private = set()
    page = 1
    while True:
        request = urllib.request.Request(
            f"{GITHUB_API}/orgs/{org}/repos?per_page=100&page={page}",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
        if not payload:
            return private
        private.update(r["name"] for r in payload if r["private"])
        page += 1


def check_online(root, token):
    errors = []
    seen = {}
    for org, path in repository_files(root):
        with open(path) as fd:
            document = yaml.safe_load(fd) or {}
        if len(document) != 1:
            continue
        repo, config = next(iter(document.items()))
        if not isinstance(config, dict):
            continue
        if org not in seen:
            try:
                seen[org] = github_private_repos(org, token)
            except urllib.error.HTTPError as exc:
                print(f"warning: cannot read {org} from GitHub: {exc}",
                      file=sys.stderr)
                seen[org] = None
        private_repos = seen[org]
        if private_repos is None or repo not in private_repos:
            continue
        declared_both = config.get("private") is True
        declared_both &= config.get("visibility") == "private"
        if not declared_both:
            errors.append(
                f"{path}: {org}/{repo} is private on GitHub but does not "
                f"declare both 'private: true' and 'visibility: private'")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repository root")
    args = parser.parse_args()

    errors = check_offline(args.root)

    token = os.environ.get("GITHUB_TOKEN")
    if token:
        errors.extend(check_online(args.root, token))
    else:
        print("GITHUB_TOKEN is not set, skipping the online visibility check")

    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        print(f"{len(errors)} problem(s) found", file=sys.stderr)
        return 1
    print("repository data is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
