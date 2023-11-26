#!/bin/python

import sys
import os
import logging
import time
import datetime

import boto3
from boto3.s3.transfer import S3Transfer
from boto3.s3.transfer import TransferConfig
from botocore.exceptions import ClientError
import zipfile
from dotenv import load_dotenv

TARGET_FILE_EXT = '.mp4'
MULTIPART_THRESHOLD = 8 * 1024 * 1024
MAX_CONCURRENCY = 10
MULTIPART_CHUNKSIZE = 8388608
MAX_BANDWIDTH = 5000000

def zip_file(file_path, file_name):
    print(f"file_path is {file_path}")
    print(f"file_name is {file_name}")
    video_file_path = os.path.join(os.path.dirname(file_path), file_name.replace('.zip', TARGET_FILE_EXT))
    zip_path = os.path.join(os.path.dirname(file_path), file_name.replace(TARGET_FILE_EXT, '.zip'))
    print(f"video_file_path is {video_file_path}")
    print(f"zip_path is {zip_path}")

    zipf = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
    zipf.write(video_file_path, file_name)
    zipf.close()
    return zip_path


def check_local_dir_exist(local_file_dir):

    if not os.path.isdir(local_file_dir):
        return False

    return True

# check bucket exist or not in s3
def check_bucket_exist(client_s3, bucket_name) -> bool:

    # check bucket is exist
    if (not client_s3.list_buckets()):
        return False

    return True

# check upload dir exist or not in s3
def create_updload_dir_exist(client_s3, bucket_name) -> bool:

    # アップロード先Dirを日付から決定する
    upload_dir_from_current_date = datetime.datetime.now().strftime('%Y%m%d') + '/'
    print(f"upload dir is {upload_dir_from_current_date}")
    # アップロード先Dirが存在するか確認する
    result = client_s3.list_objects(Bucket=bucket_name, Prefix=upload_dir_from_current_date)
    print(f"result is {result}")
    # Contentがなければ、アップロード先Dirが存在しない
    # 存在しない場合には、アップロード先Dirを作成する
    if not "Contents" in result:
        client_s3.put_object(Bucket=bucket_name, Key=upload_dir_from_current_date)
        print("dcsacdsacdsa")
        print(f"create upload dir {upload_dir_from_current_date}")

        return False

    return True

def get_not_upload_files_in_local_dir(client_s3, bucket_name, local_file_dir):

    # アップロード先Dirを日付から決定する
    subdir_name = os.path.basename(os.path.dirname(local_file_dir)) + '/'
    print(f"upload dir is {subdir_name}")

    # アップロード先に存在するファイルのリスト
    response = client_s3.list_objects(Bucket=bucket_name, Prefix=subdir_name)
    object_list = [content['Key'] for content in response['Contents']]
    object_list.pop(0)
    object_list = list(map(lambda file: file.replace(subdir_name, ''), object_list))
    object_list = list(map(lambda file: file.replace('.zip', TARGET_FILE_EXT), object_list))
    print(f"object_list is {object_list}")

    # local dirに存在するファイルのリスト
    local_file_list = [ f for f in os.listdir(local_file_dir) if os.path.isfile(os.path.join(local_file_dir, f))]
    local_file_list = [ f for f in local_file_list if f.endswith(TARGET_FILE_EXT)]
    # local_file_list =  list(map(lambda file: subdir_name + file, local_file_list))
    print(f"local_file_list is {local_file_list}")
    # local dirに存在するファイルの中から、アップロード先に存在するファイルを除外する
    return [ f for f in local_file_list if not f in object_list]

def upload_files(transfer_s3, bucket_name, local_file_dir, not_upload_files_in_local_dir):

    subdir_name = os.path.basename(os.path.dirname(local_file_dir)) + '/'

    # アップロード対象のファイルがなければ、処理を終了する
    if len(not_upload_files_in_local_dir) == 0:
        print("no files to upload.")
        return

    # アップロード対象のファイルをアップロードする
    for file_name in not_upload_files_in_local_dir:
        zip_path = zip_file(local_file_dir, file_name)
        print(f"file_name is {file_name}")
        print(f"uploading {zip_path} to {bucket_name} ...")
        transfer_s3.upload_file(zip_path, bucket_name, subdir_name + file_name.replace(TARGET_FILE_EXT, '.zip'))
        print(f"finished uploading {file_name} to {bucket_name} ...")


def auto_upload_file(bucket_name, local_file_dir):

    # create client_s3 client
    load_dotenv()
    client_s3 = boto3.client('s3')

    config = TransferConfig(
        multipart_threshold = MULTIPART_THRESHOLD,
        max_concurrency = MAX_CONCURRENCY,
        multipart_chunksize = MULTIPART_CHUNKSIZE,
        max_bandwidth = MAX_BANDWIDTH,
        )

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/customizations/s3.html#boto3.s3.transfer.S3Transfer
    transfer_s3 = S3Transfer(client_s3, config)

    # local dirが存在するか確認する
    if ( not check_local_dir_exist(local_file_dir)):
        print('\033[31m'+'local dir is not exist')
        return False
    print("local dir is exist.")

    # s3のbucketが存在するか確認する
    if (not check_bucket_exist(client_s3, bucket_name)):
        print('\033[31m'+'bucket is not exist')
        return False
    print("bucket is exist.")

    # s3のアップロード先Dirが存在するか確認し、存在しない場合には作成する
    if create_updload_dir_exist(client_s3, bucket_name):
        print("checking upload dir exist ....")
    print("finished cheking upload dir.")

    while True:
        # アップロード対象のファイルを取得する
        not_upload_files_in_local_dir = get_not_upload_files_in_local_dir(client_s3, bucket_name, local_file_dir)

        # アップロード対象のファイルをアップロードする
        upload_files(transfer_s3, bucket_name, local_file_dir, not_upload_files_in_local_dir)

        time.sleep(1)


def main():
    bucket_name = sys.argv[1]
    local_file_dir = sys.argv[2]

    auto_upload_file(bucket_name, local_file_dir)


if __name__ == '__main__':
    main()