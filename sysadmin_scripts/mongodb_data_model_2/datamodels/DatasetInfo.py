#! /usr/bin/env python

import time
import datetime
import pymongo

class DatasetInfo(object):
	"""
	Represents user access to a dataset
	"""
	
	collectionname = "user.datasetinfo"
	oldlocationname = None
	
	@staticmethod
	def createDatasetInfo(conn):
		coll = conn["user"]["datasetinfo"]
		collAcc = conn["user"]["account"]
		
		# Compound index.
		coll.ensure_index([("account_id", pymongo.ASCENDING), ("dataset_id", pymongo.ASCENDING)], unique=True)
		
		# Retrieval indices.
		coll.ensure_index("account_id")
		coll.ensure_index("dataset_id")
		
		l = list(collAcc.find())
		for item in l:
			accid = item["_id"]
			dss = item["grantedDatasets"]
			#ts = time.time()
			#isodate = datetime.datetime.fromtimestamp(ts, None)
			
			for ds in dss:
				dsid = str(ds)
				post = { \
					"account_id": str(accid), \
					"dataset_id": str(dsid), \
					"comment": "" \
				}
				coll.insert(post)
				
		# Drop account stuff
		collAcc.update({}, {"$unset": {'grantedDatasets': 1}}, upsert=False, multi=True)
		
		