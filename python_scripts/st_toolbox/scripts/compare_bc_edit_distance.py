#! /usr/bin/env python
""" Script for comparing the Levenshtein edit distance between sequence and
matched barcodes inside and outside a mask.
"""
import argparse
from collections import Counter
import os

from Levenshtein import distance
from matplotlib.path import Path
import matplotlib.pyplot as plt
import numpy as np

from st_toolbox.data import json_iterator
from st_toolbox.data import load_id_map
from st_toolbox.data import load_mask


def main(ids_file, mask_file, json_file):
    bc_coord = load_id_map(ids_file)
    mask = load_mask(mask_file)
    reads = json_iterator(json_file)

    dist_hist = {True: Counter(), False: Counter()}

    mask_list = mask.values()
    p = np.zeros(2)
    for read in reads:
        bc = read["barcode"]
        p[0], p[1] = bc_coord[read["barcode"]]
        read_class = any([path.contains_point(p) for path in mask_list])
        dist_hist[read_class][distance(bc, read["Read"][:27])] += 1

    title = "Edit distance between sequence and matched barcode\n"
    plt.subplot(211)
    plt.title(title + "Inside")
    plt.bar(dist_hist[True].keys(), dist_hist[True].values())
    plt.subplot(212)
    plt.title(title + "Outside")
    plt.bar(dist_hist[False].keys(), dist_hist[False].values())

    img_file = os.path.basename(json_file).replace(".json", ".bc_distance.png")

    plt.tight_layout()
    plt.savefig(img_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ids_file", help="Barcode (id) definition file")
    parser.add_argument("mask_file", help="File with stored mask in .npz format")
    parser.add_argument("json_file", help="JSON-reads file")

    args = parser.parse_args()
    main(args.ids_file, args.mask_file, args.json_file)
