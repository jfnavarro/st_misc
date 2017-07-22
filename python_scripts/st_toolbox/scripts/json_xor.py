#! /usr/bin/env python
""" Script for creating the symmetric difference (XOR) of two JSON files
in terms of Unique Events.
"""
import argparse
import cjson

from st_toolbox.data import json_iterator


def serialize(feature_gene, hits):
    doc = {}
    doc['y'], doc['x'], doc['gene'], doc['barcode'] = feature_gene
    doc['hits'] = hits
    return cjson.encode(doc)


def main(args):
    hits = {}

    it = json_iterator(args.json_file_1)
    for doc in it:
        feature_gene = (doc['y'], doc['x'], doc['gene'], doc['barcode'])
        hits[feature_gene] = doc['hits']

    it = json_iterator(args.json_file_2)
    for doc in it:
        feature_gene = (doc['y'], doc['x'], doc['gene'], doc['barcode'])
        if feature_gene in hits:
            hits.pop(feature_gene)
        else:
            hits[feature_gene] = doc['hits']

    with open(args.out, 'w') as out_file:
        for k, v in hits.iteritems():
            out_file.write('{}\n'.format(serialize(k, v)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('json_file_1', type=str, help='First JSON file')
    parser.add_argument('json_file_2', type=str, help='Second JSON file')
    parser.add_argument('-o', '--out', type=str, help='Name of output file')

    args = parser.parse_args()
    main(args)
