#!/bin/sh

# This script tests one of the servers
#
# admin.spatialtranscriptomics.com
# admin-dev.spatialtranscriptomics.com
#

# The script can be run like this:
# sh test_admin_servers_allow_a_few_failures.sh admin 1
#
# to test admin.spatialtranscriptomics.com with one iteration.
# If test_admin_servers.sh has a temporary failure this script retries up til 3 times.

counter=0
return_code=2

while [ $return_code -eq 2 -a $counter -lt 3 ]; do
  sh /var/lib/jenkins/st_code/sysadmin_scripts/jenkins/test_admin_servers/test_admin_servers.sh $@
  return_code=$?
  counter=`expr $counter + 1`
  if [ $return_code -eq 2 ]; then
    sleep 120
  fi
done

exit $return_code
