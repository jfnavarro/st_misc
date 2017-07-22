#!/bin/sh

# This script installs either a new EC2 instance that will be able to run the ST pipeline
#
# Invoke the script like this
#
# sh install-pipeline.sh gerrit_username
# 

set -ex

. ./common-functions.sh

if [ $# -ne 1 ]; then
  echo "Usage: `basename $0` gerrit_username"
  exit 1
fi

# The username to use for cloning the Git repositories from the Gerrit server.
gerrit_username=$1

server=ec2stpipeline

adjust_variables_for_region "eu-west-1"
#instancetype=t2.medium
instancetype=m4.xlarge
root_volume_size=8
pipeline_git_commit=054c1bce2ae6749558e90cef9707446fe9a278c1
ami="$ubuntu_14_04_ami"

tmpdir=`mktemp -d`

install_command

# First write the hostname into the file /etc/hostname
# This gives us nicer looking prompt, after the next reboot.

run_command "echo $server > /etc/hostname"
run_command apt-get update

repodir=`mktemp -d`
git -C $repodir clone ssh://${gerrit_username}@gerrit.spatialtranscriptomics.com:29418/st_pipeline
git -C $repodir checkout $pipeline_git_commit
rsync -a -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" "$repodir/st_pipeline/" root@${ip_address}:/home/ubuntu/st_pipeline
run_command chown -R ubuntu /home/ubuntu/st_pipeline
run_command apt-get install -y git build-essential libreadline-dev zlib1g-dev libbz2-dev  libsqlite3-dev  libssl-dev unzip libblas-dev liblapack-dev libatlas-base-dev gfortran

copy_command copy-out-files/ec2stpipeline/instpipeline.sh /home/ubuntu/
run_command chown ubuntu /home/ubuntu/instpipeline.sh

run_command su - -c '"bash /home/ubuntu/instpipeline.sh /home/ubuntu/st_pipeline"' ubuntu


# git commit pyenv cb65df8becb4ddf99acf711ecad399f4e55182c7




# copy_command $tmpdir/server.xml /etc/tomcat7/server.xml
# copy_command copy-out-files/admin/tomcat7 /etc/default/tomcat7
# run_command rm /etc/nginx/sites-enabled/default
# copy_command $tmpdir/admin-spatialtranscriptomics /etc/nginx/sites-available
# run_command ln -s /etc/nginx/sites-available/admin-spatialtranscriptomics /etc/nginx/sites-enabled/admin-spatialtranscriptomics 
# run_command mkdir /etc/nginx/ssl

# copy_with_mode_command copy-out-files/admin/nginx.conf /etc/nginx/nginx.conf 644

# copy_with_mode_command copy-out-files/admin/tomcat-users.xml /var/lib/tomcat7/conf/tomcat-users.xml 640
# run_command chown root.tomcat7 /var/lib/tomcat7/conf/tomcat-users.xml

# ssltmp=`mktemp -d`
# chmod 700 $ssltmp
# unzip -d $ssltmp copy-out-files/Comodo_EssentialSSL_Wildcard_certificate.bought_from_dnsimple.com/STAR_spatialtranscriptomics_com.zip
# cat $ssltmp/STAR_spatialtranscriptomics_com.crt $ssltmp/COMODORSADomainValidationSecureServerCA.crt $ssltmp/COMODORSAAddTrustCA.crt $ssltmp/AddTrustExternalCARoot.crt  > $ssltmp/concatenated_from_zip.crt

# copy_with_mode_command copy-out-files/Comodo_EssentialSSL_Wildcard_certificate.bought_from_dnsimple.com/STAR_spatialtranscriptomics_com.key /etc/nginx/ssl/STAR_spatialtranscriptomics_com.key 600
# copy_with_mode_command $ssltmp/concatenated_from_zip.crt /etc/nginx/ssl/concatenated_from_zip.crt 600


# current_git_commit=`git rev-parse HEAD`
# run_command "echo $current_git_commit > /root/installed_from_st_code_git_commit.txt"

# mkdir $tmpdir/repos

# deploy() {
# cd $tmpdir/repos
# git clone ssh://${gerrit_username}@gerrit.spatialtranscriptomics.com:29418/st_$1
# cd st_$1

# # We might want to specify the revision explicitly in the future.
# # git checkout $2 -b tmpbranch
# mvn -B  -f pom.xml -DbuildDir=. -P $maven_profile package
# copy_command $1.war /var/lib/tomcat7/webapps/
# }

# deploy api
# deploy admin

# run_command service tomcat7 restart

reboot_instance

aws ec2 modify-instance-attribute --instance-id $instance_id --groups $ssh_security_group $extra_security_group --region $region
aws ec2 create-tags --resources  $instance_id --tags "Key=Name,Value=new $server (rename this)" --region $region

