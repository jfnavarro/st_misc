#! /usr/bin/env python
""" Useful things for feature classifications
"""
from collections import Counter
from itertools import permutations
import random

import numpy as np
from pymongo import Connection
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm


def merge(x, i):
    return (x / i) * i + i / 2 + 1


def load_tissue_df(coll, merge_dist=1):
    records = {}
    tissue_labels = {}
    if merge_dist <= 1:
        merger = lambda x: x
    else:
        merger = lambda x: merge(x, merge_dist)

    for doc in coll.find():
        loc = tuple(map(merger, doc['loc']))
        if loc in records:
            records[loc] += Counter(dict(zip(doc['genes'], doc['expression'])))
        else:
            records[loc] = Counter(dict(zip(doc['genes'], doc['expression'])))
            tissue_labels[loc] = doc['tissue']
    
    df = pd.DataFrame.from_records(records.values())
    df.index = pd.MultiIndex.from_tuples(zip(tissue_labels.values(), tissue_labels.keys()), names=['tissue', 'feature'])
    
    return df


def feature_class_visualizer(coll):
    feature_labels = {}
    for doc in coll.find():
        feature_labels[tuple(doc['loc'])] = hash(doc['tissue'])

    def vis_feature_classes(df, c, s=100):
        plt.scatter(*zip(*feature_labels.keys()), c=feature_labels.values(), marker=',', edgecolor='none', cmap=cm.Dark2_r, alpha=0.5);
        plt.scatter(*zip(*[i[1] for i in df.index]), c=c, edgecolor='none', s=s, cmap=cm.gist_rainbow, marker='s', alpha=0.66)
        
        plt.ylim(450, 180)
        plt.xlim(90, 370);
        plt.axis('off');

    return vis_feature_classes


def integer_labels(df, equivalence_classes=None):
    n2i = {n: i for i, n in enumerate(df.index.levels[0])}
    
    if equivalence_classes:
        for e_class in equivalence_classes:
            label = min(n2i[e] for e in e_class)
            for e in e_class:
                n2i[e] = label
        
        relabel = {i[1]: i[0] for i in enumerate(set(n2i.values()))}
        for name in n2i.keys():
            n2i[name] = relabel[n2i[name]]
    
    y = [n2i[i[0]] for i in df.index]
    
    return np.array(y)


def compare_clusters(clusters, truth):
    max_similarity = 0
    for p in permutations(set(truth)):
        pc = np.array(map(lambda i: p[i], clusters))
        similarity = (pc == truth).sum()
        if similarity > max_similarity:
            max_similarity = similarity
            mpc = pc
    
    return float(max_similarity) / len(clusters), mpc


def weighted_choice(choices):
   total = sum(w for c, w in choices)
   r = random.uniform(0, total)
   upto = 0
   for c, w in choices:
      if upto + w > r:
         return c
      upto += w
   assert False, "Shouldn't get here"


def weighted_random_classes(y, choices):
    return np.array([weighted_choice(choices) for _ in range(len(y))])


def weighted_random_score(y):
    choices = Counter(y).items()
    score = []
    for i in range(128):
        c = weighted_random_classes(y, choices)
        score.append(compare_clusters(c, y)[0])

    return np.mean(score)


def split_df(df, r=0.25):
    rows = pd.MultiIndex.from_tuples(random.sample(df.index, int(df.shape[0] * r)))
    df_train = df.ix[rows]
    df_test = df.drop(rows)
    y_train = integer_labels(df_train)

    return df_train, y_train, df_test


def load_reads_per_feature(csv_file):
    reads = np.zeros((500, 500))
    for line in open(csv_file):
        l = line.strip().split(" ")
        x, y = map(int, l[-1].split())
        reads[y, x] = int(l[0])

    return reads


def merged_reads_per_feature(reads_matrix, size):
    merged_reads = np.zeros((600, 600))
    for i in range(500):
        for j in range(500):
            merged_reads[merge(j, size), merge(i, size)] += reads_matrix[i, j]

    return merged_reads
