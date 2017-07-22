'''
Helper methods for accessing the DBs, etc.
'''

class Helper:
    
    def __init__(self, mongoconn):
        self.mongoconnection = mongoconn


    def getDB(self, fullpath):
        parts = fullpath.split('.')
        dbname = parts[0]
        return self.mongoconnection[dbname]
        
        
    def getCollection(self, fullpath):
        parts = fullpath.split('.')
        dbname = parts[0]
        collname = parts[1]
        db = self.mongoconnection[dbname]
        return db[collname]
    
