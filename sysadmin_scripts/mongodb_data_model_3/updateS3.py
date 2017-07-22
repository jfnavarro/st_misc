#! /usr/bin/env python
"""
Script to convert ST API Amazon S3 model 2 to model 3

S3 Configuration in 

~/.aws/credentials

@author: Jose Fernandez
"""

import boto3
import botocore
import os
import sys
import subprocess
import glob

BUCKET_NAME = "featuresdev"

def run_command(command, out=subprocess.PIPE):
    try:
        print "running command: {}".format(" ".join(x for x in command).rstrip())
        proc = subprocess.Popen(command,
                                stdout=out, stderr=subprocess.PIPE,
                                close_fds=True, shell=False)
        (stdout, errmsg) = proc.communicate()
    except Exception as e:
        print str(e)
        raise e
    
s3 = boto3.resource('s3')
# Print out all bucket names
for bucket in s3.buckets.all():
    print(bucket.name)
    
# Download the feature's bucket files
file_ids = list()
for object in s3.Bucket(BUCKET_NAME).objects.all():
    print "Downloading " + object.key
    try:
        s3.Bucket(BUCKET_NAME).download_file(object.key, object.key)
        file_ids.append(object.key)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print "The file does not exist or it is no valid"
        else:
            print "Unknown error downloading file"

for file in file_ids:
    try:
        run_command(["gunzip", "-f", file])
    except Exception as e:
        print "Error gunziping file " + str(file)
        continue
    
for file in file_ids:
    if file.find(".gz") != -1:
        print "Converting JSON to TSV, skipping file " + str(file)
        continue
    try:
        clean_name = os.path.splitext(os.path.basename(file))[0]
        os.rename(clean_name, clean_name + ".json")
        new_file_name = clean_name + "_stdata.tsv"
        run_command(["json_to_matrix.py", "--json-file", clean_name + ".json", "--outfile", new_file_name])
    except Exception as e:
        print "Error converting JSON to TSV " + str(file)
        continue
 
for file in glob.glob("*.tsv"):   
    try:
        run_command(["gzip", "-f", file])
    except Exception as e:
        print "Error gzipping file " + str(file)
        continue
  
for file in glob.glob("*.gz"):            
    data = open(file, 'rb')
    print "Uploading to S3 " + file
    s3.Bucket(BUCKET_NAME).put_object(Key=file, Body=data)
    data.close()
