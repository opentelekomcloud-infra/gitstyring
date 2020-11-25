#!/usr/bin/python3
import os
from argparse import ArgumentParser

import requests as requests
import yaml

github_user = os.getenv('GITHUB_USER')
github_token = os.getenv('GITHUB_TOKEN')
github_api = "https://api.github.com"
headers = {'Authorization': f'token {github_token}'}
bad_statuses = [400, 404]


def read_yaml_file(path, org, endpoint, repo_name=None):
    if endpoint == "manage_collaborators":
        path += f'/{org}/repositories/{repo_name}.yml'
    with open(path, 'r') as file:
        data = yaml.load(file)
    return data


def manage_collaborators(owner, repo_name, repo):
    output = ''
    collaborators = repo[repo_name]['collaborators']
    for clb in collaborators:
        if collaborators[clb]:
            for user in collaborators[clb]:
                res = requests.put(
                    f"{github_api}/repos/{owner}/{repo_name}/collaborators/{user}?",
                    json={'permission': clb},
                    headers=headers,
                    timeout=15)
                if res.status_code in bad_statuses:
                    output += f'user {user} not created: {res.status_code}'
    return output


if __name__ == '__main__':
    args_parser = ArgumentParser(prog="github_api", description="Multi-purpose github api script")
    args_parser.add_argument("--endpoint", help="Selected github endpoint")
    args_parser.add_argument("--org", help="Repo owner")
    args_parser.add_argument("--repo", help="Repo data")
    args_parser.add_argument("--root", help="Root directory to fetch files")
    args = args_parser.parse_args()
    if args.endpoint == "manage_collaborators":
        manage_collaborators(
            owner=args.org,
            repo_name=args.repo,
            repo=read_yaml_file(path=args.root, org=args.org, repo_name=args.repo, endpoint=args.endpoint)
        )
