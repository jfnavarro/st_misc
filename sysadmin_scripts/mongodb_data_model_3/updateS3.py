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
import tempfile
import shutil

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

print "Starting conversion of data in S3 from model 2 to model 3"    

tmp_dir = tempfile.mkdtemp()
os.chdir(tmp_dir)
print "Using temp directory " + tmp_dir

# Create S3 object
s3 = boto3.resource('s3')
# Print out all bucket names
print "S3 buckets available"
for bucket in s3.buckets.all():
    print(bucket.name)
    
print "Using S3 bucket " + BUCKET_NAME

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
        print "Error gunziping file " + str(file) + " "  + str(e)
        continue
    
for file in glob.glob("*"):
    if file.find(".gz") != -1:
        print "Converting JSON to TSV, skipping file " + str(file)
        continue
    try:
        # We need to add the JSON extension so the conversion script works
        json_file_name = file + ".json"
        os.rename(file, json_file_name)
        new_file_name = file + "_stdata.tsv"
        run_command(["json_to_matrix.py", "--json-file", json_file_name, "--outfile", new_file_name])
    except Exception as e:
        print "Error converting JSON to TSV " + str(file) + " "  + str(e)
        continue
 
for file in glob.glob("*.tsv"):   
    try:
        run_command(["gzip", "-f", file])
    except Exception as e:
        print "Error gzipping file " + str(file)
        continue
  
for file in glob.glob("*.gz"):
    key = file.split("_stdata")[0] + "/" + file
    print "Uploading to S3 " + key            
    data = open(file, 'rb')
    try:
        s3.Bucket(BUCKET_NAME).put_object(Key=key, Body=data)
        data.close()
    except Exception as e:
        print "Error uploading file to S3 " + str(e)
        data.close()

for file in file_ids:
    print "Removing file from S3 " + file
    try:
        s3.Bucket(BUCKET_NAME).delete_key(Key=file)
    except Exception as e:
        print "Error deleting file in S3 " + str(e)
            
print "Done! removing temp folder"
shutil.rmtree(tmp_dir)