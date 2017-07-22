#!/bin/sh

# Backup script that crontab runs on zebra.scilifelab.se (Erik's Ubuntu desktop computer)
# The script takes a backup of most of the S3 buckets and stores them on the local usb hard drive.

# If this script is started like this:
# sh backup-s3.sh 3
#
# 3 directories are used for the last 3 days on a rolling scheme.
# /mnt/usb_backup/backup/s3/modulo_day_number/0
# /mnt/usb_backup/backup/s3/modulo_day_number/1
# /mnt/usb_backup/backup/s3/modulo_day_number/2

set -ev

if [ $# -ne 2 ]; then
  echo "Usage: `basename $0` number_of_backups_to_keep"
  exit 1
fi
number_of_backups_to_keep=$1
s3_backup_dir="$2"

buckets=`aws s3 ls | awk '{ print $3; }'`
skip_list="stpipelinedev stpipelineprod sts3logs"


seconds_since_1970=`date +%s`
days_since_1970=`expr $seconds_since_1970 / 86400`
modulo_day=`expr $days_since_1970 % $number_of_backups_to_keep || /bin/true`

for i in $buckets; do 
  skip_found="false"
  for j in $skip_list; do 
    if [ $i = $j ]; then
      skip_found="true"
    fi
  done
  if [ $skip_found = "false" ]; then
    dir="$s3_backup_dir/$modulo_day/$i"
    mkdir -p $dir
#    aws s3 sync --quiet --delete "s3://$i/" "$dir"
    aws s3 sync --delete "s3://$i/" "$dir" --region eu-west-1
  fi
done
