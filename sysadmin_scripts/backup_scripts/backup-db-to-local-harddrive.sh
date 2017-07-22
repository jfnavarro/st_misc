#!/bin/sh

# Backup script that crontab runs on zebra.scilifelab.se (Erik's Ubuntu desktop computer)
# The script takes a backup of mongodb running on db.spatialtranscriptomics.com
# and stores it on the local usb hard drive

set -e
datetime=`date "+%F_%X"`
echo starting backup-db-to-local-harddrive.sh $datetime

ssh -i ~/aws/spatial.pem root@db.spatialtranscriptomics.com "rm -rf /data/tmpmongodump && \
    rm -f /data/tmpmongodump.tar.gz && hostname && \
    LANG=C LC_ALL=C mongodump --quiet -o /data/tmpmongodump --username admin --password 5QTQaRefC2vL && \
    tar cfz /data/tmpmongodump.tar.gz /data/tmpmongodump"
scp -i ~/aws/spatial.pem root@db.spatialtranscriptomics.com:/data/tmpmongodump.tar.gz \
    "/mnt/usb_backup/backup/db/mongodump_db.${datetime}.tar.gz"
ssh -i ~/aws/spatial.pem root@db.spatialtranscriptomics.com \
    "rm -rf /data/tmpmongodump && rm -f /data/tmpmongodump.tar.gz"
datetime=`date "+%F_%X"`
echo ending backup-db-to-local-harddrive.sh $datetime
