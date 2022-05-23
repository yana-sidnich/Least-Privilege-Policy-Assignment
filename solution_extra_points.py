import json
from symtable import Function
import sys
import os
import argparse
from pathlib import Path
import boto3
import requests
import zipfile


#given util class
class ActionsConverter:
    # Example of method calls and their permissions. out of 4 actions found in the code, 3 actions related to the dynamoDB_client needed to be added.
    actions_to_permissions = {
        's3_client.get_object': ['s3:GetObject'],
        'sqs_client.send_message_batch': ['sqs:SendMessage'],
        'sqs_client.create_queue': ['sqs:CreateQueue', 'sqs:TagQueue'],
        'dynamodb_client.delete_item': ['dynamodb:DeleteItem'],
        # Find the method calls in the example function and
        # add the correct permissions to support them
        'dynamodb_client.describe_table': ['dynamodb:DescribeTable'],
        'dynamodb_client.transact_get_items': ['dynamodb:GetItem'],
        'dynamodb_client.put_item': ['dynamodb:PutItem'],
    }

    def __init__(self) -> None:
        self.actions = self.actions_to_permissions.keys()

    def find_actions(self, input: str) -> list:
        found_actions = []
        for action in self.actions:
            if action in input:
                print('Found action', action, 'in input str')
                found_actions.append(action)
        return found_actions


# Creates and returns the ArgumentParser object
def create_arg_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description='Generate least privilage policy')
    parser.add_argument('lambda_name', help='name of lambda function')

    return parser


#returns a list containing the needed permissions for the action in the given actions list
def get_permissions(actions: list) -> list:
    action_converter = ActionsConverter()
    permissions = []
    for action in actions:
        premmision = action_converter.actions_to_permissions.get(action)[0]
        permissions.append(premmision)

    return permissions


"""
given the lambda's code and current policy we:
    1. find all the action inside the function's code.
    2. find the needed permissions for those actions.
    3. edit the given policy data, remove uneeded permissions and add the new ones. 
"""


def generate_least_privilage(lambda_code: str, lambda_policies: dict) -> dict:
    action_converter = ActionsConverter()
    found_actions = action_converter.find_actions(lambda_code)
    needed_permissions = get_permissions(found_actions)
    # print(found_actions)
    # print(needed_permissions)

    lambda_policies['PolicyDocument']['Statement'][0][
        'Action'] = needed_permissions
    lambda_policies['PolicyDocument']['Statement'][1] = {}
    return lambda_policies


#convert the policy data into a JSON string
def to_json(policy_data):
    least_privilaged_policy_json = json.dumps(policy_data)
    with open('least_privilaged_policy.json', 'w') as outfile:
        outfile.write(least_privilaged_policy_json)


def download_url(url, save_path, chunk_size=128):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(save_path, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=chunk_size):
                fd.write(chunk)


def unzip_file(ziped_der, unziped_der):
    with zipfile.ZipFile(ziped_der, 'r') as zip_ref:
        zip_ref.extractall(unziped_der)


def download_function(url: str):
    zipped_file_name = 'lambda_func_code.zip'
    unzipped_file_name = 'lambda_func_code'
    download_url(url, zipped_file_name)
    unzip_file(zipped_file_name, unzipped_file_name)
    path_to_code_file = os.getcwd() + '/' + unzipped_file_name
    file_name = os.listdir(path_to_code_file)[0]
    return Path(file_name).read_text()


def extract_role_name(function_data: dict):
    return function_data['Configuration']['Role'].split('/')[-1]


def get_first_policy(role_name: str):
    iam_client = boto3.client('iam')
    role_policy_data = iam_client.list_role_policies(RoleName=role_name)
    lambda_policy_name = role_policy_data['PolicyNames'][0]
    return iam_client.get_role_policy(RoleName=role_name,
                                      PolicyName=lambda_policy_name)


def get_lambda_data(lambda_name: str):
    lambda_client = boto3.client('lambda')
    return lambda_client.get_function(FunctionName=lambda_name)


def main():
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args()

    function_data = get_lambda_data(lambda_name=parsed_args.lambda_name)
    lambda_code = download_function(url=function_data['Code']['Location'])
    policy_data = get_first_policy(role_name=extract_role_name(function_data))

    result = generate_least_privilage(lambda_code, policy_data)
    print(result)


if __name__ == '__main__':
    main()
