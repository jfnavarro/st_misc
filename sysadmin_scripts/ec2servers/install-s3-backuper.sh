#!/bin/sh

# This script installs a new EC2 instance for backuping s3 volumes.
#
# Invoke the script like this
#
# sh install-s3-backuper.sh
#
# The instance does not have any elastic IP address, so we don't give it any
# DNS hostname.
# The instance 
set -ex

. ./common-functions.sh

ssh_security_group=sg-836fc1e6

if [ $# -ne 0 ]; then
  echo "Usage: `basename $0`"
  exit 1
fi

server=s3-backuper

adjust_variables_for_region "eu-west-1"
instancetype=t2.medium
root_volume_size=20
ami="$ubuntu_14_04_ami"

tmpdir=`mktemp -d`

install_command

run_command "echo $server > /etc/hostname"
run_command apt-get update

current_git_commit=`git rev-parse HEAD`
run_command "echo $current_git_commit > /root/installed_from_st_code_git_commit.txt"

mkdir $tmpdir/repos

reboot_instance

# TODO: Check that the size is enough for having all s3 volumes.
create_extra_volume_and_mount_it xvdf 30 /data "$server /data" gp2

tmpdir=`mktemp -d `

echo "32 2 * * * sh /root/s3backup/backup-s3-and-create-ebs-snapshot.sh >> /var/log/backup-s3.txt 2>&1" > $tmpdir/crontab_row
copy_command $tmpdir/crontab_row /tmp/crontab_row
run_command "crontab /tmp/crontab_row"

run_command "mkdir /root/s3backup"

copy_command ../backup_scripts/backup-s3.sh /root/s3backup/backup-s3.sh
copy_command copy-out-files/s3-backuper/backup-s3-and-create-ebs-snapshot.sh /root/s3backup/backup-s3-and-create-ebs-snapshot.sh

run_command "echo $extravolume > /root/s3backup/volume_id"

aws ec2 create-tags --resources $instance_id --tags "Key=Name,Value=new $server (rename this)" --region eu-west-1 --region $region
