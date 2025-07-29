from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsProxyWidget, QSizePolicy

from pyqtgraph import GraphicsLayoutWidget, colormap, LinearRegionItem, mkPen
from pyqtgraph.functions import mkBrush

import numpy as np
import pandas as pd

from .utils.DataUtils import transform_time_grades, transform_triggers
from .nmf_view.ThresholdBox import ThresholdBox
from .nmf_view.MatrixView import MatrixView, pyqtSignal
from .nmf_view.MatrixHighlightView import MatrixHighlightView
from .nmf_view.FeatureMatrixView import FeatureMatrixView, ConstantDateAxisItem


class NMFView(GraphicsLayoutWidget):
    """
    This widget contains the views displaying a specified NMF result and its
    feature matrix and a threshold box, which allows the user to set threshold
    levels for each individual h row using sliders.

    The display results must be set, otherwise random data is displayed.

    Attributes
    ----------
    cellClicked : pyqtSignal(float, str)
        Emits the time and channel of the cursor position after the
        user clicked a cell in the feature matrix.
    min_frame_size : int
        The minimum width/height for each of the four frames.
    rank_factor : int
        The maximum amount of pixels allocated for each rank.
        Used to determine the maximum width/height of the viewboxes for W/H.
    cm : Colormap
        Colormap used to draw the matrices.
    feature_matrix_sampling_frequency : property(int)
        The sampling frequency of the feature matrix.
        Required for setting the correct time axis.

    """

    cellClicked = pyqtSignal(float, str)  # time, channel

    def __init__(self, feature_matrix_sampling_frequency=50):
        super().__init__()

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._fm_sfreq = feature_matrix_sampling_frequency

        # Display parameters
        self.min_frame_size = 210
        self.rank_factor = 30
        self.cm = colormap.get("CET-D1")
        self.setBackground("lightgrey")

        # Tracking triggers and time grades
        self._trigger_regions = []
        self._time_grade_regions = []

        # Setup viewboxes
        #
        # H Viewbox
        row_height = 3
        self._vbh: MatrixView = MatrixHighlightView(
            row_height=row_height, colormap=self.cm
        )
        self._vbh.setMouseEnabled(x=True, y=False)
        self._plot_h = self.addPlot(row=0, col=1, viewBox=self._vbh)
        self._plot_h.showAxis("right")
        self._plot_h.hideAxis("left")
        self._plot_h.hideAxis("bottom")
        self._vbh._connect_scene_events()

        # W Viewbox
        self._vbw: MatrixView = MatrixView(
            enableMouse=False, colormap=self.cm, keep_range=False
        )
        self._plot_w = self.addPlot(row=1, col=0, viewBox=self._vbw)
        self._plot_w.showAxis("bottom")
        self._plot_w.hideAxis("left")
        self._vbw._connect_scene_events()
        self._vbw.cellClicked.connect(self._w_cell_selected)

        # Line length Viewbox
        self._time_axis = ConstantDateAxisItem()
        self._vbfm: FeatureMatrixView = FeatureMatrixView(colormap=self.cm)
        self._plot_fm = self.addPlot(
            row=1,
            col=1,
            viewBox=self._vbfm,
            axisItems={"bottom": self._time_axis},
        )
        self._plot_fm.hideAxis("left")
        self._vbfm.setMouseEnabled(x=True, y=False)
        self._vbfm._connect_scene_events()
        self._vbfm.cellClicked.connect(self._fm_cell_selected)

        # link axis
        self._vbfm.setXLink(self._vbh)
        self._vbfm.setYLink(self._vbw)

        # Fill items with dummy data
        self._rank = 4
        self._time_points = 2000
        self._channels = 112
        self.set_channel_names(["random"] * self._channels)

        self._vbfm.matrix = np.random.normal(size=(self._time_points, self._channels))

        # Add Control box for H thresholds
        self._control_box = ThresholdBox(self._vbh)
        self._proxy = QGraphicsProxyWidget()
        self._proxy.setWidget(self._control_box)
        self._proxy.setContentsMargins(0, 0, 0, 0)
        self.addItem(self._proxy, row=0, col=0)

        # Add items to viewboxes
        self.set_h_matrix(np.random.normal(size=(self._rank, self._time_points)))
        self.set_w_matrix(np.random.normal(size=(self._channels, self._rank)))

        self._update_dimensions()

    @property
    def feature_matrix_sampling_frequency(self):
        return self._fm_sfreq

    @feature_matrix_sampling_frequency.setter
    def feature_matrix_sampling_frequency(self, value: int):
        self._fm_freq = value

    def set_h_matrix(self, data: np.ndarray) -> None:
        data = data.T
        self._time_points, self._rank = data.shape

        self._update_dimensions()
        self._vbh.matrix = data

        # Configure ticks such that minorticks show the value of
        # the current row and majorticks designate the row border
        row_heigth = self._vbh.row_height
        majorticks = [(i * row_heigth, "") for i in range(self._rank + 1)]
        minorticks = [((i + 0.5) * row_heigth, f"{i+1:.0f}") for i in range(self._rank)]
        axis = self._plot_h.getAxis("right")
        axis.setTicks([majorticks, minorticks])

    def h_matrix(self) -> np.ndarray:
        return self._vbh.matrix.T

    def set_w_matrix(self, data: np.ndarray) -> None:
        data = data.T
        self._rank, self._channels = data.shape
        self._vbw.matrix = data

        # Configure ticks such that minorticks show the value of
        # the current column and majorticks designate the column border
        majorticks = [(i, "") for i in range(self._rank + 1)]
        minorticks = [(i + 0.5, f"{i+1:.0f}") for i in range(self._rank)]
        axis = self._plot_w.getAxis("bottom")
        axis.setTicks([majorticks, minorticks])

    def w_matrix(self) -> np.ndarray:
        return self._vbw.matrix.T

    def set_feature_matrix(
        self, data: np.ndarray, start_timestamp=0, autoLevels=True
    ) -> None:
        self._time_axis.start_timestamp = start_timestamp
        self._time_axis.sfreq = self.feature_matrix_sampling_frequency
        self._vbfm.autoLevels = autoLevels
        self._vbfm.matrix = data.T

    def feature_matrix(self) -> np.ndarray:
        return self._vbfm.matrix.T

    def set_channel_names(self, channel_names: list) -> None:
        self._channel_names = channel_names
        self._vbfm.channel_names = channel_names

    def set_time_grades(self, df: pd.DataFrame) -> None:
        df = transform_time_grades(df, self.feature_matrix_sampling_frequency)
        for _index, row in df[df["Description"].str.startswith("IED")].iterrows():
            start = row["Onset"]
            stop = start + row["Duration"]
            self._paint_region(
                start=start,
                stop=stop,
                brush_color=QColor(25, 237, 0, 10),
                pen_color=QColor(25, 237, 0, 80),
                region_list=self._time_grade_regions,
            )

        for _index, row in df[df["Description"] == "NOISY"].iterrows():
            start = row["Onset"]
            stop = start + row["Duration"]
            self._paint_region(
                start=start, stop=stop, region_list=self._time_grade_regions
            )

    def set_triggers(self, triggers: np.ndarray) -> None:
        triggers = transform_triggers(triggers, self.feature_matrix_sampling_frequency)
        for start, stop in triggers:
            self._paint_region(
                start=start, stop=stop, region_list=self._trigger_regions
            )

    def show_value(self, visible: bool = True) -> None:
        self._vbfm.show_value = visible
        self._vbh.show_value = visible
        self._vbw.show_value = visible
        self.repaint()

    def show_crosshair(self, visible: bool = True) -> None:
        self._vbfm.show_crosshair = visible
        self._vbh.show_crosshair = visible
        self._vbw.show_crosshair = visible
        self.repaint()

    def show_channel_info(self, visible: bool = True) -> None:
        self._vbfm.show_info = visible
        self.repaint()

    def show_time_grades(self, visible: bool = True) -> None:
        for region in self._time_grade_regions:
            region.setVisible(visible)

    def show_triggers(self, visible: bool = True) -> None:
        for region in self._trigger_regions:
            region.setVisible(visible)

    def clear_time_grades(self) -> None:
        for region in self._time_grade_regions:
            self._remove_region(region)
        self._time_grade_regions.clear()

    def clear_triggers(self) -> None:
        for region in self._trigger_regions:
            self._remove_region(region)
        self._trigger_regions.clear()

    def move_forward(self, percentage=0.2) -> None:
        self._vbh.move_forward(percentage)

    def move_backward(self, percentage=0.2) -> None:
        self._vbh.move_backward(percentage)

    def _update_dimensions(self) -> None:
        new_max = max(self.min_frame_size, self._rank * self.rank_factor)

        # Set max width on W and max height on H
        self._plot_w.setMaximumWidth(new_max)
        self._plot_h.setMaximumHeight(new_max)

        self._vbw.setMaximumWidth(new_max)
        self._vbh.setMaximumHeight(new_max)

        # adjust the graphics proxy accordingly
        self._proxy.setMaximumWidth(new_max)
        self._proxy.setMaximumHeight(new_max)

    def _paint_region(
        self,
        start,
        stop,
        brush_color=QColor(255, 255, 255, 10),
        pen_color=(255, 255, 255, 80),
        region_list=[],
    ) -> None:
        brush = mkBrush(brush_color)
        pen = mkPen(pen_color, width=10)

        h_region = LinearRegionItem((start, stop), movable=False, brush=brush, pen=pen)
        fm_region = LinearRegionItem((start, stop), movable=False, brush=brush, pen=pen)

        self._plot_h.addItem(h_region)
        self._plot_fm.addItem(fm_region)

        region_list.append(h_region)
        region_list.append(fm_region)

    def _remove_region(self, region) -> None:
        self._plot_h.removeItem(region)
        self._plot_fm.removeItem(region)

    def _w_cell_selected(self, x, y) -> None:
        # Move view to center the highest value of the line length matrix
        # for which the w value multiplied with the corresponding h value contribute the most

        # e. g. w_ij was selected: find max x: h_xi * w_ij + C = ll_xi, ll_xi large, C small
        # as in h_xi * w_ij contribute the most to ll_xi

        # channel = i, h_row, w_col = j
        h_row = self._vbh.matrix[:, x]
        ll_row = self._vbfm.matrix[:, y]
        w_val = self._vbw.matrix[x, y]

        # get 100 largest ll_row values
        ll_desc_index = np.flip(np.argsort(ll_row))[:100]

        # on the difference between w*h and ll, chose those corresponding to large ll values
        candidates = np.abs((ll_row - w_val * h_row)[ll_desc_index])

        # the smaller the value, the larger the importance of w and h: chose smallest value as candidate
        candidate_index = np.argsort(candidates)[0]

        # remap onto index for coordinate
        x = ll_desc_index[candidate_index]

        # candidate_index = np.argmax(self.vbll.matrix[:, y])
        self._vbfm.center_x(x)

    def _fm_cell_selected(self, x, y) -> None:
        time = x / self.feature_matrix_sampling_frequency
        channel = self._channel_names[y]
        self.cellClicked.emit(time, channel)
