import os
import yaml
from github import Github
import logging

import os
import sys
from pprint import pprint
import yaml
import json
import re



def get_modified_workspaces_list():

    file_path = os.getenv("GITHUB_EVENT_PATH")
    github_token = os.getenv("token_github")
    github_repo_name = os.getenv("GITHUB_REPOSITORY")

    try:
        #repo_name = "vinitkapoor/altlantis_actions_test"

        files_names_list = []
        with open(file_path, 'r', encoding='UTF8') as event_file:
            event_payload_dict = yaml.load(event_file, Loader=yaml.FullLoader)
            # print(event_payload_dict)
            logging.info(event_payload_dict)


            # get pull request number, current supporting only opened pull requests.. need to check for editing etc.
            pull_request_number = event_payload_dict["number"]

            # call github api to get the file diff.
            # using an access token

            g = Github(github_token)
            # print("repo name:", github_repo_name)
            repo = g.get_repo(github_repo_name)

            # pull request number to be taken from event payload
            pr = repo.get_pull(pull_request_number)
            #print(pr.changed_files)
            logging.info(pr.changed_files)

            files_list = pr.get_files()

            logging.info(files_list.totalCount)
            # print(files_list.totalCount)

            for file in files_list.reversed:
                # print(file.filename)
                logging.info(file.filename)
                files_names_list.append(file.filename)

    except Exception as e:
        print(github_repo_name)
        print(e)

    return files_names_list

# check if the PR changes are in the allowed list of workspaces
def check_workspaces_list():

    # repo_name  = os.getenv("GITHUB_REPOSITORY")
    # repo_dir_name = os.getenv("WORKSPACE_PATH") + repo_name
    repo_dir_name = os.getenv("GITHUB_WORKSPACE")
    github_repo_name = os.getenv("GITHUB_REPOSITORY")
    head_branch = os.getenv("GITHUB_HEAD_REF")

    # repo name appears twice for some reason in the $GITHUB_REPOSITORY, below change is to address below
    github_repo_name_no_org = github_repo_name.split("/")[1]
    github_token = os.getenv("token_github")

    # define here the list of workspaces that are allowed to be modified via GitOps flow under tree_main
    # as regular expression to match:
    # \w+ matches one or more alphanumeric characters
    # [a-z][a-z]-[a-z]+-1 matches region name e.g., us-ashburn-1
    # trailing slash ensures that there is one folder after the region name
    allowed_ws_re_list = [
        'eightxeightmain/children/\w+/children/\w+/resources/[a-z][a-z]-[a-z]+-1/[a-zA-Z0-9-_]+/',  # regular ws
        'eightxeightmain/iam/\w+/'  # iam ws
        #'dir1/dir2/\w+/'
    ]

    dir_set = set()

    # checkout of the tree_test as the repo which is originally checked out is the workflows repo
    clone_cmd = "git clone -b " + head_branch + " https://sa-selfservice:" + github_token + "@github.com/" + github_repo_name
    # print(clone_cmd)
    os.system(clone_cmd)
    # checkout_cmd = "git checkout " + head_branch
    # print(checkout_cmd)
    # os.system(checkout_cmd)

    for files in get_modified_workspaces_list():
        for ws in allowed_ws_re_list:

            regex_result = re.match(ws, files)

            if regex_result is not None:
                # regex_result.group(0) - group 0 is reserved and will always return the whole match.
                # https://docs.python.org/3/library/re.html#match-objects
                dir_name = regex_result.group(0)

                # print(dir_name)
                # print(os.system('ls -l'))
                # print(os.system('pwd'))

                full_path = repo_dir_name + '/' + github_repo_name_no_org + '/' + dir_name + 'terragrunt.hcl'
                # print(full_path)
                if os.path.exists(full_path):
                    # print('full_path detected: {}'.format(full_path))
                    # print('dir_name added: {}'.format(dir_name))
                    dir_set.add(dir_name)

    return dir_set


def printEnvValues():
    file_path = os.getenv("GITHUB_EVENT_PATH")
    print("GITHUB_EVENT_PATH: {0}", file_path)

    github_token = os.getenv("token_github")
    print("GITHUB_TOKEN: {0}", github_token)

    github_repo_name = os.getenv("GITHUB_REPOSITORY")
    print("GITHUB_REPOSITORY: {0}", github_repo_name)

    github_path = os.getenv("GITHUB_PATH")
    print("GITHUB_PATH: {0}", github_path)

    github_workspace = os.getenv("GITHUB_WORKSPACE")
    print("GITHUB_WORKSPACE: {0}", github_workspace)


# evaluate the PR and return the verdict
def main():
    # printEnvValues()
    repo_dir_name = os.getenv("GITHUB_WORKSPACE")
    logging.basicConfig(filename='output.log', encoding='utf-8', level=logging.DEBUG)

    results_dict = {
        'status': 'OK',
        'message': 'Singe Workspace modified',
        'changed_workspaces_list': [],
        'workspace_dir': ''
    }



    dir_list = list(check_workspaces_list())
    # dir_list = []

    if len(dir_list) > 1:
        print('More than ONE workspace is modified in this Pull Request: \n ---')

        pprint(dir_list)
        results_dict['status'] = 'FAIL'
        results_dict['message'] = 'Multiple Workspaces were modified'
        results_dict['changed_workspaces_list'] = dir_list

    elif len(dir_list) == 1:
        results_dict['workspace_dir'] = repo_dir_name + '/' + dir_list[0]
        results_dict['message'] = 'Singe Workspace modified'
        results_dict['changed_workspaces_list'].append(results_dict['workspace_dir'])
        print('Single WS modified: {}'.format(results_dict['workspace_dir']))

    else:
        # No WS modified
        results_dict['message'] = 'NO WOrkspace was modified in this PR!!! It is OK, but just there is nothing to check'
        print('No workspace modified')

    out_file = "output.yml"
    with open(out_file, 'w') as f:
        yaml.dump(results_dict, f)


if __name__ == '__main__':
    main()


