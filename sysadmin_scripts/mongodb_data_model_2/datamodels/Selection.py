	#! /usr/bin/env python

import time
import datetime

class Selection(object):
	"""
	Represents a selection of features (as a list, not shape) made by e.g. the user.
	"""
	
	collectionname = "experiment.selection"
	oldlocationname = None
		
		
	@staticmethod
	def createDummySelection(conn):
		#ts = time.time()
		#isodate = datetime.datetime.fromtimestamp(ts, None)
		accCol = conn["user"]["account"]
		acc = accCol.find_one({})
		accid = str(acc["_id"])
		dsCol = conn["analysis"]["dataset"]
		ds = dsCol.find_one({})
		dsid = str(ds["_id"])
		#feaCol = conn["feature"][dsid]
		#fea = feaCol.find_one({})
		#feaid = str(fea["_id"])
		coll = conn["experiment"]["selection"]
		post = { \
			"enabled": "true", \
			#"feature_ids": [feaid], \
			"gene_hits": [ [ "hsp90ab1", "23456", "123.345", "345.45", "456.456" ], ["hsp90aa1", "12345", "456.456", "345.456" ] ], \
			"account_id": accid, \
			"dataset_id": dsid, \
			"name": "Dummy selection", \
			"type": "Lasso selected", \
			"status": "Active", \
			"obo_foundry_terms": ["Abra", "Ca", "Dabra"], \
			"comment": "Well done!" \
		}
		p = coll.insert(post)
		coll.ensure_index("name", unique=True)
		coll.ensure_index("account_id")
		coll.ensure_index("dataset_id")
		return p
		