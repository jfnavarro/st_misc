#! /usr/bin/env python
#import time
#import datetime

class Chip(object):
	"""
	Represents a chip
	"""
	
	collectionname = "analysis.chip"
	oldlocationname = "analysis.chip"
		
		
	@staticmethod
	def extendChip(conn):
		coll = conn["analysis"]["chip"]
		
		#ts = time.time()
		#isodate = datetime.datetime.fromtimestamp(ts, None)
		#coll.update({}, {"$set": {"last_modified": isodate}}, upsert=False, multi=True)
		
		coll.ensure_index("name", unique=True)
		