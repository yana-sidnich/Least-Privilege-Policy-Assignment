import json
import sys
import os
import argparse
from pathlib import Path


def create_arg_parser():
    # Creates and returns the ArgumentParser object

    parser = argparse.ArgumentParser(
        description='Generate least privilage policy')
    parser.add_argument('lambda_code', help='Path to the lambda code.')
    parser.add_argument('lambda_policy', help='Path to the lambda policy')
    return parser


def main():
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args(sys.argv[1:])
    if not (os.path.exists(parsed_args.lambda_code)
            and os.path.exists(parsed_args.lambda_policy)):
        print("please check the provided paths, one of them does'nt exists")
        return

    lambde_code = Path(parsed_args.lambda_code).read_text()
    lambde_policy = Path(parsed_args.lambda_policy).read_text()
    data = json.loads(lambde_policy)
    data2 = data['RoleName']

    # print(lambde_code)
    print(data)


if __name__ == '__main__':
    main()
