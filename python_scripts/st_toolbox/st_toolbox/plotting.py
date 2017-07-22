#! /usr/bin/env python
""" Module for visualizing data in standardized fashion
"""
import re

import numpy as np

DIVERGING_3 = ["EF8A62", "F7F7F7", "67A9CF"]
DIVERGING_5 = ["CA0020", "F4A582", "F7F7F7", "92C5DE", "0571B0"]


def quality_scatter(data, ax):
    x = np.zeros(len(data))
    y = np.zeros(len(data))

    for i, doc in enumerate(data):
        x[i] = doc["x"]
        y[i] = doc["y"]

    ax.set_axis_bgcolor("#F7F7F7")

    ax.scatter(x, y, c="#0571B0", edgecolor="none",
               alpha=0.33, s=10, label="Expression")


def highlight_scatter(data, regex, ax):
    matched_data = []
    for doc in data:
        m = re.search(regex, doc["Gene"])
        if m:
            matched_data.append(doc)

    x = np.zeros(len(matched_data))
    y = np.zeros(len(matched_data))

    for i, doc in enumerate(matched_data):
        x[i] = doc["x"]
        y[i] = doc["y"]

    ax.scatter(x, y, c="#CA0020", edgecolor="#CA0020",
               alpha=0.5, s=20, label=regex)


def labeled_scatter(data, mask, ax, label):
    ax.set_axis_bgcolor("#F7F7F7")

    label_true_data = []
    label_false_data = []
    for doc in data:
        p = np.array([doc["x"], doc["y"]])
        for path in mask.itervalues():
            if path.contains_point(p):
                label_true_data.append(doc)
                break
        else:
            label_false_data.append(doc)

    x_t = np.zeros(len(label_true_data))
    y_t = np.zeros(len(label_true_data))
    for i, doc in enumerate(label_true_data):
        x_t[i] = doc["x"]
        y_t[i] = doc["y"]

    ax.scatter(x_t, y_t, c="#EF8A62", label=label,
               edgecolor='none', alpha=0.5, s=10)

    x_f = np.zeros(len(label_false_data))
    y_f = np.zeros(len(label_false_data))
    for i, doc in enumerate(label_false_data):
        x_f[i] = doc["x"]
        y_f[i] = doc["y"]

    ax.scatter(x_f, y_f, c="#67A9CF", label="Other",
               edgecolor='none', alpha=0.5, s=10)
