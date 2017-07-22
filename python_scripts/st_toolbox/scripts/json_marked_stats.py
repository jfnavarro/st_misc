#! /usr/bin/env python
""" Script for creating statistics and summary plots from a JSON ST-data file
and a mask .npz file which discriminates features.
"""
import argparse
from collections import defaultdict
import os

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.path import Path
import numpy as np

from st_toolbox.data import load_json
from st_toolbox.plotting import labeled_scatter


def main(json_file, mask_file):
    assert json_file.endswith("json"), "Incorrect file ending."
    assert mask_file.endswith("npz"), "Incorrect file ending."

    img_file = os.path.basename(json_file).replace(".json", ".png")

    data = load_json(json_file)
    mask_polys = np.load(mask_file)

    mask = {}
    for name, polygon in mask_polys.iteritems():
        mask[name] = Path(polygon)

    fig = plt.figure()
    ax = fig.add_subplot(111, aspect='equal')

    label = name[:-2]
    labeled_scatter(data, mask, ax, label)

    ax.invert_yaxis()
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.legend()
    ax.set_title("Feature classification", size=20)

    fig.set_size_inches(10, 8)
    fig.savefig(img_file)

    all_features = defaultdict(int)
    true_features = defaultdict(int)
    all_transcripts = defaultdict(int)
    true_transcripts = defaultdict(int)

    for doc in data:
        seq = doc["Seq"]
        all_features[seq] += 1
        all_transcripts[seq] += doc["Nr"]
        p = np.array([doc["x"], doc["y"]])
        for path in mask.itervalues():
            if path.contains_point(p):
                true_features[seq] += 1
                true_transcripts[seq] += doc["Nr"]

    sum_all_features = sum(all_features.itervalues())
    sum_true_features = sum(true_features.itervalues())

    stat_dict = {"true_features": sum_true_features}
    stat_dict["tfp"] = float(sum_true_features) / sum_all_features

    stat_dict["false_features"] = sum_all_features - sum_true_features
    stat_dict["ffp"] = float(stat_dict["false_features"]) / sum_all_features

    sum_all_transcripts = sum(all_transcripts.itervalues())
    stat_dict["true_transcripts"] = sum(true_transcripts.itervalues())
    stat_dict["ttp"] = float(stat_dict["true_transcripts"]) / sum_all_transcripts

    stat_dict["false_transcripts"] = sum_all_transcripts - stat_dict["true_transcripts"]
    stat_dict["ftp"] = float(stat_dict["false_transcripts"]) / sum_all_transcripts

    stat_string = """
    Statistics:
    -----------
    Features under tissue:   {true_features} ({tfp:.0%})
    Features outside tissue: {false_features} ({ffp:.0%})

    Transcripts (reads) under tissue:   {true_transcripts} ({ttp:.0%})
    Transcripts (reads) outside tissue: {false_transcripts} ({ftp:.0%})
    """

    print(stat_string.format(**stat_dict))

    stat_file = img_file.replace(".png", ".stats.txt")
    with open(stat_file, "w") as fh:
        fh.write(stat_string.format(**stat_dict))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", help="JSON ST-data file")
    parser.add_argument("mask_file", help="File with stored mask in .npz format")

    args = parser.parse_args()

    main(args.json_file, args.mask_file)
