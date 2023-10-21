#!/bin/python

import sys
import os
import logging
import time

import boto3
from botocore.exceptions import ClientError
import zipfile
from dotenv import load_dotenv


def zip_video(video_path, video_name):
    zip_path = os.path.join(os.path.dirname(video_path), video_name.replace('mp4', 'zip'))
    zipf = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
    zipf.write(video_path + video_name, video_name)
    zipf.close()
    return zip_path


def upload_video(video_path, video_name):
    start = time.perf_counter()
    load_dotenv()
    s3 = boto3.client('s3')
    print(s3.list_buckets())

    try:
        s3.upload_file(video_path, 'my-bucket', video_name)
    except ClientError as e:
        logging.error(e)
        return False

    print(time.perf_counter() - start)

    return True


def update_video_with_transfer_accerleration(video_name):
    start = time.perf_counter()
    load_dotenv()
    s3 = boto3.client('s3')
    print(s3.list_buckets())

    try:
        s3.put_bucket_accelerate_configuration(
            Bucket='my-bucket',
            AccelerateConfiguration={
                'Status': 'Enabled'
            }
        )
    except ClientError as e:
        logging.error(e)
        return False

    print(time.perf_counter() - start)

    return True


def main():
    video_path = sys.argv[1]
    video_name = sys.argv[2]

    zip_path = zip_video(video_path, video_name)

    # update video with normal mode
    if (not upload_video(zip_path, os.path.basename(zip_path))):
        print('success to upload video with normal mode')

    # update video with transfer accerleration
    if (not update_video_with_transfer_accerleration(video_name)):
        print('success to upload video with transfer accerleration')

if __name__ == '__main__':
    main()