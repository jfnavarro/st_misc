#! /usr/bin/env python

import time
import datetime
from Selection import Selection

class Task(object):
	"""
	Represents an experiment task
	"""
	
	collectionname = "experiment.task"
	oldlocationname = None
	
		
	
	@staticmethod
	def createDummyTask(conn):
		ts = time.time()
		isodate = datetime.datetime.fromtimestamp(ts, None)
		accCol = conn["user"]["account"]
		acc = accCol.find_one({})
		accid = str(acc["_id"])
		coll = conn["experiment"]["task"]
		sell = list()
		selid = str(Selection.createDummySelection(conn))
		sell.append(selid)
		post = { \
			"name": "Dummy task", \
			"status": "Active", \
			"start": isodate, \
			"end": isodate, \
			"account_id": accid, \
			"parameters": "a2+b2=c2", \
			"selection_ids": sell, \
			"result_file": "None" \
		}
		coll.insert(post)
		coll.ensure_index("name", unique=True)
		coll.ensure_index("account_id")
		
		