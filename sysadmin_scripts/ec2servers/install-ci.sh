#!/bin/sh

# This script installs a new EC2 instance for st-ci-master.spatialtranscriptomics.com
#
# It is mainly used for documenation purposes
#
# Invoke the script like this
#
# sh install-ci.sh
# 
# The script ends by echoing an associate-address command. 
# If you copy and paste that command into the terminal, the newly created EC2 instance will be given the official IP address.


# Please edit these configuration variables

#instancetype=m3.large
instancetype=t2.micro
#https_security_group=sg-cac27daf   # https-http-anywhere

ci_security_group=sg-7d6cc218
allocation_id=eni-431abf27    # representing the public ip address for gerrit.spatialtranscriptomics.com
root_volume_size=40
server=ci-master

SMTP_USER=AKIAJ4A6L7SQI7B4ZJXQ
SMTP_PASSWORD=Akx7PqYg9wdvm75Ex13pMaVEcEWNMjzBaXUJa+nFOs8W
SMTP_SERVER=email-smtp.eu-west-1.amazonaws.com
EMAIL_ADDRESS=erik.sjolund@scilifelab.se
GERRIT_SERVER_HOSTNAME=gerrit.spatialtranscriptomics.com
JIRA_SERVER_HOSTNAME=jira.spatialtranscriptomics.com

#gerrit_project=st_client
gerrit_project=bowtie
old_git_URL=https://github.com/BenLangmead/bowtie.git

ssl_certificate_key=copy-out-files/Comodo_EssentialSSL_Wildcard_certificate.bought_from_dnsimple.com/STAR_spatialtranscriptomics_com.key

ssltmp=`mktemp -d`
chmod 700 $ssltmp
unzip -d $ssltmp copy-out-files/Comodo_EssentialSSL_Wildcard_certificate.bought_from_dnsimple.com/STAR_spatialtranscriptomics_com.zip
cat $ssltmp/STAR_spatialtranscriptomics_com.crt $ssltmp/COMODORSADomainValidationSecureServerCA.crt $ssltmp/COMODORSAAddTrustCA.crt $ssltmp/AddTrustExternalCARoot.crt  > $ssltmp/concatenated_from_zip.crt
ssl_certificate=$ssltmp/concatenated_from_zip.crt

#install_jira="true"
install_jira="false"
# DO NOT EDIT BELOW THIS LINE

set -ex

