#! /usr/bin/env python
""" Graphically view an NCF chip design file
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
from chaco.api import ScatterInspectorOverlay
from chaco.tools.api import BetterZoom
from chaco.tools.api import PanTool
from chaco.tools.api import ScatterInspector

from st_toolbox.data import load_ndf

from chaco.api import Blues as Map
from chaco.api import DataRange1D

size = (800, 800)
title = "NCF"


class FeatureScatter(HasTraits):
    plot = Instance(Component)
    traits_view = View(
                    Group(
                        Item('plot', editor=ComponentEditor(size=size),
                             show_label=False),
                        orientation="vertical"),
                    resizable=True, title=title)

    def __init__(self, ncf_file):
        self.features = load_ndf(ncf_file)

    def _create_plot_component(self):
        """ Creates the plot component of the to be used in the FeatureScatter
            instance.
        """
        feature_types = self.features.keys()

        print(feature_types)

        x = np.array(self.features["BORDER"]["x"] + self.features["ADDITIONAL_BORDER"]["x"])
        y = np.array(self.features["BORDER"]["y"] + self.features["ADDITIONAL_BORDER"]["y"])

        pd = ArrayPlotData()
        pd.set_data("x", x)
        pd.set_data("y", y)

        plot = Plot(pd)
        plot.plot(("x", "y"),
                  type="scatter",
                  name="my_plot",
                  color="red",
                  index_sort="ascending",
                  marker_size=2.0,
                  bgcolor="black",
                  line_width=0,
                  )

        my_plot = plot.plots["my_plot"][0]

        my_plot.tools.append(BetterZoom(my_plot, zoom_factor=1.2))
        my_plot.tools.append(PanTool(my_plot, drag_button="right"))
        my_plot.tools.append(ScatterInspector(my_plot))

        my_plot.overlays.append(ScatterInspectorOverlay(my_plot,
                                hover_marker_size=4))

        return plot

    def _plot_default(self):
        plot = self._create_plot_component()

        return plot


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ncf_file", help="NCF Chip design file")

    args = parser.parse_args()

    scatter = FeatureScatter(args.ncf_file)

    scatter.configure_traits()
