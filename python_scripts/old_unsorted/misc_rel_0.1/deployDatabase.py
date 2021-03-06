#! /usr/bin/env python
# @Created by Jose Fernandez

""" complete definition here """

from optparse import OptionParser
from collections import namedtuple
import csv
import os
import subprocess 
import sys
import datetime
try:
    from pymongo import Connection, GEO2D
    from pymongo import errors
    from gridfs import GridFS
    import numpy as np
except ImportError, e:
    sys.stderr.write("Pymongo or numpy was not found, aborting...\n")
    sys.exit(1)

class Chip(object):
    """Class representing fundamental properties of experiment chip.
    """
    def __init__(self, chipFile):
        self.x1 = np.inf
        self.x2 = -np.inf
        self.y1 = np.inf
        self.y2 = -np.inf
        self.x1_border = np.inf
        self.x2_border = -np.inf
        self.y1_border = np.inf
        self.y2_border = -np.inf
        self.x1_total = np.inf
        self.x2_total = -np.inf
        self.y1_total = np.inf
        self.y2_total = -np.inf

        self.name = stripExtension(chipFile)

        self.barcodes = None

        fh = open(chipFile, "r")
        rder = csv.reader(fh, delimiter="\t")
        DesignRow = namedtuple("DesignRow", rder.next())

        for row in rder:
            d_row = DesignRow(*row)
            x = int(d_row.X)
            y = int(d_row.Y)
            if d_row.CONTAINER == "BORDER":
                self.x1_border = x if x < self.x1_border else self.x1_border
                self.y1_border = y if y < self.y1_border else self.y1_border
                self.x2_border = x if x > self.x2_border else self.x2_border
                self.y2_border = y if y > self.y2_border else self.y2_border
                
            elif d_row.CONTAINER.endswith("PROBES"):
                if self.barcodes == None:
                    self.barcodes = int(d_row.CONTAINER.partition("K")[0]) * 1000

                self.x1 = x if x < self.x1 else self.x1
                self.y1 = y if y < self.y1 else self.y1
                self.x2 = x if x > self.x2 else self.x2
                self.y2 = y if y > self.y2 else self.y2
                
            else:
                self.x1_total = x if x < self.x1_total else self.x1_total
                self.y1_total = y if y < self.y1_total else self.y1_total
                self.x2_total = x if x > self.x2_total else self.x2_total
                self.y2_total = y if y > self.y2_total else self.y2_total

        fh.close()

    
def stripExtension(string):
    f = string.rsplit('.', 1)
    if(f[0].find("/") != -1):
        return f[0].rsplit('/', 1)[1]
    else:
        return f[0]

      
def usage():
    print "Usage:"
    print "python deployDatabase.py [options] barcodes.json stats.txt figureRed.jpg figureBlue.jpg chip.ndf nameExperiment admin password [host] [port] [mongoPAth]"
    print "barcodes.json => json files that contains all the transcripts which is generated by the pipeline"
    print "stats.txt => text file with all the stats that the pipeline generates"
    print "figureRed.jpg => cell tissue figure red (with frame) in jpg format"
    print "figureBlue.jpg => cell tissue figure blue (without frame) in jpg format"
    print "chip.ndf => chip ndf file that contains the chip specs, ususally present in st_doc/array_specs"
    print "Options:"
    print "[-n, --nameDataset] => the name we want the dataset to be stored in the database"
    print "[-a, --admin] => the user name for the admin"
    print "[-d, --password] => the password for the admin"
    print "[-c, --host] => (default localhost)"
    print "[-p, --port] => (default 27017)"
    print "[-m, --mongo-path] =>path to the mongo binaries, e.x /home/mongo/bin/ (default will use PATH locations in system)"

