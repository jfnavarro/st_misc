#! /usr/bin/env python
"""
Script to convert ST API database model 2 to model 3
@author: Jose Fernandez
"""

import argparse
import os
import sys

try:
    from pymongo import MongoClient
    from pymongo import errors
    from bson.objectid import ObjectId
except ImportError, e:
    sys.stderr.write("Pymongo was not found, aborting...\n")
    sys.exit(1)

def usage():
    print "Usage:"
    print "  python updateDB.py [options]"
    print "Options:"
    print "  [-a, --user] => username for the MongoDB admin"
    print "  [-d, --password] => password for the MongoDB admin"
    print "  [-c, --host] => (default localhost)"
    print "  [-p, --port] => (default 27017)"
    print "Description:"
    print "  Updates the ST database from data model 2 to data model 3."
    print "  NOTE: It is a wise idea to manually run mongodump to create a backup of the data state prior to the update!"

def main(admin, password, host, port):

    print "Connecting to database..."
    mongoConnection = 0
    try:
        mongoConnection = MongoClient(host, port) 
    except errors.AutoReconnect:
        print 'Cannot connect to database. \nPlease manually start up MongoDB.'
        sys.exit(1)
    
    print "mongoConnection" , mongoConnection
    
    print "Authorizing..."
    try:
        db_admin = mongoConnection["admin"]
        db_admin.authenticate(admin, password)
        print "Authorization Ok!"
    except TypeError,e:
        sys.stderr.write("There was an error in the authentication: " + str(e) + "\n")
        sys.exit(1)
        
    ###############################################################################################################
    db_analysis = mongoConnection["analysis"]
    datasets = db_analysis["dataset"]
    imagealignments = db_analysis["imagealignment"]
    chips = db_analysis["chip"]
    # Remove the experiment database
    mongoConnection.drop_database("experiment")
    # Remove some fields in analysis.dataset
    datasets.update_many({}, {'$unset' : { 'overall_feature_count' : 1}})
    datasets.update_many({}, {'$unset' : { 'overall_hit_count' : 1}})
    datasets.update_many({}, {'$unset' : { 'unique_barcode_count' : 1}})
    datasets.update_many({}, {'$unset' : { 'overall_hit_quartiles' : 1}})
    datasets.update_many({}, {'$unset' : { 'gene_pooled_hit_quartiles' : 1}})
    datasets.update_many({}, {'$unset' : { 'obo_foundry_terms' : 1}})
    # Update the analysis.dataset collection to add the fields from analysis.imagealignment
    for ele in datasets.find():
        try:
            dataset_id = ele["_id"]
            al_id = ele["image_alignment_id"]
            al = imagealignments.find_one({"_id": ObjectId(al_id)})
            if al_id is not None and al is not None:
                datasets.update_one({"_id": dataset_id}, {"$set": {"figure_blue": al["figure_blue"]}})
                datasets.update_one({"_id": dataset_id}, {"$set": {"figure_red": al["figure_red"]}})
                datasets.update_one({"_id": dataset_id}, {"$set": {"alignment_matrix": al["alignment_matrix"]}})
                datasets.update_one({"_id": dataset_id}, {"$set": {"files": [dataset_id + "_stdata.tsv.gz"]}})
            else:
                datasets.delete_one({"_id": dataset_id})
        except KeyError:
            continue
            datasets.delete_one({"_id": dataset_id})
    # Remove image_alignment_id field from analysis.dataset
    datasets.update_many({}, {'$unset' : { 'image_alignment_id' : 1}})
    # Remove analysis.imagealignment and analysis.chip
    imagealignments.drop()
    chips.drop()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-c', '--host', type=str, default="localhost", 
                        help='Address of the host to connect to')
    parser.add_argument('-p', '--port', type=int, default=27017, 
                        help='Port of the host to connect to')
    parser.add_argument('-a', '--user', required=True, type=str, 
                        help='the user name for the admin of the database')
    parser.add_argument('-d', '--password', required=True, type=str, 
                        help='the password for the admin of the database')
    
    args = parser.parse_args()
    main(args.user, args.password, args.host, args.port)