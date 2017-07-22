#! /usr/bin/env python
""" Script for comparing the T content of reads inside and outside a mask.
"""
import argparse
import os

from matplotlib.path import Path
import numpy as np

from st_toolbox.data import json_iterator
from st_toolbox.data import load_id_map

import matplotlib.pyplot as plt

def main(ids_file, mask_file, json_file):
    bc_coord = load_id_map(ids_file)

    mask_polys = np.load(mask_file)
    mask = {}
    for name, polygon in mask_polys.iteritems():
        mask[name] = Path(polygon)

    read = json_iterator(json_file).next()
    readl = len(read["Read"])

    t_hist = {True: np.zeros(readl, dtype=np.int), \
              False: np.zeros(readl, dtype=np.int)}

    reads = json_iterator(json_file)

    mask_list = mask.values()
    p = np.array([0, 0])
    for read in reads:
        p[0], p[1] = bc_coord[read["barcode"]]
        read_class = any([path.contains_point(p) for path in mask_list])
        t_hist[read_class][read["Read"].count("T")] += 1

    plt.subplot(211)
    plt.title("Inside")
    plt.bar(range(readl), t_hist[True])
    plt.xlim([0, readl])
    plt.subplot(212)
    plt.title("Outside")
    plt.xlim([0, readl])
    plt.bar(range(readl), t_hist[False])

    img_file = os.path.basename(json_file).replace(".json", ".T_content.png")

    plt.savefig(img_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ids_file", help="Barcode (id) definition file")
    parser.add_argument("mask_file", help="File with stored mask in .npz format")
    parser.add_argument("json_file", help="JSON-reads file")

    args = parser.parse_args()
    main(args.ids_file, args.mask_file, args.json_file)