if [ $# -ne 0  ]; then
  echo "error: This script expects no arguments."
  exit 1
fi
tmpdir=`mktemp -d`
chmod 700 $tmpdir

. ./common-functions.sh

adjust_variables_for_region "eu-west-1"

ami="$ubuntu_14_04_ami"

cp copy-out-files/ci-master/gerrit.config $tmpdir
sed -i "s/@GERRIT_SERVER_HOSTNAME@/${GERRIT_SERVER_HOSTNAME}/g" $tmpdir/gerrit.config
sed -i "s/@JIRA_SERVER_HOSTNAME@/${JIRA_SERVER_HOSTNAME}/g" $tmpdir/gerrit.config
sed -i "s/@SMTP_SERVER@/${SMTP_SERVER}/g" $tmpdir/gerrit.config
sed -i "s/@SMTP_USER@/${SMTP_USER}/g" $tmpdir/gerrit.config
sed -i "s/@SMTP_PASSWORD@/${SMTP_PASSWORD}/g" $tmpdir/gerrit.config
sed -i "s/@EMAIL_ADDRESS@/${EMAIL_ADDRESS}/g" $tmpdir/gerrit.config

install_command

# First write the hostname into the file /etc/hostname
# This gives us nicer looking prompt, after the next reboot.

run_command "echo $server > /etc/hostname"
run_command apt-get update

# DNS gerrit.spatialtranscriptomics.com  54.72.250.160

run_command apt-get install -y default-jdk git nginx

#cd $tmpdir

gerrit_war_file=gerrit-2.10.war
wget -O  $tmpdir/$gerrit_war_file  http://gerrit-releases.storage.googleapis.com/$gerrit_war_file 

copy_command $tmpdir/$gerrit_war_file /tmp

run_command su - ubuntu -c \"java -jar /tmp/$gerrit_war_file init --batch -d /home/ubuntu/gerrit  --install-plugin=download-commands\"

copy_with_mode_command  $tmpdir/gerrit.config /home/ubuntu/gerrit/etc/gerrit.config 644
run_command su - ubuntu -c \"/home/ubuntu/gerrit/bin/gerrit.sh restart\"

# Gerrit mailing list question (2015-03-11):
# "is it possible to create the gerrit admin user on the command line instead of in the web interface?"
# https://groups.google.com/d/topic/repo-discuss/EGcQIYMgyTo/discussion
#
# It seems it is not possible right now (2015-03-11).
#
# cat copy-out-files/ci-master/gerrit-admin.id_rsa.pub | run_command su - ubuntu -c \"java -jar /tmp/$gerrit_war_file create-account --group Administrators --ssh-key - -d /home/ubuntu/gerrit gerrit-admin\"

run_command su - ubuntu -c \"java -jar /tmp/$gerrit_war_file create-project --name $gerrit_project\"

aws ec2 modify-instance-attribute --instance-id $instance_id --groups $ssh_security_group $ci_security_group

gitdir=`mktemp -d`
cd $gitdir

git clone $old_git_URL $gerrit_project
cd $gerrit_project

git remote add gerritremote ssh://esjolund@${ip_address}:29418/$gerrit_project
git push gerritremote refs/remotes/origin/*:refs/heads/*
cd
git remote add gerritremote ssh://$gerritadmin@${GERRIT_SERVER_HOSTNAME}:29418/$gerritproject
git push gerritremote refs/*:refs/*

sed "s/@GERRIT_SERVER_HOSTNAME@/${GERRIT_SERVER_HOSTNAME}/g" copy-out-files/ci-master/nginx/gerrit > $tmpdir/gerrit
copy_command $tmpdir/gerrit /etc/nginx/sites-available
run_command ln -s /etc/nginx/sites-available/gerrit /etc/nginx/sites-enabled/gerrit


sed "s/@JENKINS_SERVER_HOSTNAME@/${JENKINS_SERVER_HOSTNAME}/g" copy-out-files/ci-master/nginx/jenkins > $tmpdir/jenkins
copy_command $tmpdir/jenkins /etc/nginx/sites-available
run_command ln -s /etc/nginx/sites-available/jenkins /etc/nginx/sites-enabled/jenkins

if [ $install_jira = "true" ]; then
  sed "s/@JIRA_SERVER_HOSTNAME@/${JIRA_SERVER_HOSTNAME}/g" copy-out-files/ci-master/nginx/jira > $tmpdir/jira
  copy_command $tmpdir/jira /etc/nginx/sites-available
  run_command ln -s /etc/nginx/sites-available/jira /etc/nginx/sites-enabled/jira
fi

run_command mkdir /etc/nginx/ssl
copy_with_mode_command $ssl_certificate_key /etc/nginx/ssl/ssl_certificate_key 600
copy_with_mode_command $ssl_certificate  /etc/nginx/ssl/ssl_certificate 600

# Is there a better way to document the version of the install script that the server was installed from?
current_git_commit=`git rev-parse HEAD`
run_command "echo $current_git_commit > /root/installed_from_st_code_git_commit.txt"



wget -q -O - http://pkg.jenkins-ci.org/debian/jenkins-ci.org.key | run_command apt-key add -
run_command 'echo deb http://pkg.jenkins-ci.org/debian binary/ > /etc/apt/sources.list.d/jenkins.list'
run_command apt-get update 
run_command apt-get install jenkins -y
run_command apt-get install git-core
run_command adduser jenkins www-data
run_command perl -pi -e 's/HTTP_PORT=8080/HTTP_PORT=12080/g' /etc/default/jenkins
run_command service jenkins restart


reboot_instance

aws ec2 modify-instance-attribute --instance-id $instance_id --groups $ssh_security_group $https_security_group 
aws ec2 create-tags --resources  $instance_id --tags "Key=Name,Value=new $server (rename this)"

# Later, you probably want to run this command to move the official ip address to the new instance
echo aws ec2 associate-address --instance-id $instance_id --allow-reassociation  --allocation-id $allocation_id
