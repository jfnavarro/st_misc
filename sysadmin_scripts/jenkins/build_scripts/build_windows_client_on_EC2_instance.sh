#!/bin/sh

set -e

instance_id=i-25ad16c1

# describe-instances is not yet supported for a specic IAM role:
# http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-supported-iam-actions-resources.html

retry_count=1
while state=$(aws ec2 describe-instances --instance-ids $instance_id --output text --region eu-west-1 --query 'Reservations[*].Instances[*].State.Name'); test "$state" = "pending" -o  "$state" = "stopping" -o "$state" = "shutting-down"; do
  sleep 1; echo -n '.'
  if [ $retry_count -gt 10 ]; then
    echo maximum number of aws ec2 describe-instances retries reached 1>&2
    exit 1
  fi
  retry_count=`expr $retry_count + 1`
done; echo " $state"



state=`aws ec2 describe-instances --instance-ids $instance_id --output text --region eu-west-1 --query 'Reservations[*].Instances[*].State.Name'`


#state=stopped
#ip_address=54.72.89.162

if [ "$state" = "stopped" ]; then
  aws ec2 start-instances --instance-ids $instance_id --region eu-west-1
fi

retry_count=1
while state=$(aws ec2 describe-instances --instance-ids $instance_id --output text --region eu-west-1 --query 'Reservations[*].Instances[*].State.Name'); test "$state" = "pending"; do
  sleep 2; echo -n '.'
  if [ $retry_count -gt 20 ]; then
    echo maximum number of aws ec2 describe-instances retries reached 1>&2
    exit 1
  fi
  retry_count=`expr $retry_count + 1`
done; echo " $state"

ip_address=`aws ec2 describe-instances --instance-ids $instance_id --output text --region eu-west-1 --query 'Reservations[*].Instances[*].PublicIpAddress'`



# arn:aws:ec2:eu-west-1:2422-7503-6941:instance/i-9afa86da

retry_count=1

# We will need to add "-i ~/.ssh/windows-jenkins-build.pem" to the ssh and scp commands to make this script work with
# st_code/sysadmin_scripts/ec2servers/install-windows.sh

while ! ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null  -o ConnectTimeout=20 Administrator@${ip_address} "/bin/true"; do
    if [ $retry_count -gt 10 ]; then
      echo maximum number of ssh retries reached 1>&2
      exit 1
    fi
    retry_count=`expr $retry_count + 1`
    sleep_seconds=10
    echo sleeps $sleep_seconds seconds.
    sleep $sleep_seconds
done

tmpdir=`mktemp -d`

cd $tmpdir

git clone ssh://jenkins@127.0.0.1:29418/st_client
cd st_client
git fetch ssh://jenkins@127.0.0.1:29418/st_client $GERRIT_REFSPEC && git checkout FETCH_HEAD
cd ..
tar cfz st_client.tar.gz st_client

remote_tmp_source_dir=`ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null Administrator@${ip_address} "mktemp -d /tmp/created_by_jenkins.source.XXXXXX"`
remote_tmp_result_dir=`ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null Administrator@${ip_address} "mktemp -d  /tmp/created_by_jenkins.result.XXXXXX"`

scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null st_client.tar.gz Administrator@${ip_address}:${remote_tmp_source_dir}

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null Administrator@${ip_address} "cd ${remote_tmp_source_dir}; tar xfz st_client.tar.gz; cd st_client; sh build_cygwin.sh ${remote_tmp_source_dir}/st_client stclient_production_build ${remote_tmp_result_dir}"

rm -rf /tmp/windows_build_results
scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r  Administrator@${ip_address}:"${remote_tmp_result_dir}" /tmp/windows_build_results

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null Administrator@${ip_address} "cd /tmp; rm -rf ${remote_tmp_source_dir}; rm -rf ${remote_tmp_result_dir}"
rm -rf "$tmpdir"

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null Administrator@${ip_address} "poweroff"

retry_count=1
while state=$(aws ec2 describe-instances --instance-ids $instance_id --output text --region eu-west-1 --query 'Reservations[*].Instances[*].State.Name'); test ! "$state" = "stopped"; do
  sleep 5; echo -n '.'
  if [ $retry_count -gt 60 ]; then
    echo maximum number of aws ec2 describe-instances retries reached 1>&2
    exit 1
  fi
  retry_count=`expr $retry_count + 1`
done; echo " $state"

