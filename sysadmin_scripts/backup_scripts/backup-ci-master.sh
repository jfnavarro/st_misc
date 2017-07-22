#!/bin/sh

# Backup script that crontab runs on zebra.scilifelab.se (Erik's Ubuntu desktop computer)
# The script takes a backup of the /data filesystem on ci-master.spatialtranscriptomics.com
# and stores it on the local usb hard drive

set -e
datetime=`date "+%F %X"`

echo starting backup-ci-master.sh $datetime

ssh -i /home/esjolund/aws/ci-master.pem root@st-ci-master.spatialtranscriptomics.com "sh /root/backup-routine/unmount-data.sh"

echo ssh unmount-data.sh return $?

ci_master_data_volume=vol-c61c1cd1
snapshot_id=`aws ec2 create-snapshot --volume-id $ci_master_data_volume --description "ci-master data volume: $datetime" --query SnapshotId`

if [ -z "$snapshot_id" ]; then
  echo "snapshot_id is empty"
  exit
fi

# Maybe we don't need to wait for state to be equal to "completed"?
# When "aws ec2 create-snapshot " returns it should be possible to use the volume again.

while state=$(aws ec2 describe-snapshots --snapshot-ids "$snapshot_id" --output text --query 'Snapshots[*].State'); test "$state" != "completed"; do
  sleep 15
done;

ssh -i /home/esjolund/aws/ci-master.pem root@st-ci-master.spatialtranscriptomics.com "sh /root/backup-routine/mount-data.sh"

rsync -a -e "ssh -i /home/esjolund/aws/ci-master.pem" --delete root@st-ci-master.spatialtranscriptomics.com:/data/ /mnt/usb_backup/backup/ci-master
ssh -i /home/esjolund/aws/ci-master.pem root@st-ci-master.spatialtranscriptomics.com "sh /root/backup-routine/start_jenkins_and_gerrit.sh"

datetime=`date "+%F %X"`
echo ending of backup-ci-master.sh $datetime
