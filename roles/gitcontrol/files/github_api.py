#!/usr/bin/python3
import os
from argparse import ArgumentParser

import requests as requests

github_user = os.getenv('GITHUB_USER')
github_token = os.getenv('GITHUB_TOKEN')
github_api = "https://api.github.com"
headers = {'Authorization': f'token {github_token}'}

test_data = {
    "key": "test-to-be-deleted",
    "value": {
        "allow_merge_commit": True,
        "allow_rebase_merge": True,
        "allow_squash_merge": True,
        "archived": False,
        "collaborators": {
            "admin": [
                "anton-sidelnikov",
                "otc-zuul"
            ],
            "maintain": None,
            "pull": [
                "lego963"
            ],
            "push": None
        },
        "default_branch": "master",
        "delete_branch_on_merge": False,
        "description": "Test Repo for Github Management Tool",
        "has_issues": True,
        "has_projects": True,
        "has_wiki": True,
        "homepage": None,
        "language": "Python",
        "private": False,
        "protection_rules": {
            "master": {
                "allow_deletions": False,
                "allow_force_pushes": False,
                "dismiss_stale": True,
                "include_administrators": True,
                "require_branches_up_before_merge": False,
                "require_linear_history": False,
                "require_signed_commits": False,
                "require_status_check": False,
                "restrict_who_can_push_to_match_br": [
                    "otc-zuul"
                ],
                "review_from_code_owners": False,
                "reviews": 1,
                "who_can_dismiss_pr_reviews": [
                    "anton-sidelnikov"
                ]
            }
        }
    }
}


def manage_collaborators(owner, repo):
    collaborators = repo['value']['collaborators']
    for clb in collaborators:
        if collaborators[clb]:
            for user in collaborators[clb]:
                username = user
                permission = {'permission': clb}
                res = requests.put(
                    f"{github_api}/repos/{owner}/{repo['key']}/collaborators/{username}?",
                    json=permission,
                    headers=headers,
                    timeout=15)
    return print("OK")


if __name__ == '__main__':
    args_parser = ArgumentParser(prog="github_api", description="Multi-purpose github api script")
    args_parser.add_argument("--endpoint", help="Selected github endpoint")
    args_parser.add_argument("--org", help="Repo owner")
    args_parser.add_argument("--repo", help="Repo data")
    args = args_parser.parse_args()
    if args.endpoint == "manage_collaborators":
        manage_collaborators(args.org, test_data)
