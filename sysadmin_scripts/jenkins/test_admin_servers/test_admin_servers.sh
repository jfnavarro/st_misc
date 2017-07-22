#!/bin/sh

# This script tests one of the servers
#
# admin.spatialtranscriptomics.com
# admin-dev.spatialtranscriptomics.com
#
set -e

#
# The SECRETID and CLIENTID can be found in the st_client source code:
#
# $ grep SECRETID st_client/CMakeLists.txt
# set(SECRETID "ayfBaF5UAKR2")
# $ grep CLIENTID st_client/CMakeLists.txt
# set(CLIENTID "st-viewer-client")
# $ 

# This script returns exit status 2 if there might be a temporary problem.

SECRETID=ayfBaF5UAKR2
CLIENTID=st-viewer-client

server=$1

iterations=$2

# We make use of the public DNS of each AWS EC2 instance.
#
# esjolund@zebra:/tmp$ host admin.spatialtranscriptomics.com
# admin.spatialtranscriptomics.com is an alias for ec2-54-171-170-214.eu-west-1.compute.amazonaws.com.
# ec2-54-171-170-214.eu-west-1.compute.amazonaws.com has address 54.171.170.214
# esjolund@zebra:/tmp$ 
#
# But that public DNS of an AWS EC2 instance has different IP addresses if queried from AWS or from internet.
# (Either the public IP address or the private IP address is returned from the DNS nameserver).
# Right now (2015-06-25) the https://admin.spatialtranscriptomics.com only listens on the public IP address.
# That is why we have to add the --resolve option to the curl command.
# We should probably change this in the future so that the 
#  https://admin.spatialtranscriptomics.com 
# listens on both the public and private IP address. We could then save some money because there is no cost (as in money)
# for network traffic between private IP addresses.

resolve_option="--resolve admin-dev.spatialtranscriptomics.com:443:54.171.51.182 --resolve admin.spatialtranscriptomics.com:443:54.171.170.214"

fetch () {
  http_return_code=`curl -w '%{http_code}' -s -o /dev/null $resolve_option   "$1"`
  if [ ! \( 200 -eq "$http_return_code" -o 401 -eq "$http_return_code" \) ]; then
    exit 1
  fi
  if [ 401 -eq "$http_return_code" ]; then
    # We might want to treat HTTP return code 401 (Unauthorized) in a special way so we give
    # this information to the caller by returning 401.
    exit 2
  fi
}

if [ $# -ne 2  ]; then
  echo Wrong number of arguments
  exit 1
fi

# This construct:
# "$iterations" -eq "$iterations"
# verifies that $iterations is a number

if [ ! \( "$server" = "admin" -o "$server" = "admin-dev" \) -o ! "$iterations" -eq "$iterations" ]; then
  echo "Usage: `basename $0` [ admin | admin-dev ] num_iterations"
  exit 1
fi

if [ "$server" = "admin-dev" ]; then
  username=test-admin@scilifelab.se
  password=1234
fi

if [ "$server" = "admin" ]; then
  username=erik.sjolund@scilifelab.se
  password=spattigtransa
fi

tmpdir=`mktemp -d`
chmod 700 $tmpdir

token_output="$tmpdir/fetch_token"

# This script requires that jq is installed.
# Homepage: http://stedolan.github.io/jq/
# To install jq on Ubuntu run 
# apt-get install jq

http_return_code=`curl -w '%{http_code}' -s -o "$token_output" -u ${CLIENTID}:${SECRETID} --data "" -X POST  -H "Content-Type: application/json" -H "Content-Length: 0" \
 $resolve_option \
   "https://$server.spatialtranscriptomics.com/api/oauth/token?grant_type=password&scope=read&username=${username}&password=${password}" `

if [ 200 -ne "$http_return_code" ]; then
  exit 2
fi

token=`jq -r .access_token "$token_output"`

cd $tmpdir

for i in `seq 1 $iterations`; do 
  if [ "$server" = "admin-dev" ]; then
    fetch "https://admin-dev.spatialtranscriptomics.com/api/rest/versionsupportinfo"
    fetch "https://admin-dev.spatialtranscriptomics.com/api/rest/account/current/user?access_token=$token"
    fetch "https://admin-dev.spatialtranscriptomics.com/api/rest/dataset?access_token=$token"
    fetch "https://admin-dev.spatialtranscriptomics.com/api/rest/imagealignment/5382fe346d6e9e7d90c7bd55?access_token=$token"
    fetch "https://admin-dev.spatialtranscriptomics.com/api/rest/image/compressed/130219_558894_1F_blue.jpg?access_token=$token"
    fetch "https://admin-dev.spatialtranscriptomics.com/api/rest/image/compressed/130219_558894_1F_red_blue.jpg?access_token=$token"
    fetch "https://admin-dev.spatialtranscriptomics.com/api/rest/features/51bad2e8e4b0129270296cce?access_token=$token"
    fetch "https://admin-dev.spatialtranscriptomics.com/api/rest/chip/51bad25fe4b0129270296ccd?access_token=$token"
  fi
  if [ "$server" = "admin" ]; then
    fetch "https://admin.spatialtranscriptomics.com/api/rest/versionsupportinfo"
    fetch "https://admin.spatialtranscriptomics.com/api/rest/account/current/user?access_token=$token"
    fetch "https://admin.spatialtranscriptomics.com/api/rest/dataset?access_token=$token"
    fetch "https://admin.spatialtranscriptomics.com/api/rest/imagealignment/54623f23e4b08455172629e5?access_token=$token"
    fetch "https://admin.spatialtranscriptomics.com/api/rest/image/compressed/141104_1000L_CN2_D1_MOB15_HE_FS.jpg?access_token=$token"
    fetch "https://admin.spatialtranscriptomics.com/api/rest/image/compressed/141104_1000L_CN2_D1_MOB15_HE_FS.jpg?access_token=$token"
    fetch "https://admin.spatialtranscriptomics.com/api/rest/features/547d9b05e4b095d5541949ed?access_token=$token"
    fetch "https://admin.spatialtranscriptomics.com/api/rest/chip/53efc8eae4b00814323c330f?access_token=$token"
  fi
done
