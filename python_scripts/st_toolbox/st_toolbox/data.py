#! /usr/bin/env python
""" Module for parsing and dealing with ST data formats.
"""
from collections import defaultdict
from collections import namedtuple
import csv
import json

import numpy as np
from matplotlib.path import Path

import cjson


def readfq(fp):  # this is a generator function
    """ Heng Li's fasta/fastq reader function.
    """
    last = None  # this is a buffer keeping the last unprocessed line
    while True:  # mimic closure; is it a bad idea?
        if not last:  # the first record or a record following a fastq
            for l in fp:  # search for the start of the next record
                if l[0] in '>@':  # fasta/q header line
                    last = l[:-1]  # save this line
                    break
        if not last:
            break
        name, seqs, last = last[1:].partition(" ")[0], [], None
        for l in fp:  # read the sequence
            if l[0] in '@+>':
                last = l[:-1]
                break
            seqs.append(l[:-1])
        if not last or last[0] != '+':  # this is a fasta record
            yield name, ''.join(seqs), None  # yield a fasta record
            if not last:
                break
        else:  # this is a fastq record
            seq, leng, seqs = ''.join(seqs), 0, []
            for l in fp:  # read the quality
                seqs.append(l[:-1])
                leng += len(l) - 1
                if leng >= len(seq):  # have read enough quality
                    last = None
                    yield name, seq, ''.join(seqs)  # yield a fastq record
                    break
            if last:  # reach EOF before reading enough quality
                yield name, seq, None  # yield a fasta record instead
                break


def json_iterator(json_file):
    """ Iterator over lines in an ST json file.
    """
    with open(json_file) as fh:
        for line in fh:
            yield cjson.decode(line)


def save_json(data, json_file):
    """ Save data in ST json format.
    """
    with open(json_file, "w") as fh:
        for datum in data:
            fh.write(json.dumps(datum) + "\n")


def load_id_map(id_file):
    """ Load a ids file in to a barcode -> coordinate dictionary.
    """
    id_map = {}
    with open(id_file, "r") as fh:
        for line in fh:
            bc, x, y = line.split("\t")
            id_map[bc] = (int(x), int(y))

    return id_map


def load_json(json_file):
    """ Load a json file with e.g. expression data.
    """
    data = []
    with open(json_file) as fh:
        for line in fh.readlines():
            data.append(cjson.decode(line))

    return data


def load_ndf(ndf_file):
    """ Load all points from an ndf file to a dictionary of the types of points.
    """
    fh = open(ndf_file, 'r')
    ndf_reader = csv.reader(fh, delimiter='\t')
    header = ndf_reader.next()
    DesignRow = namedtuple('DesignRow', header)

    features = defaultdict(lambda: {"x": [], "y": []})

    for row in ndf_reader:
        d_row = DesignRow(*row)
        features[d_row.CONTAINER]["x"].append(int(d_row.X))
        features[d_row.CONTAINER]["y"].append(int(d_row.Y))

    fh.close()

    return features


def get_limits(data):
    """ Get the x, y ranges of the ST data.
    """
    y_min = 1e6
    y_max = -1e6
    x_min = 1e6
    x_max = -1e6

    for doc in data:
        x = doc["x"]
        y = doc["y"]
        y_min = y if y < y_min else y_min
        y_max = y if y > y_max else y_max
        x_min = x if x < x_min else x_min
        x_max = x if x > x_max else x_max

    return x_min, x_max, y_min, y_max


def load_mask(mask_file):
    """ Load .npz polygon mask file in to a dictionary of Path's that can
    be used to check for point membership efficiently.
    """
    mask_polys = np.load(mask_file)
    mask = {}
    for name, polygon in mask_polys.iteritems():
        mask[name] = Path(polygon)

    return mask


def count_str_in_read(read_data, string, id_map):
    """ Count occuerances of a string in a read.
    """
    x = np.zeros(len(read_data))
    y = np.zeros_like(x)
    c = np.zeros_like(x)

    for i, doc in enumerate(read_data):
        x[i], y[i] = id_map[doc["barcode"]]
        c[i] = doc["Read"].count(string)
