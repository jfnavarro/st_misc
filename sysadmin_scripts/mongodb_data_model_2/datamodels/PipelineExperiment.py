#! /usr/bin/env python

import time
import datetime
from PipelineStats import PipelineStats

class PipelineExperiment(object):
	"""
	Represents an experiment as resulting from the pipeline being run
	"""
	
	collectionname = "experiment.pipelineexperiment"
	oldlocationname = "experiment.experiment"
		
	@staticmethod
	def updatePipelineExperiment(conn):
		coll = conn["experiment"]["experiment"]
		#ts = time.time()
		#isodate = datetime.datetime.fromtimestamp(ts, None)
		#accCol = conn["user"]["account"]
		#acc = accCol.find_one({})
		#accid = str(acc["_id"])
		#for exp in list(coll.find()):
		#	id_ = exp["_id"]
		#	stats_id = str(PipelineStats.createStats(conn, str(id_)))
		#	coll.update({'_id': id_}, {"$set": {"account_id": accid}}, upsert=False, multi=True)
		#coll.update({}, {"$unset": {"created": 1}}, upsert=False, multi=True)
		coll.update({}, {"$set": {"emr_state": "COMPLETED", "emr_creation_date_time": None, "emr_end_date_time": None, "emr_last_state_change_reason": None }}, multi=True)
		coll.ensure_index("name", unique=True)
		coll.ensure_index("account_id")
		coll.rename("pipelineexperiment")
		