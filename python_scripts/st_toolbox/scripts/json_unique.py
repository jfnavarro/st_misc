#! /usr/bin/env python
""" Script for creating a JSON file with the unique events in a given JSON
file compared to a given list of JSON files. E.g. to compare one hiseq lane
to all the other lanes.
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
    seen = set([])
    for f in args.complement_files:
        it = json_iterator(f)
        for doc in it:
            feature_gene = (doc['y'], doc['x'], doc['gene'], doc['barcode'])
            seen.add(feature_gene)

    with open(args.out, 'w') as out_file:
        it = json_iterator(args.json_file)
        for doc in it:
            feature_gene = (doc['y'], doc['x'], doc['gene'], doc['barcode'])
            if feature_gene not in seen:
                serial_doc = serialize(feature_gene, doc['hits'])
                out_file.write('{}\n'.format(serial_doc))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('json_file', type=str, help='First JSON file')
    parser.add_argument('--complement_files', nargs='+', type=str,
                        help='Space seperated list of json ST files to compare '
                             'the first file with.')
    parser.add_argument('-o', '--out', type=str, help='Name of output file')

    args = parser.parse_args()
    main(args)
