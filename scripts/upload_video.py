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


def upload_video(video_path, video_name, bucket_name):
    start = None
    load_dotenv()
    s3 = boto3.client('s3')

    # check bucket is exist
    if (not s3.list_buckets()):
        print('\033[31m'+'bucket is not exist')
        return False

    print('\033[33m' + 'uploading {0} to {1} ...'.format(video_name, bucket_name))

    # upload video
    try:
        start = time.perf_counter()
        s3.upload_file(video_path, bucket_name, video_name.replace('.zip', '_' + time.strftime('%Y%m%d%H%M%S') + '.zip'))
    except ClientError as e:
        logging.error(e)
        return False

    print('\033[33m' + 'upload time with Normal mode :{}'.format(time.perf_counter() - start))

    return True


def update_video_with_transfer_accerleration(video_path, video_name, bucket_name):
    start = None
    load_dotenv()
    s3 = boto3.client('s3')

    # check bucket is exist
    if (not s3.list_buckets()):
        print('\033[31m' + 'bucket is not exist')
        return False

    print('\033[33m' + 'uploading {0} to {1} ...'.format(video_name, bucket_name))

    try:
        s3.put_bucket_accelerate_configuration(
            Bucket=bucket_name,
            AccelerateConfiguration={
                'Status': 'Enabled'
            }
        )
        start = time.perf_counter()
        s3.upload_file(video_path, bucket_name, video_name.replace('.zip', '_' + time.strftime('%Y%m%d%H%M%S') + '.zip'))
    except ClientError as e:
        logging.error(e)
        return False

    print('\033[33m' + 'upload time with transfer acceleration mode :{}'.format(time.perf_counter() - start))

    return True


def main():
    video_path = sys.argv[1]
    video_name = sys.argv[2]
    bucket_name = sys.argv[3]

    zip_path = zip_video(video_path, video_name)

    # update video with normal mode
    if (not upload_video(zip_path, os.path.basename(zip_path), bucket_name)):
        print('success to upload video with normal mode')

    # # update video with transfer accerleration
    if (not update_video_with_transfer_accerleration(zip_path, os.path.basename(zip_path), bucket_name)):
        print('success to upload video with transfer accerleration')

if __name__ == '__main__':
    main()