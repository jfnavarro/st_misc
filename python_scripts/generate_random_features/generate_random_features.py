#!/bin/py

# This python script generates a features file that contains random data without any biological sense.
#
# To see the command line parameters
#
# python generate_random_features.py -h

import sys
import random
import argparse
import string

parser = argparse.ArgumentParser(description='Generate a features file in JSON format. It will be printed to stdout.')

parser.add_argument('-g', '--number-of-genes', type=str, help='Number of genes', required=False, default=20)
parser.add_argument('-l', '--gene-name-length', type=str, help='Length of the gene names', required=False, default=10)
parser.add_argument('-d', '--dimension', type=str, help='Dimension of features grid N x N', required=False, default=10)
parser.add_argument('-b', '--barcode-length', type=str, help='length of the barcodes', required=False, default=20)
parser.add_argument('-p', '--percentage-zero-hits', type=str, help='assume gene hit count 0 for percentage of genes', required=False, default=10)
parser.add_argument('-m', '--max-hit-count', type=str, help='maximum allowed hit count', required=False, default=50000)

args = parser.parse_args()

def randomstring(alphabet, length):
     return ''.join(random.choice(alphabet) for i in range(length))

gene_names_set = set()

while len(gene_names_set) < args.number_of_genes:
  gene_name = randomstring(string.lowercase, args.gene_name_length)
  gene_names_set.add(gene_name)

gene_names_list = list(gene_names_set)

sys.stdout.write("[\n")

skip = args.percentage_zero_hits / 100
first_time = True
for x in range(args.dimension):
  for y in range(args.dimension):
    random_barcode = randomstring("ACGT", args.barcode_length)
    gene_nr = 0
    while gene_nr < args.number_of_genes:
      if random.random() > skip:
        if first_time:
          first_time = False
        else:
          sys.stdout.write(",")
        hits = random.randint(1,args.max_hit_count)
        sys.stdout.write("\n {\n    \"y\": %i,\n    \"x\": %i,\n    \"hits\": %i,\n    \"barcode\": \"%s\",\n    \"gene\": \"%s\"\n  }" % (x, y, hits, random_barcode, gene_names_list[gene_nr]))
      gene_nr = gene_nr + 1

sys.stdout.write("\n]\n")

