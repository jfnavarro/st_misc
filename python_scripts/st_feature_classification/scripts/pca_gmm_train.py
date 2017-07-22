from st_feature_classification.util import *

import argparse
from itertools import permutations
import time

import pandas as pd
import numpy as np

from sklearn.mixture import GMM
from sklearn.decomposition import KernelPCA


def main(args):
    df = pd.load(args.df)
    y = integer_labels(df)

    pca = KernelPCA(None, kernel=args.kernel)
    pca.fit(df)
    X = pca.transform(df)

    nonzero_components = X.shape[1]

    seed = int(time.time() * 1000)

    gmm = GMM(4, n_init=10, random_state=seed)
    gmm.fit(X)
    c = gmm.predict(X)

    score, _ = compare_clusters(c, y)

    best = score

    with open(args.out, 'w') as fh:
        fh.write('{} {} {} {}\n'.format(args.kernel, nonzero_components, seed, best))

    n_comps = range(2, 16) + [int(i) for i in np.linspace(16, nonzero_components, 20)]

    for n in n_comps:
        pca = KernelPCA(n, kernel=args.kernel)
        pca.fit(df)
        X = pca.transform(df)

        for i in range(128):
            seed = int(time.time() * 1000)

            gmm = GMM(4, random_state=seed)
            gmm.fit(df)
            c = gmm.predict(df)

            score, _ = compare_clusters(c, y)
            if score > best:
                best = score
                with open(args.out, 'a'):
                    fh.write('{} {} {} {}\n'.format(args.kernel, n, seed, best))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('df')
    parser.add_argument('kernel')
    parser.add_argument('out')


    args = parser.parse_args()
    main(args)

