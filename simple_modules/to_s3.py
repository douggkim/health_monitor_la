import boto3
import json
import os 

client_secrets_path = os.getcwd()+"/amazon_credentials.json"
with open(client_secrets_path, 'r') as file: 
    secret_keys = json.load(file)

session = boto3.Session(
    aws_access_key_id=secret_keys['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=secret_keys['AWS_SECRET_ACCESS_KEY']
)
s3 = session.resource('s3')
# Filename - File to upload
# Bucket - Bucket to upload to (the top level directory under AWS S3)
# Key - S3 object name (can contain subdirectories). If not specified then file_name is used
s3.meta.client.upload_file(Filename=os.getcwd()+'/heart_rate_2022-12-10 22:58:09.789063.csv', Bucket=secret_keys['BUCKET_NAME'], Key='heart_rate_2022-12-10 22:58:09.789063.csv')
# s3.meta.client.upload_file(Filename=os.getcwd()+'../heart_rate_2022-12-10 22:58:09.789063.csv', Bucket=secret_keys['BUCKET_NAME'])