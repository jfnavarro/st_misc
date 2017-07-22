#! /usr/bin/env python
# @Created by Jose Fernandez

""" complete definition here """

import argparse
import os
import sys
try:
    from pymongo import Connection
    from pymongo import errors
except ImportError, e:
    sys.stderr.write("Pymongo was not found, aborting...\n")
    sys.exit(1)


def main(username,userpassword,userrole,userdatasets,admin,password,host,port,mongopath):
    
    if(username == "" or userpassword == "" or userrole not in ["ROLE_USER","ROLE_ADMIN"] 
       or len(userdatasets) == 0 or admin == "" or password == ""):
        sys.stderr.write("Error in the options, type python addUser.py --help\n")
        sys.exit(1)
        
    print "Connection to Data Base..."
    mongoConnection = 0
    try:
        mongoConnection = Connection(host + ":" + str(port),fsync=True) 
    except errors.AutoReconnect:
        print 'Cannot connect to database. \nPlease manually start up mongoDB before pipeline continues'
        sys.exit(1)
    
    print "mongoConnection" , mongoConnection
    
    print "Authorizing.."

    try:
        db_admin = mongoConnection["admin"]
        db_admin.authenticate(admin,password)
    except TypeError,e:
        sys.stderr.write("There was an error in the authenticatio\n")
        sys.exit(1)
    
    print "Adding read/write users to databases"
    
    user = "stviewer_rw"
    user_pass = "sKv3Lnw91yxc"
    
    db_user = mongoConnection["user"]
    db_user.add_user(user, user_pass, False )
    db_user.authenticate( user, user_pass )
    
    print "Checking if user name is present in DB"
    
    user_userdetails = db_user["userdetail"]
    
    user = user_userdetails.find_one({"username": username})
    if(user):
        print "User is already present, removing previous one.."
        user_userdetails.remove(user)

    print "Creating user"
    id_user = user_userdetails.insert({"username" : username, 
                                       "password" : userpassword, 
                                       "role" : userrole, 
                                       "grantedDatasets" : userdatasets})   
    
    print "DONE"

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-b', '--datasets', nargs='+', type=str, help='Space sparated list of name of datasets ids the user can access to')
    parser.add_argument('-u', '--userpassword',        type=str, help='Password of the user to be created')
    parser.add_argument('-z', '--username',            type=str, help='Name of the user to be created')
    parser.add_argument('-r', '--userrole',            type=str, help='Role of the user to be created ROLE_USER|ROLE_ADMIN')
    parser.add_argument('-c', '--host',                type=str, default="localhost", help='Address of the host to connect to')
    parser.add_argument('-p', '--port',                type=str, default=27017, help='Port of the host to connect to')
    parser.add_argument('-a', '--admin',               type=str, help='the user name for the admin of the database')
    parser.add_argument('-d', '--adminpassword',       type=str, help='the password for the admin of the database')
    parser.add_argument('-m', '--mongo_path',          type=str, help='path to the mongo binaries, e.x /home/mongo/bin/ (default will use PATH locations in system)')
    
    args = parser.parse_args()
    main(args.username, args.userpassword, args.userrole, args.datasets, 
         args.admin, args.adminpassword, args.host, args.port, args.mongo_path)
                                    

