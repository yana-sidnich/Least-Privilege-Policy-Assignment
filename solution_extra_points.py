import os
import argparse
from pathlib import Path
import boto3
import requests
import zipfile
# Local import of soltuion.py function
from solution import generate_least_privilage, export_json_to_file


# Creates and returns the ArgumentParser object
def create_arg_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description='Generate least privilage policy')
    parser.add_argument('lambda_name', help='name of lambda function')

    return parser


# Download the content of the url path to a local file
def download_url(url: str, save_path: str, chunk_size=128):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(save_path, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=chunk_size):
                fd.write(chunk)


# Unzip given zipped directory to requested directory
def unzip_file(ziped_dir: str, unziped_dir: str):
    with zipfile.ZipFile(ziped_dir, 'r') as zip_ref:
        zip_ref.extractall(unziped_dir)


# Download the specific code of the lambda, read and return it as a string.
def download_function(url: str):
    zipped_file_name = 'lambda_func_code.zip'
    unzipped_file_name = 'lambda_func_code'
    download_url(url, zipped_file_name)
    unzip_file(zipped_file_name, unzipped_file_name)
    path_to_code_file = os.getcwd() + '/' + unzipped_file_name
    file_name = os.listdir(path_to_code_file)[0]
    return Path(file_name).read_text()


# Get the role name out of the function data
def extract_role_name(function_data: dict):
    return function_data['Configuration']['Role'].split('/')[-1]


# Using the iam boto3 client, we retrieve the first policy of the specific role.
# Please note that this is an assumption that the lambda has only one policy.
# If in the future the lambda has more that one policy, this should be done looping on all policies.


def get_first_policy(role_name: str):
    iam_client = boto3.client('iam')
    role_policy_data = iam_client.list_role_policies(RoleName=role_name)
    lambda_policy_name = role_policy_data['PolicyNames'][0]
    # leaving the returning message as is - with the ResponseMetadata in it.
    return iam_client.get_role_policy(RoleName=role_name,
                                      PolicyName=lambda_policy_name)


# Get the data of the lambda using the boto3 lambda client.
def get_lambda_data(lambda_name: str):
    lambda_client = boto3.client('lambda')
    return lambda_client.get_function(FunctionName=lambda_name)


def main():
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args()

    function_data = get_lambda_data(lambda_name=parsed_args.lambda_name)
    lambda_code = download_function(url=function_data['Code']['Location'])
    policy_data = get_first_policy(role_name=extract_role_name(function_data))
    least_privileged_policy = generate_least_privilage(lambda_code,
                                                       policy_data)
    export_json_to_file(least_privileged_policy,
                        'least_privilaged_policy_extra_points.json')


if __name__ == '__main__':
    main()
