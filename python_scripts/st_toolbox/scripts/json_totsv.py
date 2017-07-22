#!/usr/bin/env python

#Author: Mauricio Barrientos
#Date: May 15th,2013
#Description: Tool to extract fields of interest from a JSON database file generated from the pipeline
#             in a tab-separated format, for easy UNIX-command line processing.

import sys
import cjson
import argparse

def main(args):
	inputStream = sys.stdin
	outputStream = sys.stdout
	
	field_separator = args.sep
	#Change input and output streams if required
	if args.file:
		try: 
			inputStream = open(args.file,"r")
		except Exception:
			sys.stderr.write("File "+args.file+" could not be read") 
			sys.exit(1)

	if args.output:
		try: 
			outputStream = open(args.output,"w")
		except Exception:
			sys.stderr.write("File "+args.output+" could not be opened for writing") 
			sys.exit(1)

	#Extract columns
	columns = [ x.strip() for x in args.fields.split(",") ]
	if args.header:
		"\t".join(columns)+"\n"

	for line in inputStream:
		doc = cjson.decode(line)
		itemList = []
		for field in columns:
			itemList.append(str(doc[field]))
		outputStream.write(field_separator.join(itemList)+"\n")
	outputStream.close()

if __name__ == '__main__':
	#Process command line arguments
	parser = argparse.ArgumentParser(description=
		"""Extracts the selected fields from the JSONdb file and returns the values in a tab-separated file
			The command line utility reads input from STDIN and writes to STDOUT by default, but -f and -o 
			options can be specified to read/write from/to a file respectively

			Fields to extract must be specified comma-separated with no spaces in between. 

			A typical example would be the following: Extract the gene and position in chip from the barcodes.json file.

			json_totsv.py x,y,gene -f barcodes.json

			It is possible to pipe input and output to other utilities. Fore example, to a list all unique events ifor mitochondrial genes from a barcodes.json file
			
			cat barcodes.json | grep "MT_" | json_totsv.py x,y,gene | sort | uniq 
		"""
		)
	parser.add_argument("fields",help="Comma-separated names of the fields that will be extracted from the jsondb")
	parser.add_argument("-H","--header",action="store_true", help="Add column headers to output")
	parser.add_argument("-s","--sep",default="\t",metavar="char", help="Field separator. Default is tab-character")
	parser.add_argument("-f","--file",help="Read input from a JSONdb file",metavar="JSONdb")
	parser.add_argument("-o","--output",help="Write output to file")
	
	args = parser.parse_args()
	
	main( args )