def main(features,stats,redTissue,blueTissue,chipFile,nameExp,admin,password,host,port,mongopath): #reads
    
    if(features == "" or stats == "" or redTissue == "" or admin == "" or password == ""  
       or blueTissue == "" or nameExp == "" or chipFile == "" or not os.path.isfile(chipFile) 
       or not os.path.isfile(redTissue) or not os.path.isfile(blueTissue)
       or not os.path.isfile(features) or not os.path.isfile(stats)): 
        print "One/s of the input files is missing"
        sys.exit(1)
        

    print "Creating Data Base..."
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
        sys.stderr.write("There was an error in the authentication\n")
        sys.exit(1)
    
    print "Adding read/write users to databases"
    
    user = "stviewer_rw"
    user_pass = "sKv3Lnw91yxc"
    
    db_analysis = mongoConnection["analysis"]
    
    db_analysis.add_user(user, user_pass, False )
    db_analysis.authenticate( user, user_pass )
    
    db_general = mongoConnection["general"]
    db_general.add_user(user, user_pass, False )
    db_general.authenticate(user, user_pass)
    
    db_feature = mongoConnection["feature"]
    db_feature.add_user(user, user_pass, False )
    db_feature.authenticate(user, user_pass)
    
    print "Checking chip name is present in DB"
    
    chipName = stripExtension(chipFile)
    datasets_chips = db_analysis["chip"]
    
    chip = datasets_chips.find_one({"name": chipName})
    if(chip):
        print "Chip is already present, using the id of the present chip"
        #datasets_chips.remove(chip)
        id_chips = chip["_id"]
    else:
        chipObject = Chip(chipFile)
        id_chips = datasets_chips.insert({"name" : chipName, 
                                          "barcodes" : chipObject.barcodes, 
                                          "x1" : chipObject.x1, 
                                          "y1" : chipObject.y1, 
                                          "x1_border" : chipObject.x1_border, 
                                          "x2_border" : chipObject.x2_border, 
                                          "x1_total" : chipObject.x1_total, 
                                          "y1_total" : chipObject.y1_total,
                                          "x2" : chipObject.x2, 
                                          "y2" : chipObject.y2, 
                                          "x2_border" : chipObject.x2_border, 
                                          "y2_border" : chipObject.y2_border, 
                                          "x2_total" : chipObject.x2_total, 
                                          "y2_total" : chipObject.y2_total })   
    
        
    print "Creating datasets (stats and figures) and chips in the analysis table"
    
    
    """ I should move the figures to the amazon storage partition as soon as I know when that is """
    
    """ I should get the stats from the stat file """
    
    
    datasets_collection = db_analysis["dataset"]
    dataset = datasets_collection.find_one({"name": nameExp})
    if(dataset):
        print "Dataset already present, removing previous one..."
        datasets_collection.remove(dataset)
    id_dataset = datasets_collection.insert({"name" : nameExp, 
                                             "chipid" : id_chips, 
                                             "figure_x1" : 0, 
                                             "figure_x2" : 0, 
                                             "figure_y1" : 0, 
                                             "figure_y2" : 0, 
                                             "figure_blue" : blueTissue,
                                             "figure_red" : redTissue, 
                                             "figure_status" : 0,
                                             "stat_barcodes" :0,
                                             "stat_genes" :0,
                                             "stat_unique_genes" :0,
                                             "stat_unique_barcodes" : 0,
                                             "stat_tissue" : "brain",
                                             "stat_specie" : "mouse",
                                             "created" : datetime.datetime.utcnow()})
    

    print "Creating features table"
    
    print "Importing features from json file " + features

    proc = subprocess.Popen([mongopath + 'mongoimport','--host',host,'--port',str(port),
                             "--collection",str(id_dataset),'--db','feature','--file',features,'--upsert','-u',user,'-p',user_pass], 
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, errmsg) = proc.communicate()
    print stdout
    
    print "Creating indexes"
    
    db_feature.nameExp.create_index([("loc", GEO2D)])
    db_feature.nameExp.create_index("gene")
    
    print "Creating projection (not functional yet)"
    
    
    
        
    print "Creating computational analysis test example"
    
    analysis_collection = db_general["analysis"]
    
    test_analysis = analysis_collection.find_one({"name": "dea_test"})
    if(test_analysis):
        print "Test Analysis is already present, removing previous one.."
        analysis_collection.remove(test_analysis)
        
    analysis_id = analysis_collection.insert({"name" : "dea_test" , "dummy" : 0, "datasetId" : id_dataset})

    
    print "DONE"

if __name__ == "__main__":
    
    parser = OptionParser()
    parser.add_option("-c", "--host", dest="host",default="localhost")
    parser.add_option("-p", "--port", dest="port",default=27017)
    parser.add_option("-n", "--nameDataset", dest="nameExp")
    parser.add_option("-a", "--admin", dest="admin")
    parser.add_option("-d", "--password", dest="password")
    parser.add_option("-m", "--mongo-path", dest="mongopath")

    options, args = parser.parse_args()
    if len(args) == 5:
        features, stats, redTissue, blueTissue, chipFile = args
    else:
        print usage()
        sys.exit()
    
    main(features,stats,redTissue,blueTissue,chipFile,str(options.nameExp),str(options.admin),
         str(options.password),str(options.host),int(options.port),str(options.mongopath))
                                    
