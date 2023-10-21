# upload_s3
upload video files by boto3 to s3 buckets

# how to use
- create .env file and write info for access s3.
``` .env
AWS_ACCESS_KEY_ID='**********'
AWS_SECRET_ACCESS_KEY='**********'
AWS_DEFAULT_REGION='ap-northeast-1'

```

- set video dir path and video file name, and execution
```
python upload_video.py $VIDEO_DIR_PATH $VIDEO_FILE_NAME
```

## ref
- [Pythonを使ってAmazon S3にファイルをアップロードする](https://qiita.com/honda28/items/bf71c2b39e8ab109fda3)
- [S3へのファイル登録のパフォーマンス比較](https://www.magata.net/memo/index.php?S3%A4%D8%A4%CE%A5%D5%A5%A1%A5%A4%A5%EB%C5%D0%CF%BF%A4%CE%A5%D1%A5%D5%A5%A9%A1%BC%A5%DE%A5%F3%A5%B9%C8%E6%B3%D3)
- [S3 Transfer AccelerationをAWS CLIを使って試してみた](https://dev.classmethod.jp/articles/s3-transfer-acceleration-with-aws-cli/)
- [boto3でS3からファイルをダウンロード・アップロードするのを高速化する](https://anton0825.hatenablog.com/entry/2022/04/19/144621)
- [aws Uploading files](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html#uploading-files)
- [How I will get response of success in aws file upload on s3 bucket using boto3?](https://stackoverflow.com/questions/56470774/how-i-will-get-response-of-success-in-aws-file-upload-on-s3-bucket-using-boto3)