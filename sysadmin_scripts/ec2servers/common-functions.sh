# This file contains some shell functions that we could reuse if we create more installation scripts for our AWS EC2 instances.
# The file is meant to be sourced in a shell script.

adjust_variables_for_region() {
  region="$1"
  case "$region" in
    eu-west-1)
      availability_zone=eu-west-1a
      subnet="subnet-29845f4c"
      ubuntu_14_04_ami=ami-234ecc54
      ssh_security_group=sg-836fc1e6
      https_http_anywhere_security_group=sg-cac27daf
      https_http_scilife_security_group=sg-ecb90589
    ;;
    us-east-1)
      availability_zone=us-east-1a
      subnet="subnet-22da4355"
      ubuntu_14_04_ami=ami-9a562df2
      ssh_security_group=sg-44ad2820
      https_http_anywhere_security_group=sg-1aad287e
      https_http_scilife_security_group=sg-dbad28bf
    ;;
  *) echo "unknown region: $region"
     exit 1
    ;;
  esac
}

run_command() {
  ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${ip_address} $@
}

copy_command() {
  scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $1 root@${ip_address}:$2
}

copy_with_mode_command() {
  scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $1 root@${ip_address}:$2
  run_command chmod $3 $2
}

install_command() {

echo installing $ami

  # TODO: remove this  --key-name spatial
  # when it seems to work
  instance_id=`aws ec2 run-instances --image-id $ami --count 1 --instance-type $instancetype --region $region --placement AvailabilityZone=$availability_zone  --security-group-ids $ssh_security_group --iam-instance-profile Name=$server --subnet-id $subnet  --user-data file://scripts/user-data.sh  --block-device-mapping "[ { \"DeviceName\": \"/dev/sda1\", \"Ebs\": { \"VolumeSize\": $root_volume_size } } ]"  --disable-api-termination --output text --query 'Instances[*].InstanceId'`

  # From http://alestic.com/2013/11/aws-cli-query
  # Wait for the instance to be created
  while state=$(aws ec2 describe-instances --instance-ids $instance_id --output text --region $region --query 'Reservations[*].Instances[*].State.Name'); test -n "$state" -a "$state" = "pending"; do
    sleep 1; echo -n '.'
  done; echo " $state"

  ip_address=`aws ec2 describe-instances --instance-ids $instance_id --output text --region $region --query 'Reservations[*].Instances[*].PublicIpAddress'`

  echo ip_address=$ip_address

  # Right now we are using  StrictHostKeyChecking=no
  # http://serverfault.com/questions/330503/scp-without-known-hosts-check
  # but we would like to retrieve the ssh host key by a script instead
  # http://xocoatl.blogspot.se/2011/03/starting-ec2-instance.html
  # or should we somehow provide the ssh host key with the user-data script?

  retry_count=1
  while ! ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null  -o ConnectTimeout=20 root@${ip_address} "/bin/true"; do
    if [ $retry_count -gt 10 ]; then
      echo maximum number of ssh retries reached 1>&2
      exit 1
    fi
    retry_count=`expr $retry_count + 1`
    sleep_seconds=10
    echo sleeps $sleep_seconds seconds. Although the instance is in pending state, we are not yet able to log in
    sleep $sleep_seconds
  done

  for i in ssh_host_dsa_key ssh_host_ecdsa_key ssh_host_rsa_key; do 
    copy_with_mode_command copy-out-files/ssh/${server}/$i /etc/ssh/$i 600
    copy_with_mode_command copy-out-files/ssh/${server}/${i}.pub /etc/ssh/$i.pub 644
  done

  copy_command scripts/common.sh /root/common.sh
  run_command sh /root/common.sh
  run_command rm /root/common.sh
}

create_extra_volume_and_mount_it() {

partition="$1"
size="$2"
mountpoint="$3"
name="$4"

extravolume=`aws ec2 create-volume --volume-type standard --availability-zone $availability_zone --size $size  --query VolumeId --region $region`

state="dummystring"
retry_count=1
while [ "$state" != "available" ]; do
  if [ $retry_count -gt 40 ]; then
    echo maximum number of ssh retries reached 1>&2
    exit 1
  fi
aws ec2 describe-volumes --volume-id "$extravolume" --output text --query 'Volumes[*].State'  --region $region
  state=`aws ec2 describe-volumes --volume-id "$extravolume" --output text --query 'Volumes[*].State'  --region $region`
  retry_count=`expr $retry_count + 1`
  sleep_seconds=3
  echo sleeps $sleep_seconds seconds waiting for volume to become available
  sleep $sleep_seconds
done
aws ec2 create-tags --resources $extravolume --tags "Key=Name,Value=$name" --region $region
aws ec2 attach-volume --instance-id $instance_id --volume-id $extravolume --device /dev/$partition --region $region

retry_count=1
while ! run_command grep -q $partition /proc/partitions; do
  if [ $retry_count -gt 40 ]; then
    echo maximum number of ssh retries reached 1>&2
    exit 1
  fi
  retry_count=`expr $retry_count + 1`
  sleep_seconds=1
  echo sleeps $sleep_seconds seconds waiting for partition $partition to be seen in /proc/partitions
  sleep $sleep_seconds
done

run_command "mkdir -p $mountpoint"
run_command "mkfs -t ext4 /dev/$partition"
run_command "echo  /dev/$partition $mountpoint  ext4   defaults,nobootwait,noatime,nofail  0 2 >> /etc/fstab"
run_command "mount $mountpoint"

}


reboot_instance() {

reboot_file=/root/has_rebooted_after_admin_installation

# It seems crontab has a non-zero exit code if no crontab has been installed for that user.
# That is why we add "|| /bin/true" so the shell script doesn't stop.
run_command "crontab -l > /root/crontab.saved || /bin/true"

run_command "echo @reboot /usr/bin/touch $reboot_file > /tmp/my_crontab"
run_command "crontab /tmp/my_crontab"
run_command reboot

retry_count=1
while ! run_command ls $reboot_file; do
  if [ $retry_count -gt 40 ]; then
    echo maximum number of ssh retries reached 1>&2
    exit 1
  fi
  retry_count=`expr $retry_count + 1`
  sleep_seconds=10
  echo sleeps $sleep_seconds seconds. Instance is still rebooting. 
  sleep $sleep_seconds
done

run_command "crontab /root/crontab.saved ; rm /root/crontab.saved"

}
