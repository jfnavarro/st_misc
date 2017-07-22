#!/bin/sh

# This script installs either a new EC2 instance for db.spatialtranscriptomics.com or db-dev.spatialtranscriptomics.com
#
# Invoke the script like this
#
# sh install-db.sh db gerrit_username
#
# or
#
# sh install-db.sh db-dev gerrit_username
#
#
# The script ends by echoing an associate-address command.
# If you copy and paste that command into the terminal, the newly created EC2 instance will be
# given the official IP address. But before this you should make sure the mongodb data has been
# migrated to the new instance. Right now (2015-02-17) this script doesn't migrate the mongodb data.

set -ex

. ./common-functions.sh

ssh_security_group=sg-836fc1e6

if [ $# -ne 2 -o ! \( "$1" = "db" -o "$1" = "db-dev" \) ]; then
  echo "Usage: `basename $0` [ db | db-dev ] gerrit_username"
  exit 1
fi

# The username to use for cloning the Git repositories from the Gerrit server.
gerrit_username=$2

server="$1"

if [ "$server" = "db" ]; then
   adjust_variables_for_region "eu-west-1"
   instancetype=t2.large
   mongodb_security_group=sg-c2d06fa7 # mongodb-prod
   allocation_id=eipalloc-879478e2    # representing the public ip address for db.spatialtranscriptomics.com
   root_volume_size=40
fi

if [ "$server" = "db-dev" ]; then
   adjust_variables_for_region "eu-west-1"
   instancetype=t2.medium
   mongodb_security_group=sg-c2da63a7 # mongodb-dev
   allocation_id=eipalloc-5519fa30    # representing the public ip address for db-dev.spatialtranscriptomics.com
   root_volume_size=20
fi

ami="$ubuntu_14_04_ami"

install_command

# First write the hostname into the file /etc/hostname
# This gives us nicer looking prompt, after the next reboot.

run_command "echo $server > /etc/hostname"
run_command apt-get update

# Check that the size is big enough holding the mongodb data

create_extra_volume_and_mount_it xvdf 250 /data "$server /data" gp2

tmpdir=`mktemp -d`

sed "s/@REPLACE_WITH_VOLUME_ID@/$extravolume/g" copy-out-files/db/run-ec2-consistent-snapshot-master.sh > $tmpdir/run-ec2-consistent-snapshot-master.sh

run_command apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10

copy_command copy-out-files/db/mongodb.list /etc/apt/sources.list.d/mongodb.list
run_command apt-get update
run_command apt-get install -y mongodb-org

run_command mkdir -p /data/db/logs/
run_command chown -R mongodb:mongodb /data/db/

copy_command copy-out-files/db/mongodb.conf /etc/mongod.conf


# These DEB packages are needed for ec2-consistent-snapshot

list="awscli
cpanminus
docutils-common
libalgorithm-c3-perl
libaliased-perl
libany-moose-perl
libauthen-sasl-perl
libb-hooks-endofscope-perl
libboolean-perl
libclass-c3-perl
libclass-c3-xs-perl
libclass-load-perl
libclass-load-xs-perl
libclass-singleton-perl
libclass-tiny-perl
libcpan-distnameinfo-perl
libcpan-meta-check-perl
libcpan-meta-perl
libcpan-meta-requirements-perl
libdata-optlist-perl
libdatetime-locale-perl
libdatetime-perl
libdatetime-timezone-perl
libdevel-caller-perl
libdevel-globaldestruction-perl
libdevel-lexalias-perl
libdevel-partialdump-perl
libencode-locale-perl
libeval-closure-perl
libfile-listing-perl
libfile-pushd-perl
libfile-slurp-perl
libfont-afm-perl
libhtml-form-perl
libhtml-format-perl
libhtml-parser-perl
libhtml-tagset-perl
libhtml-tree-perl
libhttp-cookies-perl
libhttp-daemon-perl
libhttp-date-perl
libhttp-message-perl
libhttp-negotiate-perl
libio-html-perl
libio-socket-inet6-perl
libio-socket-ssl-perl
libjbig0
libjpeg-turbo8
libjpeg8
liblcms2-2
liblist-moreutils-perl
liblocal-lib-perl
liblwp-mediatypes-perl
liblwp-protocol-https-perl
libmailtools-perl
libmodule-cpanfile-perl
libmodule-implementation-perl
libmodule-metadata-perl
libmodule-runtime-perl
libmongodb-perl
libmoose-perl
libmro-compat-perl
libnamespace-clean-perl
libnet-amazon-ec2-perl
libnet-http-perl
libnet-smtp-ssl-perl
libnet-ssleay-perl
libpackage-deprecationmanager-perl
libpackage-stash-perl
libpackage-stash-xs-perl
libpadwalker-perl
libpaper-utils
libpaper1
libparams-classify-perl
libparams-util-perl
libparams-validate-perl
libparse-cpan-meta-perl
libsocket6-perl
libstring-shellquote-perl
libsub-exporter-perl
libsub-exporter-progressive-perl
libsub-identify-perl
libsub-install-perl
libtask-weaken-perl
libtie-ixhash-perl
libtiff5
libtry-tiny-perl
liburi-perl
libvariable-magic-perl
libwebp5
libwebpmux1
libwww-perl
libwww-robotrules-perl
libxml-namespacesupport-perl
libxml-parser-perl
libxml-sax-base-perl
libxml-sax-expat-perl
libxml-sax-perl
libxml-simple-perl
make
python3-bcdoc
python3-botocore
python3-chardet
python3-colorama
python3-dateutil
python3-docutils
python3-jmespath
python3-pil
python3-pkg-resources
python3-ply
python3-pygments
python3-requests
python3-roman
python3-rsa
python3-six
python3-urllib3
unzip"

run_command apt-get install -y $list

# MongoDB::Admin is needed for ec2-consistent-snapshot
# but there is no DEB package available so we need to fetch it with cpanm.
run_command cpanm --sudo MongoDB::Admin

if [ "$server" = "db" ]; then
  # Here we activate the script ec2-consistent-snapshot. It will take a Amazona EBS volume snapshot of the /data partition of db.spatialtranscriptomics.com.
  # We skip all of this for db-dev.spatialtranscriptomics.com.

  run_command mkdir -p /root/backup/ec2-consistent-snapshot-master
  run_command mkdir -p /root/backup/logs

  # From
  # https://github.com/alestic/ec2-consistent-snapshot/blob/master/ec2-consistent-snapshot

  copy_with_mode_command  copy-out-files/db/ec2-consistent-snapshot-master/ec2-consistent-snapshot /root/backup/ec2-consistent-snapshot-master 755
  copy_with_mode_command  $tmpdir/run-ec2-consistent-snapshot-master.sh /root/backup/run-ec2-consistent-snapshot-master.sh 755

  current_git_commit=`git rev-parse HEAD`
  run_command "echo $current_git_commit > /root/installed_from_st_code_git_commit.txt"

  copy_command copy-out-files/db/crontab /root/crontab
  run_command crontab /root/crontab
fi

reboot_instance

aws ec2 modify-instance-attribute --instance-id $instance_id --groups $ssh_security_group $mongodb_security_group --region $region
aws ec2 create-tags --resources  $instance_id --tags "Key=Name,Value=new $server (rename this)" --region $region

# Later, you probably want to run this command to move the official ip address to the new instance.
# But make sure the mongodb data has been migrated first.

echo aws ec2 associate-address --instance-id $instance_id --allow-reassociation  --allocation-id $allocation_id  --region $region
