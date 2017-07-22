#!/bin/sh

# This script installs a Windows server 2012 EC2 instance with awscli.
# More documentation is found in the powershell script:
# install-windows.userdata.txt

rdp_security_group=sg-946a0cf1
ssh_security_group=sg-836fc1e6
instancetype=t2.medium

root_volume_size=50
windows_ami=ami-68347d1f
instance_id=`aws ec2 run-instances --image-id $windows_ami --count 1 --instance-type $instancetype  --block-device-mapping "[ { \"DeviceName\": \"/dev/sda1\", \"Ebs\": { \"VolumeSize\": $root_volume_size } } ]" --region eu-west-1 --placement AvailabilityZone=eu-west-1a --key-name windows-jenkins-build --security-group-ids $ssh_security_group $rdp_security_group  --subnet-id subnet-29845f4c  --user-data file://install-windows.userdata.txt  --output text --query 'Instances[*].InstanceId'`
ip_address=`aws ec2 describe-instances --instance-ids $instance_id --output text --region eu-west-1 --query 'Reservations[*].Instances[*].PublicIpAddress'`
echo ip_address=$ip_address

