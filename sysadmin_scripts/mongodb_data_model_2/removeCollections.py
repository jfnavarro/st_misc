#! /usr/bin/env python

'''
@author: Joel Sjostrand
'''


import argparse
import sys
from Helper import Helper
from datamodels.CollectionMetadata import CollectionMetadata

try:
    from pymongo import Connection
    from pymongo import errors
except ImportError, e:
    sys.stderr.write("Pymongo was not found, aborting...\n")
    sys.exit(1)
    
    
   

def usage():
    print "Usage:"
    print "  python removeCollections.py [options]"
    print "Options:"
    print "  [-a, --admin] => the user name for the admin"
    print "  [-d, --password] => the password for the admin"
    print "  [-c, --host] => (default localhost)"
    print "  [-p, --port] => (default 27017)"
    print "  [-m, --mongo-path] =>path to the mongo binaries, e.x /home/mongo/bin/ (default will use PATH locations in system)"
    print "Description:"
    print "   Deletes all collections for data model 2 for the case of restoring a model 1 dump. Mongo system.users collections are not touched."
    print "   This script should be run prior to (manually) running mongorestore <dump>, so as to ensure that new collections are also removed."





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
        
#    print "Verifying version of database..."
#    hlp = Helper(mongoConnection)
#    isUpgraded = False
#    try:
#        # To do this properly, one would check all collections...
#        coll = hlp.getCollection(CollectionMetadata.collectionname)
#        dummy = coll.find_one({"collection_name": "analysis.dataset"})
#        v = dummy["last_changed_model_version"]
#        if float(v) >= 2.0:
#            isUpgraded = True
#        else:
#            isUpgraded = False
#    except TypeError, e:
#        # No such collection means we're at an older DB data model.
#        isUpgraded = False
#    if not isUpgraded:
#        sys.stderr.write("... aborting -- this database already seems to be older than data model 2.0.\n")
#        sys.exit(1) 
#    else:
#        print "...OK, proceeding with data model 2 clean."

    ###############################################################################################################
    
    print "Deleting analysis DB..."
    mongoConnection.drop_database('analysis')
    print "...done!"
    
    print "Deleting experiment DB..."
    mongoConnection.drop_database('experiment')
    print "...done!"
    
    print "Deleting feature DB..."
    mongoConnection.drop_database('feature')
    print "...done!"
    
    print "Deleting user collections..."
    coll = mongoConnection["user"]["account"]
    coll.drop()
    coll = mongoConnection["user"]["datasetinfo"]
    coll.drop()
    print "...done!"
    
    print "Deleting admin collections..."
    coll = mongoConnection["admin"]["collectionmetadata"]
    coll.drop()
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
                                    

