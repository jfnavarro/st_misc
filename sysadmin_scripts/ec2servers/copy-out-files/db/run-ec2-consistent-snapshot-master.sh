#!/bin/sh

export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH

AWS_DEFAULT_REGION=eu-west-1 /root/backup/ec2-consistent-snapshot-master/ec2-consistent-snapshot   --region  eu-west-1  --use-iam-role  --freeze-filesystem /data  --mongo-username admin  --mongo-password 5QTQaRefC2vL --mongo @REPLACE_WITH_VOLUME_ID@ --description "db /data $(date +'%Y-%m-%d %H:%M:%S')"
