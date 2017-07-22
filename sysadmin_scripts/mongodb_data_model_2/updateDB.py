#! /usr/bin/env python

'''
@author: Joel Sjostrand
'''

import time
import datetime

import argparse
import os
import sys
from Helper import Helper
from datamodels.CollectionMetadata import CollectionMetadata
from datamodels.Account import Account
from datamodels.Dataset_and_ImageAlignment import Dataset
from datamodels.Dataset_and_ImageAlignment import ImageAlignment
from datamodels.Chip import Chip
from datamodels.DatasetInfo import DatasetInfo
from datamodels.Feature import Feature
from datamodels.PipelineExperiment import PipelineExperiment
from datamodels.Task import Task

try:
    from pymongo import Connection
    from pymongo import errors
except ImportError, e:
    sys.stderr.write("Pymongo was not found, aborting...\n")
    sys.exit(1)
    
    
   

def usage():
    print "Usage:"
    print "  python updateDB.py [options]"
    print "Options:"
    print "  [-a, --admin] => username for the MongoDB admin"
    print "  [-d, --password] => password for the MongoDB admin"
    print "  [-c, --host] => (default localhost)"
    print "  [-p, --port] => (default 27017)"
    print "  [-m, --mongo-path] =>path to the mongo binaries, e.x /home/mongo/bin/ (default will use PATH locations in system)"
    print "Description:"
    print "  Updates the ST database from data model 1 to data model 2."
    print "  NOTE: It is a wise idea to manually run mongodump to create a backup of the data model 1 state prior to the update!"




def main(admin, password, host, port, mongopath): #reads
    
    if (admin == None or password == None or host == None or port == None or mongopath == None): 
        print "One or more of the input arguments is missing"
        sys.exit(1)
        

    print "Connecting to database..."
    mongoConnection = 0
    try:
        mongoConnection = Connection(host + ":" + str(port),fsync=True) 
    except errors.AutoReconnect:
        print 'Cannot connect to database. \nPlease manually start up MongoDB.'
        sys.exit(1)
    
    print "mongoConnection" , mongoConnection
    
    print "Authorizing..."

    try:
        db_admin = mongoConnection["admin"]
        db_admin.authenticate(admin, password)
    except TypeError,e:
        sys.stderr.write("There was an error in the authentication: " + str(e) + "\n")
        sys.exit(1)
        
    ###############################################################################################################
        
    print "Verifying version of database..."
    hlp = Helper(mongoConnection)
    isUpgradable = False
    try:
        # To do this properly, one would check all collections...
        coll = hlp.getCollection(CollectionMetadata.collectionname)
        dummy = coll.find_one({"collection_name": "analysis.dataset"})
        v = dummy["last_changed_model_version"]
        if float(v) >= 2.0:
            isUpgradable = False
        else:
            isUpgradable = True
    except TypeError, e:
        # No such collection means we're at an older DB data model.
        isUpgradable = True
    if not isUpgradable:
        sys.stderr.write("... aborting -- this database already has an equal or newer data model than 2.0.\n")
        sys.exit(1) 
    else:
        print "...OK, proceeding with data model update."

    ###############################################################################################################
    
    #print "Updating user.account..."
    #Account.extendAccount(mongoConnection)
    #print "...done!"
    
    #print "Updating analysis.dataset and analysis.imagealignment..."
    #Dataset.updateDataset(mongoConnection)
    #print "...done!"

    #print "Updating analysis.chip..."
    #Chip.extendChip(mongoConnection)
    #print "...done!"
    
    #print "Updating user.datasetinfo..."
    #DatasetInfo.createDatasetInfo(mongoConnection)
    #print "...done!"
    
    #print "Updating feature.feature..."
    #Feature.extendFeatures(mongoConnection)
    #print "...done!"
    
    print "Updating experiment.experiment and experiment.pipelinestats..."
    PipelineExperiment.updatePipelineExperiment(mongoConnection)
    print "...done!"
    
    print "Updating experiment.task and experiment.selection..."
    Task.createDummyTask(mongoConnection)
    print "...done!"
    
    print "Updating admin.collectionmetadata..."
    CollectionMetadata.createMetadata(mongoConnection)
    print "...done!"
    
    
    

    

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-c', '--host',                type=str, default="localhost", help='Address of the host to connect to')
    parser.add_argument('-p', '--port',                type=str, default=27017, help='Port of the host to connect to')
    parser.add_argument('-a', '--admin',               type=str, default=" ", help='the user name for the admin of the database')
    parser.add_argument('-d', '--adminpassword',       type=str, default=" ", help='the password for the admin of the database')
    parser.add_argument('-m', '--mongo_path',          type=str, default=" ", help='path to the mongo binaries, e.x /home/mongo/bin/ (default will use PATH locations in system)')
    
    args = parser.parse_args()
    
    main(args.admin, args.adminpassword, args.host, args.port, args.mongo_path)
                                    

