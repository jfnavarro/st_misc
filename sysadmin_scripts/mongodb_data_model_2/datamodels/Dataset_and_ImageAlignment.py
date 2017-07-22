#! /usr/bin/env python
import datetime
import time
from bson.objectid import ObjectId
from datamodels.Feature import Feature

class Dataset(object):

	"""
	Represents a dataset
	"""
	
	collectionname = "analysis.dataset"
	oldlocationname = "analysis.dataset"
	

	@staticmethod	
	def updateDataset(conn):
		coll = conn["analysis"]["dataset"]
		chipColl = conn["analysis"]["chip"]
		ImageAlignment.createIndex(conn)
		
		# Rename some fields
		coll.update({}, {"$rename": {'stat_genes': 'overall_feature_count', \
									'stat_unique_barcodes': 'unique_barcode_count', 'stat_unique_genes': 'unique_gene_count', \
									'stat_tissue': 'tissue', 'stat_specie': 'species', 'stat_comments': 'comment'}}, upsert=False, multi=True)
		
		i = 0
		l = list(coll.find())
		accCol = conn["user"]["account"]
		acc = accCol.find_one({})
		accid = str(acc["_id"])
		for ds in l:
			# Create image alignment
			id = ds["_id"]
			chipId = ds["chipid"]
			chip = chipColl.find_one({"_id": ObjectId(chipId)})
			chipName = chip["name"]
			name = str(i) + " " + chipName
			figureRed = ds["figure_red"]
			figureBlue = ds["figure_blue"]
			alignmentMatrix = ds["alignment_matrix"]
			imal = ImageAlignment.createDocument(conn, chipId, figureRed, figureBlue, alignmentMatrix, name)
			i += 1
			
			# Timestamp.
			ts = time.time()
			#isodate = datetime.datetime.fromtimestamp(ts, None)
			
			# Feature quartiles.
			q, pq, summ = Feature.getQuartiles(conn, ds['_id'])
			post = {
				"enabled": True, \
				"obo_foundry_terms": ["Abra", "Ca", "Dabra"], \
				"image_alignment_id": str(imal), \
				"overall_hit_count": summ, \
				"overall_hit_quartiles": q, \
				"gene_pooled_hit_quartiles": pq, \
				"created_by_account_id": accid
			}
			coll.update	({'_id': id}, {"$set": post}, upsert=False, multi=False)
		
		coll.update({}, {"$unset": {'alignment_matrix': 1, "chipid": 1, "figure_blue": 1, "figure_red": 1, "figure_status": 1, 'stat_barcodes': 1}}, upsert=False, multi=True)
		coll.ensure_index("name", unique=True)
		


class ImageAlignment(object):
	"""
	Represents an image alignment
	"""
	
	collectionname = "analysis.imagealignment"
	oldlocationname = None	
		
	@staticmethod	
	def createDocument(conn, chipId, figureRed, figureBlue, alignmentMatrix, name):
		coll = conn["analysis"]["imagealignment"]
		
		#ts = time.time()
		#isodate = datetime.datetime.fromtimestamp(ts, None)
		
		post = { "name": name, \
         "chip_id": chipId, \
         "figure_red": figureRed, \
         "figure_blue": figureBlue, \
         "alignment_matrix": alignmentMatrix\
        } \
		
		id_ = coll.insert(post)
		return id_
		
		
	@staticmethod	
	def createIndex(conn):
		coll = conn["analysis"]["imagealignment"]
		coll.ensure_index("name", unique=True)
		coll.ensure_index("chip_id")
		