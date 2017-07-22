#! /usr/bin/env python
import datetime
import time

class Account(object):
	"""
	Represents an account
	"""
	
	collectionname = "user.account"
	oldlocationname = "user.account"
	

	@staticmethod	
	def extendAccount(conn):
		coll = conn["user"]["account"]
		
		l = list(coll.find())
		for item in l:
			id = item["_id"]
			username = item["username"]
			email = username + "@scilifelab.se"
			if "." in username:
				parts = username.split(".")
				firstname = parts[0].title()
				lastname = parts[1].title()
				if (len(parts) == 3):
					lastname += " " + parts[2].title()
			else:
				firstname = None
				lastname = None
			#ts = time.time()
			#isodate = datetime.datetime.fromtimestamp(ts, None)
			#print str(isodate)
			coll.update({'_id': id}, {"$set": {'username': email, 'first_name': firstname, 'last_name': lastname, \
											'institution': "SciLifeLab", 'street_address': "Tomtebodavagen 23A", 'city': "Solna", 'postcode': "171 65", \
											'country': "Sweden", 'enabled': "true"}}, upsert=False, multi=False)
		#coll.update({}, {"$unset": {'username': 1}}, upsert=False, multi=True)
		coll.ensure_index("username", unique=True)
		
		
		