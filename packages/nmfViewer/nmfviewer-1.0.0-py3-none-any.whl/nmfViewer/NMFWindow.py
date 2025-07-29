from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QWidget,
    QWidget,
)

import numpy as np

from spidet.utils.h5_utils import detect_triggers

from .utils.FileUtils import load_time_grades
from .NMFView import NMFView
from .controls.NMFTreeView import NMFFeatureMatrixItem, NMFModelItem
from .controls.Tabs import Tabs


class NMFWindow(QWidget):
    """
    A self contained window offering all features of the NMF Viewer.
    Can be included in a PyQt application like any other widget.

    Attributes
    ----------
    timeClicked : pyqtSignal(int, str)
        Emits (row, channel) corresponding to mouse position.
        Emitted when the user clicked on a cell in the feature matrix.


    """

    timeClicked = pyqtSignal(int, str)  # time, channel

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.start_time = 0
        self.nmf_view = NMFView()
        self.nmf_view.cellClicked.connect(self._on_cell_clicked)
        self.tabs = Tabs()
        self.feature_matrix_group = None

        controls_tab = self.tabs.controls_widget
        controls_tab.featureMatrixChanged.connect(self._on_feature_matrix_selected)
        controls_tab.nmfModelChanged.connect(self._on_nmf_model_selected)
        controls_tab.show_value.connect(self._on_show_value_checked)
        controls_tab.show_crosshair.connect(self._on_show_crosshair_checked)
        controls_tab.show_channel_info.connect(self._on_show_channel_info_checked)

        evaluation_tab = self.tabs.evaluation_widget
        evaluation_tab.newTriggersPath.connect(self._on_new_triggers_path)
        evaluation_tab.newTimeGradePath.connect(self._on_new_time_grade_path)
        evaluation_tab.clearTriggers.connect(self.nmf_view.clear_triggers)
        evaluation_tab.clearTimeGrades.connect(self.nmf_view.clear_time_grades)
        evaluation_tab.showTimeGrades.connect(self.nmf_view.show_time_grades)
        evaluation_tab.showTriggers.connect(self.nmf_view.show_triggers)
        evaluation_tab.showVPrime.connect(self._on_show_v_prime)

        self._init_ui()

    def keyPressEvent(self, a0) -> None:
        if a0.key() == Qt.Key.Key_Right:
            self.nmf_view.move_forward()
        elif a0.key() == Qt.Key.Key_Left:
            self.nmf_view.move_backward()
        return super().keyPressEvent(a0)

    def _init_ui(self):
        layout = QHBoxLayout()
        layout.addWidget(self.tabs)
        layout.addWidget(self.nmf_view)
        self.setLayout(layout)

    def _show_v_prime(self):
        if not self.feature_matrix_group:
            return
        w = self.nmf_view.w_matrix()
        h = self.nmf_view.h_matrix()
        v_prime = np.abs(self.feature_matrix_group.feature_matrix - w @ h)

        self.nmf_view.set_feature_matrix(
            data=v_prime, start_timestamp=self.start_time, autoLevels=False
        )

    def _show_v(self):
        if self.feature_matrix_group:
            self.nmf_view.set_feature_matrix(
                data=self.feature_matrix_group.feature_matrix,
                start_timestamp=self.start_time,
                autoLevels=True,
            )

    def _update_feature_matrix(self, show_v_prime: bool = False):
        if show_v_prime:
            self._show_v_prime()
        else:
            self._show_v()

    def _on_cell_clicked(self, time, channel):
        self.timeClicked.emit(int(time + self.start_time), channel)

    def _on_show_v_prime(self, checked: bool):
        self._update_feature_matrix(checked)

    def _on_new_triggers_path(self, path):
        trigs = detect_triggers(path)
        if len(trigs) == 0:
            return

        self.tabs.evaluation_widget.show_triggers.setChecked(True)
        self.nmf_view.set_triggers(trigs)

    def _on_new_time_grade_path(self, path):
        time_grades = load_time_grades(path)
        if time_grades.empty:
            return

        self.tabs.evaluation_widget.show_time_grades.setChecked(True)
        self.nmf_view.set_time_grades(time_grades)

    def _on_feature_matrix_selected(self, item: NMFFeatureMatrixItem):
        self.feature_matrix_group = item.feature_matrix_group
        self.nmf_view.set_channel_names(self.feature_matrix_group.feature_names)
        self.nmf_view.feature_matrix_sampling_frequency = (
            self.feature_matrix_group.sfreq
        )
        self.start_time = item.start_timestamp
        self.tabs.evaluation_widget.toggle_v_prime_button.setChecked(False)
        self._update_feature_matrix()

    def _on_nmf_model_selected(self, item: NMFModelItem):
        self.nmf = item.nmf

        self.nmf_view.set_h_matrix(self.nmf.h)
        self.nmf_view.set_w_matrix(self.nmf.w)
        self.tabs.metrics_widget.set_metrics(self.nmf.metrics())
        self._update_feature_matrix()

    def _on_show_value_checked(self, show: bool) -> None:
        self.nmf_view.show_value(show)

    def _on_show_crosshair_checked(self, show: bool) -> None:
        self.nmf_view.show_crosshair(show)

    def _on_show_channel_info_checked(self, show: bool) -> None:
        self.nmf_view.show_channel_info(show)
