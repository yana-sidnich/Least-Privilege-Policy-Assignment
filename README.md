# AWS Lambda Assignment - Contrast Security

This repository contains my solution to given home assignment. There are two .py file:

1.  solution.py - containing the solution not including the bonus part.
2.  solution_extra_points.py - containing the solution including the bonus part.

# My Work Process

## First Step

Before this assignment I didn't a lot of have experience working with aws services.
My first step was getting familiar with the AWS CLI, I followed the installation steps in the AWS documentation and watched [the following youtube guide](https://www.youtube.com/watch?v=PWAnY-w1SGQ&t=847s) , focusing on the parts I thought was relevant for this assignment. My next step was to read some information about lambda's policies. In this process learned about IAM execution roles, role's policies and how lambda function are created and managed.

## Second Step

My next step was starting to extract as much information I could about the lambda function. I configured the credentials with the one you provided me with so I can start working with the CLI. The first step was getting the function's code so I can inspect it. In order to do that I searched the right command inside the AWS CLI commands reference, and I found the get-function command. Running this command resulted with the following output:
![contrast1](https://photos.app.goo.gl/FQsFGr4xkphYXhk19)

we can see the Code section in the output which contains the location of the files. From looking at the URL I assumed the code is located inside a S3 bucket. I pasted the URL and downloaded the file. My next step was looking at the code and as guided, try to look for all the actions inside the code. We can see that using the AWS SDK boto3 we opened 2 clients, one for the S3 services, and one for the dynamoDB services. Next lets look for all the function that are triggered on both of this clients:

1.  s3:
    get_object()

2.  dynamoDB:
    describe_table()
    transact_get_items()
    put_item()

To my understanding each function is an action that requires a permission, so my next step was looking for the required permissions. Again turning to google and the AWS documentation I found [this page](https://docs.aws.amazon.com/service-authorization/latest/reference/reference_policies_actions-resources-contextkeys.html) which lists all the actions for eash AWS service. I listed to myself all the actions that need to be in our policy document:

2.  s3:
    get_object() =====> s3:GetObjectAcl

3.  dynamoDB:
    decribe_table() =====> dynamodb:DescribeTable
    transact_get_items() =====> dynamodb:GetItem
    put_item() =====> dynamodb:PutItem

(I want to be honest, until now I'm not sure about my answer, to my understanding a permission is an action listed inside the policy document, if an action is listed then the lambda is granted the permission to call this function and use this service's functions, I hope I got it right :) ).

next step was looking into our function policy. From what I figured out the policy is strongly connected to the execution role of the function, the function's policies are the policies of the function's execution role. The role name can be seen in the first picture, what we need is the last part of the string, after the '/' character: **"sample_s3_dynamodb-role-ay0f0nbb"**.
using this name and the following command we got the following output:
![contrast 2 ](https://photos.app.goo.gl/re6beWoS1Lj8LHeS9)
We can see that the function's role has one policy named **"policy_sample"**. Now using the role's and policy's names we can get more information about the policy using the following command (The output is partial, the full one can be seen in the sample_policy.txt file):
![contrast3](https://photos.app.goo.gl/Z7j9qLDWQmoGzADC6)
We can see there are a lot more policies granted to our lambda function, more that needed, and we need to fix that.
(Again, I want to be honest, it was very weird to me that there are all of this actions granted for our function, and even more it bothered be that the permission I stated that we need to have are not in this list, I hope I'm on the right track here....).

## Step Three

My next step was to implement the needed changes in the util class given me. I added the actions and the corresponding permissions. This step is pretty self explanatory, you can see the changes inside the code obviously.

## Step Four

Finally, the coding part :)
for this step, the workflow has some assumptions:

1. For the solution.py The code and policy are local files
2. The solution script is called using 'python solution.py <lambda code file path> <policy json file path>, for example - 'python3.10 solution.py lambda_function.py sample_policy.json'
3. The solution_extra_points.py expects the lambda name as an argument.
4. This solution was checked python with 3.8.10, and python 3.10

In this part, I developed and checked in stages:
On the Policy part: 5. Understand the policy JSON structure 6. Manually configured a specific policy action list - to verify I am able to configure the correct location . 7. Once configured correctly - I wrapped this logic inside its own independent function.

At every stage everything is printed out in order to verify correctness of the solution.

On the function part:

1. First of all I tried to extract the actions and print them to the screen - in order to verify that the actions done by the lambda are correctly caught.
2. Once I saw this works, I generated the list of permissions needed from those actions, and again, verified it works using prints, the prints were used as a kind of manual testing and verification to the correctness of the solution, over all the development stages (The purpose is to check myself after every small step, in order to see that the output is what I expect it to be).

Combining the functionalities:
Once both parts were investigated and done, we are left with the task of changing the given policy to follow the principle of least privileged. This was done by replacing the Actions section inside every statement to contain only the actions/permissions that are needed.
(One more honest explanation, I realized I assumed that each role can have only one policy, and I guess that "in the real world" it can have many policies. the change to the code is not that big, the functionality is there, I just need to loop on all the policies of the role and apply the logic to each on of them. In addition we can change the logic a bit, if we know that the actions we need are included in the given policy we can use the intersection function to filter all the unneeded actions from each statement. Right now all Actions in each statement are changed to the same needed actions/permissions ). Finally our function returns the new policy as dict (basically a JSON), and the main function exports it to a local JSON file.
Of course additional documentation is available inside the code itself.

There are two seperate scripts:

1. The first - solution.py - assumes the input is loaded from local files. The file paths are sent on the command line execution.
2. The second - solution_extra_points.py, receives the lambda name as an argument, and it extracts both lambda code and lambda policy, using the boto3 - aws sdk. This script reuses the functions and logic inside the original solution script.

## Summery

First of all thank you for this opportunity : )
When I started this assignment I had more of a theoretical knowledge about lambda function and some other AWS services like S3 bucket, but I needed to gain more hands on experience working with tools like AWS CLI, AWS SDK (boto3 in this case), and using the different AWS services inside my code projects. This assignment made me "get my hands dirty" and starts gaining experience with this tools.

I hope to hear from you if you see me fitted for this role, either way I would love to get a feedback from you about my submission :)

## Dependencies

The utility uses the following dependencies

1. argparse
2. requests
3. boto3
4. zipfile
5. pathlib

## Usage

solution.py script:

```
usage: solution.py [-h] lambda_code lambda_policy

Generate least privilage policy

positional arguments:
  lambda_code    Path to the lambda code.
  lambda_policy  Path to the lambda policy

optional arguments:
  -h, --help     show this help message and exit
```

output is sent to file least_privilaged_policy.json

solution_extra_points.py script:

```
usage: solution_extra_points.py [-h] lambda_name

Generate least privilage policy

positional arguments:
  lambda_name  name of lambda function

options:
  -h, --help   show this help message and exit
```

output is sent to file least_privilaged_policy_extra_points.json
