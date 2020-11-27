# Gitstyring
Github management by Ansible via specific role.

# Ansible Role: Gitcontrol
Manage your organization repositories(**later will add other stuff**) at Github:

## Structure
Describe all your organizations in `orgs/{{ structure_name }}/`,

**Each organization must have next folder structure:**
```yaml
org:
  name:
    people:
      dismissed_members.yml
      members.yml
    repositories:
      repo_name.yml
    teams:
      dismissed_members.yml
      members.yml
```

```Currently works only repo management```
## Repositories

Describe your repositories in `orgs/my_org/repositories/my_repo.yml`, file name should be equal to repo name, and one repo per file:
```yaml
my_repo:
  default_branch: main
  description: >-
    Brief description.  Try to fit it in one line.  As linefeeds are not allowed here.
  homepage: https://example.com
  language: Python
  archived: true / false # this is one direction road: once archived the repo can be unarchived via web only
  has_issues: true / false
  has_projects: true
  has_wiki: true / false
  private: true / false
  delete_branch_on_merge: false
  allow_merge_commit: false
  allow_squash_merge: true
  allow_rebase_merge : false
  teams:
    maintain: # List of teams who need to manage the repository without access to sensitive or destructive actions.
    pull: # List of teams who can only read this repo.
    push: # List of teams with push access.
    admin: # List of admin teams.
      - csm
  collaborators:
    maintain: # List of members who need to manage the repository without access to sensitive or destructive actions.
    pull: # List of members who can only read this repo.
    push: # List of members with push access.
    admin:  # List of admin members.
      - anton-sidelnikov
  protection_rules: # do not change protection rules structure all fields is required
    main: # branch name which already created in branch protection rules
      required_status_checks:
        strict: true / false
        contexts: # The list of status checks to require in order to merge into this branch
          - eco/check
      enforce_admins: true
      required_pull_request_reviews:
        dismissal_restrictions:
          users: [] # list of members or empty list
          teams: [] # list of teams or empty list
        dismiss_stale_reviews: true
        require_code_owner_reviews: false
        required_approving_review_count: 1
      restrictions:
        users: [] # list of members or empty list
        teams: [] # list of teams or empty list
        apps: # list of app slugs with push access
          - otc-zuul
      required_linear_history: false
      allow_force_pushes: false
      allow_deletions: false

```
* Those teams and collaborators should exist in organization.

# How to use it

Firstly:
- export GITHUB_TOKEN="github-token"
- export GITHUB_USER="github-username"

To apply changes in your organization repositories run:
```
ansible-playbook playbooks/run.yml -e github_repos_state=present

```