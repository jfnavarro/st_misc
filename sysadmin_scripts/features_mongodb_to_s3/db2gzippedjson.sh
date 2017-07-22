#!/bin/bash

# Exports a feature collection passed in by its name (==dataset object ID) to a compressed JSON file.
# Facilitates migration from MongoDB to S3.

# TODO before running: Replace PASSWORD below


FID=$1
echo "STARTING EXPORT OF $FID"
#mongoexport --authenticationDatabase admin -u admin -p PASSWORD -d feature -c $FID -f barcode,gene,hits,x,y -o $FID.dump.json --jsonArray
mongoexport -d feature -c $FID -f x,y,hits,barcode,gene -o $FID.dump.json --jsonArray
echo "FINISHED EXPORT OF $FID"

echo "STARTING CLEANUP OF $FID.dump.json as $FID"
sed 's/ \"_id\" : { \"$oid\" : \"[a-z0-9]*\" }, / /g' $FID.dump.json > $FID
rm $FID.dump.json
echo "FINISHED CLEANUP OF $FID.dump.json as $FID"

echo "STARTING gzip of $FID"
gzip $FID
echo "FINISHED gzip of $FID"

