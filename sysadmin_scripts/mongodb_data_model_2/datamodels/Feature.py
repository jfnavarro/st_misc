#! /usr/bin/env python

import operator
import math

class Feature(object):
	"""
	Represents a feature in the modelling sense -- hits for a
	a specific gene in a specific location.
	"""
	
	collectionname = "feature.<dataset_id>"
	oldlocationname = "feature.<dataset_id>"
		
	
	@staticmethod
	def extendFeatures(conn):
		dscoll = coll = conn["analysis"]["dataset"]
		#collnew = conn["feature"]["feature"]
		l = list(dscoll.find())
		for ds in l:
			id = str(ds["_id"])
			coll = conn["feature"][id]
			coll.update({}, {"$set": {"dataset_id": id, "annotation": ""}}, upsert=False, multi=True)
			#coll.update({}, {"$rename": {"gene": "gene_nomenclature"}}, upsert=False, multi=True)
			#fs = list(coll.find())
			#for f in fs:
			#	collnew.insert(f)
			#coll.drop()
		
		
	@staticmethod
	def getQuartiles(conn, datasetId):
		# This must be invoked prior to the move of the feature organization.
		print "Getting quartiles for " + str(datasetId)
		coll = conn["feature"][str(datasetId)]
		sum = 0
		hits = list()
		pooledHits = dict()
		l = coll.find()
		for item in l:
			gene = str(item["gene"]).upper()
			h = item["hits"]
			sum += h
			hits.append(h)
			if gene in pooledHits:
				pooledHits[gene] += h
			else:
				pooledHits[gene] = h
		hits.sort()
		sortedPooled = sorted(pooledHits.iteritems(), key=operator.itemgetter(1))
		for i in range(len(sortedPooled)):
			sortedPooled[i] = sortedPooled[i][1]
		return (Feature.computeQuartiles(hits), Feature.computeQuartiles(sortedPooled), sum)
		
		
	@staticmethod
	def computeQuartiles(hits):
		if (len(hits) == 0):
			return [-1, -1, -1, -1, -1]
		
		if (len(hits) == 1):
			return [ hits[0], hits[0], hits[0], hits[0], hits[0] ]
		
		q = [-1, -1, -1, -1, -1]
		
		# Linear interpolation for intermediate values, exact at endpoints.
		n = len(hits)
		q[0] = hits[0]
		q[4] = hits[n - 1]
		idx = [ 0.25*n - 0.25,  0.5*n - 0.5,  0.75*n - 0.75 ]
		for i in range(3):
			floor = int(math.floor(idx[i]))
			ceil = int(math.ceil(idx[i]))
			delta = idx[i] - floor;
			q[i + 1] = hits[floor] * (1.0 - delta) + hits[ceil] * delta  # No prob if ceil==floor...
		return q
	