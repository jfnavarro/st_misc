#!/bin/sh

# This script installs either a new EC2 instance for admin.spatialtranscriptomics.com or admin-dev.spatialtranscriptomics.com
#
# Invoke the script like this
#
# sh install-admin.sh admin gerrit_username
# 
# or 
#
# sh install-admin.sh admin-dev gerrit_username
#
# 
# The script ends by echoing an associate-address command. 
# If you copy and paste that command into the terminal, the newly created EC2 instance will be given the official IP address.

set -ex

. ./common-functions.sh

if [ $# -ne 2 -o ! \( "$1" = "admin" -o "$1" = "admin-dev" \) ]; then
  echo "Usage: `basename $0` [ admin | admin-dev ] gerrit_username"
  exit 1
fi

# The username to use for cloning the Git repositories from the Gerrit server.
gerrit_username=$2

server="$1"

if [ "$server" = "admin" ]; then
   adjust_variables_for_region "eu-west-1"
   instancetype=t2.large
   extra_security_group="$https_http_anywhere_security_group"
   allocation_id=eipalloc-01967a64    # representing the public ip address for admin.spatialtranscriptomics.com
   maven_profile=prod
   root_volume_size=50
fi

if [ "$server" = "admin-dev" ]; then
   adjust_variables_for_region "eu-west-1"
   instancetype=t2.medium
   extra_security_group="$https_http_scilife_security_group"
   allocation_id=eipalloc-2119fa44    # representing the public ip address for admin-dev.spatialtranscriptomics.com
   maven_profile=dev
   root_volume_size=20
fi

ami="$ubuntu_14_04_ami"

tmpdir=`mktemp -d`

for i in server.xml admin-spatialtranscriptomics; do
  sed "s/@SERVER@/$server/g" copy-out-files/admin/$i > $tmpdir/$i
done

install_command

# First write the hostname into the file /etc/hostname
# This gives us nicer looking prompt, after the next reboot.

run_command "echo $server > /etc/hostname"
run_command apt-get update

run_command apt-get install -y openjdk-7-jre openjdk-7-jdk tomcat7 tomcat7-admin nginx
copy_command $tmpdir/server.xml /etc/tomcat7/server.xml
copy_command copy-out-files/admin/tomcat7 /etc/default/tomcat7
run_command rm /etc/nginx/sites-enabled/default
copy_command $tmpdir/admin-spatialtranscriptomics /etc/nginx/sites-available
run_command ln -s /etc/nginx/sites-available/admin-spatialtranscriptomics /etc/nginx/sites-enabled/admin-spatialtranscriptomics 
run_command mkdir /etc/nginx/ssl

copy_with_mode_command copy-out-files/admin/nginx.conf /etc/nginx/nginx.conf 644

copy_with_mode_command copy-out-files/admin/tomcat-users.xml /var/lib/tomcat7/conf/tomcat-users.xml 640
run_command chown root.tomcat7 /var/lib/tomcat7/conf/tomcat-users.xml

ssltmp=`mktemp -d`
chmod 700 $ssltmp
unzip -d $ssltmp copy-out-files/Comodo_EssentialSSL_Wildcard_certificate.bought_from_dnsimple.com/STAR_spatialtranscriptomics_com.zip
cat $ssltmp/STAR_spatialtranscriptomics_com.crt $ssltmp/COMODORSADomainValidationSecureServerCA.crt $ssltmp/COMODORSAAddTrustCA.crt $ssltmp/AddTrustExternalCARoot.crt  > $ssltmp/concatenated_from_zip.crt

copy_with_mode_command copy-out-files/Comodo_EssentialSSL_Wildcard_certificate.bought_from_dnsimple.com/STAR_spatialtranscriptomics_com.key /etc/nginx/ssl/STAR_spatialtranscriptomics_com.key 600
copy_with_mode_command $ssltmp/concatenated_from_zip.crt /etc/nginx/ssl/concatenated_from_zip.crt 600


current_git_commit=`git rev-parse HEAD`
run_command "echo $current_git_commit > /root/installed_from_st_code_git_commit.txt"

mkdir $tmpdir/repos

deploy() {
cd $tmpdir/repos
git clone ssh://${gerrit_username}@gerrit.spatialtranscriptomics.com:29418/st_$1
cd st_$1

# We might want to specify the revision explicitly in the future.
# git checkout $2 -b tmpbranch
mvn -B  -f pom.xml -DbuildDir=. -P $maven_profile package
copy_command $1.war /var/lib/tomcat7/webapps/
}

deploy api
deploy admin

run_command service tomcat7 restart

reboot_instance

aws ec2 modify-instance-attribute --instance-id $instance_id --groups $ssh_security_group $extra_security_group --region $region
aws ec2 create-tags --resources  $instance_id --tags "Key=Name,Value=new $server (rename this)" --region $region

# Later, you probably want to run this command to move the official ip address to the new instance
echo aws ec2 associate-address --instance-id $instance_id --allow-reassociation  --allocation-id $allocation_id --region $region
