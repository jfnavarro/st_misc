#! /usr/bin/env python
""" Use a lasso selection to label which features will be considered as
under the tissue. This manual version of labeling should be used mostly to
explore various comparisons between points.

Label by drawing with left mouse key.

To select more than one area, hold shift while selecting.

To zoom the scatter plot, scroll.

To pan the scatter plot, hold right mouse key.

To save a labeled JSON file, hit the "s" key when selection is done.

The output file will be stored in the working directory.
"""
import argparse
from collections import Counter
import os

import numpy as np

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayPlotData
from chaco.api import Plot
from chaco.api import LassoOverlay
from chaco.api import ScatterInspectorOverlay
from chaco.tools.api import LassoSelection
from chaco.tools.api import BetterZoom
from chaco.tools.api import PanTool
from chaco.tools.api import ScatterInspector

from st_toolbox.data import json_iterator

from chaco.api import Blues as Map
from chaco.api import DataRange1D


class FeatureLasso(LassoSelection):
    """ A controller for lassoying features and returning all the points
    of the features inside the lasso.
    """
    def _selection_changed_fired(self, event):
        indices = self.selection_datasource.metadata["selection"]
        if any(indices):
            x = np.compress(indices, self.component.index.get_data())
            y = np.compress(indices, self.component.value.get_data())

            inside = set(zip((int(x_) for x_ in x), (int(y_) for y_ in y)))
            print("Marked features: {}".format(len(inside)))

        return

    def normal_key_pressed(self, event):
        if event.character == "s":

            L = self.component.label
            name_list = ["{}_{}".format(L, i) for i in range(len(self.disjoint_selections))]
            kwargs = dict(zip(name_list, self.disjoint_selections))
            np.savez(self.component.out_file, **kwargs)
            print("Saved mask ({} polygons) to {}.npz\
                  ".format(len(self.disjoint_selections), self.component.out_file))

size = (800, 800)
title = "Select features to label"


class FeatureScatter(HasTraits):
    plot = Instance(Component)
    traits_view = View(Group(Item('plot', editor=ComponentEditor(size=size),
                             show_label=False),
                             orientation="vertical"),
                       resizable=True, title=title)

    def __init__(self, data, out_file, label):
        self.data = data
        self.out_file = out_file
        self.label = label

    def _create_plot_component(self):
        """ Creates the plot component of the to be used in the FeatureScatter
            instance.
        """
        x = np.zeros(len(self.data))
        y = np.zeros(len(self.data))
        c = np.zeros(len(self.data))

        for i, (coord, count) in enumerate(self.data.items()):
            x[i], y[i] = coord
            c[i] = count

        c = np.log2(c)

        pd = ArrayPlotData()
        pd.set_data("x", x)
        pd.set_data("y", y)
        pd.set_data("color", c)

        cm = Map(DataRange1D(low=-c.max() / 2, high=c.max()))

        plot = Plot(pd)
        plot.plot(("x", "y", "color"),
                  type="cmap_scatter",
                  name="my_plot",
                  marker="dot",
                  index_sort="ascending",
                  color_mapper=cm,
                  marker_size=2,
                  bgcolor=0xF7F7F7,
                  )

        plot.title = "Scatter Plot With Lasso Selection"
        plot.line_width = 1
        plot.padding = 50

        my_plot = plot.plots["my_plot"][0]
        my_plot.data = self.data
        my_plot.out_file = self.out_file
        my_plot.label = self.label

        lasso_selection = FeatureLasso(component=my_plot,
                                       selection_datasource=my_plot.index,
                                       drag_button="left")

        my_plot.tools.append(lasso_selection)
        my_plot.tools.append(BetterZoom(my_plot, zoom_factor=1.2))
        my_plot.tools.append(PanTool(my_plot, drag_button="right"))
        my_plot.tools.append(ScatterInspector(my_plot))

        lasso_overlay = LassoOverlay(lasso_selection=lasso_selection,
                                     component=my_plot,
                                     selection_fill_color=0xEF8A62)

        my_plot.overlays.append(lasso_overlay)
        my_plot.overlays.append(ScatterInspectorOverlay(my_plot,
                                hover_marker_size=4))

        return plot

    def _plot_default(self):
        plot = self._create_plot_component()

        return plot


def get_observed_feature_coords(json_file):
    """ Get only the coordinates from an ST data json file.
    """
    reads = json_iterator(json_file)
    coords = Counter()
    for doc in reads:
        coords[(doc["x"], doc["y"])] += 1

    return coords


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", help="JSON ST-data file")
    parser.add_argument("out_suffix", help="Suffix for the .npz mask file which \
                        will contain the polygons representing the marked \
                        regions.")
    parser.add_argument("--label", help="Name of label in this classification.",
                        default="Under tissue")

    args = parser.parse_args()

    data = get_observed_feature_coords(args.json_file)

    out_file = os.path.basename(args.json_file).replace(
        ".json", "." + args.out_suffix + "_mask")

    scatter = FeatureScatter(data, out_file, args.label)

    scatter.configure_traits()
