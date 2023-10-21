#!/bin/python

import boto3
from dotenv import load_dotenv

if __name__ == '__main__':
    load_dotenv()
    s3 = boto3.client('s3')
    print(s3.list_buckets())