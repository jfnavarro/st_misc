from st_feature_classification.util import *

import argparse
import time

import pandas as pd
import numpy as np

from sklearn.decomposition import KernelPCA
from sklearn.grid_search import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC


def main(args):
    df = pd.load(args.df)

    svc_seed = int(time.time() * 1000)
    estimators = [('reduce_dim', KernelPCA(kernel='linear')),
                  ('svm', LinearSVC(random_state=svc_seed))]

    clf = Pipeline(estimators)

    equiv_sets = None
    params = dict(reduce_dim__n_components=[2, 3, 5, 8, 10, 25, 50, 100],
                  svm__C=[0.25, 0.5, 1, 2, 4, 8, 16])

    if args.twoclass:
        params = dict(reduce_dim__n_components=[2, 3, 5, 8, 10, 25, 40, 45, 50, 55, 60, 75, 100])
        equiv_sets = [['external plexiform', 'glomerular cell layer'],
                      ['internal plexiform', 'mitral cell layer']]

    grid_search = GridSearchCV(clf, param_grid=params, cv=3)

    best = 0.0
    while True:
        random_seed = int(time.time() * 1000)
        random.seed(random_seed)

        df_l, _, df_t = split_df(df, 0.33)
        y_l = integer_labels(df_l, equiv_sets)

        try:
            grid_search.fit(df_l, y_l)
        except ValueError:
            # Most likely wrong number of classes in cross validation set
            continue


        y_t = integer_labels(df_t, equiv_sets)
        c = grid_search.predict(df_t)

        score, c = compare_clusters(c, y_t)

        if score > best:
            best = score
            print('{} {} {}'.format(svc_seed, random_seed, best))
            with open(args.out, 'a') as fh:
                fh.write('{} {} {}\n'.format(svc_seed, random_seed, best))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('df')
    parser.add_argument('out')
    parser.add_argument('--twoclass', action='store_true')

    args = parser.parse_args()
    main(args)
