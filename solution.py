import json
import sys
import os
import argparse
from pathlib import Path


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
    parser.add_argument('lambda_code', help='Path to the lambda code.')
    parser.add_argument('lambda_policy', help='Path to the lambda policy')
    return parser


#returns a list containing the needed permissions for the action in the given actions list
def get_permissions(actions: list) -> list:
    action_converter = ActionsConverter()
    permissions = []
    for action in actions:
        premmision = action_converter.actions_to_permissions.get(action)
        permissions.extend(premmision)
    return permissions


# def intersect(l1 : list, l2 : list):
#     print(list(set(l1).intersection(l2)))
#     return list(set(l1).intersection(l2))


def update_statement(statement: dict, permissions: list):
    statement['Action'] = permissions


"""
given the lambda's code and current policy we:
    1. find all the action inside the function's code.
    2. find the needed permissions for those actions.
    3. edit the given policy data, remove uneeded permissions and add the new ones. 
"""


def generate_least_privilage(lambda_code: str, lambda_policies: str) -> dict:
    found_actions = ActionsConverter().find_actions(lambda_code)
    needed_permissions = get_permissions(found_actions)
    policy_json = json.loads(lambda_policies)

    if isinstance(policy_json['PolicyDocument']['Statement'], list):
        for statement in policy_json['PolicyDocument']['Statement']:
            update_statement(statement, needed_permissions)

    else:  # dict
        update_statement(policy_json['PolicyDocument']['Statement'],
                         needed_permissions)

    return policy_json


#export the least privilaged policy to JSON file
def export_json_to_file(policy_data, file_name):
    least_privilaged_policy_json = json.dumps(policy_data, indent=4)
    with open(file_name, 'w') as outfile:
        outfile.write(least_privilaged_policy_json)


def main():
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args()
    if not (os.path.exists(parsed_args.lambda_code)
            and os.path.exists(parsed_args.lambda_policy)):
        print("please check the provided paths, one of them doesn't exists")
        return

    lambda_code = Path(parsed_args.lambda_code).read_text()
    lambda_policy = Path(parsed_args.lambda_policy).read_text()
    least_privilaged_policy = generate_least_privilage(lambda_code,
                                                       lambda_policy)
    export_json_to_file(least_privilaged_policy,
                        'least_privilaged_policy.json')


if __name__ == '__main__':
    main()
