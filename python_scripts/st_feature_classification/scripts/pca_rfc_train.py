from st_feature_classification.util import *

import argparse
import time

import pandas as pd
import numpy as np

from sklearn.decomposition import KernelPCA
from sklearn.grid_search import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier


def main(args):
    df = pd.load(args.df)

    rfc_seed = int(time.time() * 1000)
    estimators = [('reduce_dim', KernelPCA(kernel='linear')),
                  ('rfc', RandomForestClassifier(32, random_state=rfc_seed))]

    clf = Pipeline(estimators)

    params = dict(reduce_dim__n_components=[2, 3, 5, 8, 10, 25, 50, 100])

    grid_search = GridSearchCV(clf, param_grid=params, cv=3)

    best = 0.0
    while True:
        random_seed = int(time.time() * 1000)
        random.seed(random_seed)

        df_l, y_l, df_t = split_df(df, 0.33)

        try:
            grid_search.fit(df_l, y_l)
        except ValueError:
            # Most likely wrong number of classes in cross validation set
            continue


        y_t = integer_labels(df_t)
        c = grid_search.predict(df_t)

        score, c = compare_clusters(c, y_t)

        if score > best:
            best = score
            print('{} {} {}'.format(rfc_seed, random_seed, best))
            with open(args.out, 'a') as fh:
                fh.write('{} {} {}\n'.format(rfc_seed, random_seed, best))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('df')
    parser.add_argument('out')

    args = parser.parse_args()
    main(args)
