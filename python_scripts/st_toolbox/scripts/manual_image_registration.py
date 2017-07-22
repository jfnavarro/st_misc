#! /usr/bin/env python
""" This script will show a region of the BORDER and ADDITIONAL_BORDER border
points in a provided NDF Chip design file, and ask the user to relate the
central marked point to a point in an an image in pixel coordinates.

Typing in the coordinate (in the form e.g. 1300, 340) and hitting enter will
relate the printed point to this given pixel point.

To get a new point without registering the previous one (due to e.g. that region
in the image begin occluded by tissue etc.) simply hit enter without typing
anything.

Additionaly, if one is using Fiji to store the registered point in the image as
an ROI list, in stead of typing the point coordinate, type 'a' and hit enter
to accept the point as being in the ROI list.

When registration is done, type 'd' and hit enter to save files and also print
out the registered points.
"""
import argparse
from random import choice

import matplotlib.pyplot as plt
import numpy as np

from st_toolbox.data import load_ndf


def region_limits(ndf, region):
    """ Find upper and lower limits of coordinates in a region of features
    in NDF data.
    """
    return {k: [max(ndf[region][k]),
                min(ndf[region][k])] for k in ndf[region].keys()}


def limit_test(limits, c):
    return (min(limits['x']) <= c[0] <= max(limits['x'])) and \
           (min(limits['y']) <= c[1] <= max(limits['y']))


def get_border_controls(ndf):
    """ Get the control points in an NDF which are conatined inside the border
    areas.
    """
    controls = zip(ndf["NGS_CONTROLS"]['x'], ndf["NGS_CONTROLS"]['y'])

    # The key for the PROPES is different depending on design
    probes_key = filter(lambda k: "PROBES" in k, ndf.keys())[0]

    border_limits = region_limits(ndf, "BORDER")
    probes_limits = region_limits(ndf, probes_key)

    control_within_border = filter(lambda c: limit_test(border_limits, c), controls)
    control_within_probes = filter(lambda c: limit_test(probes_limits, c), controls)

    additional_border_limits = region_limits(ndf, "ADDITIONAL_BORDER")

    control_inside_additional_border = filter(lambda c: limit_test(additional_border_limits, c), controls)

    control_inside_border = (set(control_within_border) - \
                             set(control_within_probes)) | \
                            set(control_inside_additional_border)
    
    return list(control_inside_border)


def main(args):
    ndf = load_ndf(args.ndf_file)
    win_size = 50

    border_x = ndf["BORDER"]["x"] + ndf["ADDITIONAL_BORDER"]["x"]
    border_y = ndf["BORDER"]["y"] + ndf["ADDITIONAL_BORDER"]["y"]

    border_pts = zip(border_x, border_y)

    border = np.zeros((max(border_x) + win_size, max(border_y) + win_size))
    for x, y in border_pts:
        border[x, y] = 1

    border_control_points = get_border_controls(ndf)

    fig = plt.figure()
    ax = fig.add_subplot(111, aspect='equal')
    plt.show(block=False)

    coord_map = {}
    coord_list = []
    i = 0
    while True:
        r_x, r_y = choice(border_control_points)

        section = border[r_x - win_size:r_x + win_size, r_y - win_size:r_y + win_size]
        ns_x, ns_y = section.nonzero()
        s_x = ns_x + r_x - win_size
        s_y = ns_y + r_y - win_size

        ax.scatter(s_x, s_y, c='red', marker='s', edgecolor='none')
        ax.scatter([r_x], [r_y], marker='s', facecolor='none', s=200, edgecolor='blue', lw=1.5)
        ax.set_xlim([r_x - win_size, r_x + win_size])
        ax.set_ylim([r_y + win_size, r_y - win_size])

        plt.draw()

        print(r_x, r_y)

        s = raw_input()

        if s == 'd':
            break

        elif s == 'a':
            i += 1
            coord_list.append((r_x, r_y))
            print('point registered as point {} in list'.format(i))

        elif s == '':
            pass

        else:
            img_x, img_y = map(int, s.split(","))
            coord_map[(img_x, img_y)] = (r_x, r_y)
            print(str((img_x, img_y)) + ' -> ' + str((r_x, r_y)))

        ax.cla()

    print(coord_map)
    print(coord_list)
    with open(args.out_file, 'w') as fh:
        if len(coord_list) > 0:
            fh.write(str(coord_list))
        else:
            fh.write(str(coord_map))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ndf_file", help="NDF Chip design file")
    parser.add_argument("out_file", help="Text file in to which the dict or "
                        "list of registered points will be written.")

    args = parser.parse_args()

    main(args)
