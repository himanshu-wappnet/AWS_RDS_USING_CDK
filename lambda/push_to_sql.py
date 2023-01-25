#!/usr/bin/python
import json
import boto3
import pymysql 
import os


# read data from lamda configuration
rds_endpoint  = os.environ['db_endpoint']
username = os.environ['db_username']
password = os.environ['db_password'] 
db_name = os.environ['db_name']
s3_boto_cient = boto3.client('s3')

def main(event, context):
    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    s3_file_name = event["Records"][0]["s3"]["object"]["key"]
    
    # get data from s3 bucket
    resp = s3_boto_cient.get_object(Bucket=bucket_name, Key=s3_file_name)
    data = resp['Body'].read().decode('utf-8')
    data = data.split("\n")
    conn = None
    try:
        conn = pymysql.connect(host = rds_endpoint, user=username, passwd=password, db=db_name, connect_timeout=60)
    except pymysql.MySQLError as e:
        print("ERROR: Unexpected error: Could not connect to RDS instance.")

    # Creating the initial table for inserting the csv data
    try:
        cur = conn.cursor()
        cur.execute("create table s3dataimport ( id INT NOT NULL AUTO_INCREMENT, Name varchar(255) NOT NULL, PRIMARY KEY (id))") 
        conn.commit()
    except:
        pass
    
    # Iterate over S3 csv file content and insert into RDS database
    with conn.cursor() as cur:
        for column in data:
            try:
                column = column.replace("\n","").split(",")
                print ("Column data for reference > "+str(column))
                cur.execute('insert into s3dataimport (Name) values("'+str(column[1])+'")')
                conn.commit()
            except:
                continue
    return {
        'statusCode': 200,
        'body': json.dumps('Successfully executed the lamda function')
    }