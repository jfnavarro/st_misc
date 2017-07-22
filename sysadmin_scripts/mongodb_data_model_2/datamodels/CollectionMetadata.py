#! /usr/bin/env python

import time
import datetime

class CollectionMetadata(object):
	"""
	Represents metadata for the collections
	"""
	
	collectionname = "admin.collectionmetadata"
	oldlocationname = None
	
	def __init__(self):
		self.collection_id = None
		self.since_model_version = None
		self.last_changed_model_version = None
		self.last_modified = None
		
	
	
	@staticmethod
	def createMetadata(conn):
		
		ts = time.time()
		isodate = datetime.datetime.fromtimestamp(ts, None)
		
		coll = conn["admin"]["collectionmetadata"]
		post = { \
			"collection_name": "feature.<dataset_id>", \
			"since_model_version": "1", \
			"last_changed_model_version": "2" \
			}
		coll.insert(post)
		
		post = { \
			"collection_name": "analysis.dataset", \
			"since_model_version": "1", \
			"last_changed_model_version": "2" \
			}
		coll.insert(post)
		
		post = { \
			"collection_name": "analysis.imagealignment", \
			"since_model_version": "2", \
			"last_changed_model_version": "2" \
			}
		coll.insert(post)
		
		post = { \
			"collection_name": "analysis.chip", \
			"since_model_version": "1", \
			"last_changed_model_version": "2" \
			}
		coll.insert(post)
		
		post = { \
			"collection_name": "user.account", \
			"since_model_version": "1", \
			"last_changed_model_version": "2" \
			}
		coll.insert(post)
		
		post = { \
			"collection_name": "user.datasetinfo", \
			"since_model_version": "2", \
			"last_changed_model_version": "2" \
			}
		coll.insert(post)
		
		post = { \
			"collection_name": "experiment.pipelineexperiment", \
			"since_model_version": "1", \
			"last_changed_model_version": "2" \
			}
		coll.insert(post)
		
		post = { \
			"collection_name": "experiment.pipelinestats", \
			"since_model_version": "2", \
			"last_changed_model_version": "2" \
			}
		coll.insert(post)
		
		post = { \
			"collection_name": "experiment.selection", \
			"since_model_version": "2", \
			"last_changed_model_version": "2" \
			}
		coll.insert(post)
		
		post = { \
			"collection_name": "experiment.task", \
			"since_model_version": "2", \
			"last_changed_model_version": "2" \
			}
		coll.insert(post)
		
		post = { \
			"collection_name": "admin.collectionmetadata", \
			"since_model_version": "2", \
			"last_changed_model_version": "2" \
			}
		coll.insert(post)
		
		coll.create_index("collection_name", unique=True)
		
		