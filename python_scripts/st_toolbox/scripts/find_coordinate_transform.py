""" Finds a transformation between image and array coordinate systems from a
file with mapping between points stored a python dictionary.
"""
import argparse
import ast
import os

import numpy as np
from skimage import transform


def main(args):
    if args.roi:
        with open(args.point_map) as fh:
            point_list = ast.literal_eval(fh.read())

        with open(args.roi) as fh:
            fh.next()
            coords = {}
            for i, line in enumerate(fh):
                row = line.split('\t')
                coords[(int(row[3]), int(row[4]))] = point_list[i]

    else:
        with open(args.point_map) as fh:
            coords = ast.literal_eval(fh.read())

    src = np.array(coords.keys())
    dst = np.array(coords.values())

    sim_tf = transform.SimilarityTransform()
    sim_tf.estimate(src, dst)

    # Enhance transformation fit by removing points which are likely
    # wrongly registered.
    dst_proj = sim_tf(src)

    norm_dst_proj = (dst_proj - dst_proj.mean(0)) / dst_proj.mean()
    norm_dst = (dst - dst.mean(0)) / dst.mean()
    match = np.sum((norm_dst_proj - norm_dst) ** 2, -1) ** 0.5

    outlier_limit = match.mean() + 3 * match.std()
    dst_fil = dst[match < outlier_limit]
    src_fil = src[match < outlier_limit]

    sim_tf.estimate(src_fil, dst_fil)

    if args.point_map.endswith('.txt'):
        out_file = os.path.basename(args.point_map).replace('.txt', '_transform.npy')
        print('Transformation matrix (pixels -> features):')
        print(sim_tf._matrix)
        print('(saved to file)')
        np.save(out_file, sim_tf._matrix)
        print('Inverted Transformation matrix (features -> pixels):')
        print(np.linalg.inv(sim_tf._matrix))
    else:
        print('Unexpected input file ending, printing matrix to std_out:\n')
        print(sim_tf._matrix)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("point_map", help="File with coordinate map dictionary, "
                                          "Must be a .txt file!")
    parser.add_argument("-r", "--roi", help="Use Fiji ROI mode, provide a ROI "
                                            "list xls file as argument.")

    args = parser.parse_args()

    main(args)
