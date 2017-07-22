#!/bin/sh

dir=/data/s3backup/modulo_day_number
mkdir -p $dir
sh /root/s3backup/backup-s3.sh 1 $dir

volume_id=`cat /root/s3backup/volume_id`
/sbin/fsfreeze --freeze /data
aws ec2 create-snapshot --volume-id $volume_id --description "s3-backuper /data snapshot" --region eu-west-1
/sbin/fsfreeze --unfreeze /data
