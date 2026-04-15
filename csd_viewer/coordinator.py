import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Any, Optional

import numpy as np
from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtWidgets import QFileDialog, QMessageBox, QListWidgetItem

from csd_viewer.files.csd_file import CSDFile
from csd_viewer.files.client import (
    list_files, download_filepair, clear_temp_files, 
    API_URL, list_local_files, TEMP_FOLDER
)
from csd_viewer.plotting.plot_csd import Rescale
from csd_viewer.gui.constants import (
    COLOR_SUCCESS, COLOR_MUTED, COLOR_INFO, COLOR_CAUTION
)
from csd_viewer.gui.panels import (
    StatusPanel, FileListPanel, PlotControlPanel, 
    FittingPanel, ToolsPanel, ElementPanel
)
from csd_viewer.gui.canvas import MqPlotCanvas

from csd_viewer.gui.element_indicator import ElementIndicator
from ops.ecris.analysis.model.element import PERSISTANT_ELEMENTS, VARIABLE_ELEMENTS

from csd_viewer.status_bar import StatusBarSingleton

class FileMode:
    REMOTE = "REMOTE"
    LOCAL = "LOCAL"

class Coordinator(QObject):
    def __init__(self, main_window, default_directory: Path):
        super().__init__()
        self._main_window = main_window
        self._current_directory = default_directory
        
        # Connect to Status Bar
        self.status_bar_service = StatusBarSingleton()
        self.status_bar_service.on_status_changed = self._on_status_bar_update
        
        # State
        self.plotted_files: List[Path] = []
        self.mode = FileMode.LOCAL
        self._last_updated = "N/A"
        self._files_available = 0
        
        # Elements
        self.element_indicators: List[ElementIndicator] = []
        for el in PERSISTANT_ELEMENTS + VARIABLE_ELEMENTS:
            self.element_indicators.append(ElementIndicator(el, self._is_element_plotted))
        
        # Attached Objects
        self._status_panel: Optional[StatusPanel] = None
        self._file_list_panel: Optional[FileListPanel] = None
        self._plot_control_panel: Optional[PlotControlPanel] = None
        self._fitting_panel: Optional[FittingPanel] = None
        self._tools_panel: Optional[ToolsPanel] = None
        self._element_panel: Optional[ElementPanel] = None
        self._canvas: Optional[MqPlotCanvas] = None

    def _is_element_plotted(self, element):
        if self._element_panel and element in self._element_panel.element_checks:
            return self._element_panel.element_checks[element].isChecked()
        return False

    def _on_status_bar_update(self, info):
        self._main_window.statusBar().showMessage(info, 5000)

    def attach(self, obj: Any):
        if isinstance(obj, StatusPanel):
            self._status_panel = obj
        elif isinstance(obj, FileListPanel):
            self._file_list_panel = obj
        elif isinstance(obj, PlotControlPanel):
            self._plot_control_panel = obj
        elif isinstance(obj, FittingPanel):
            self._fitting_panel = obj
            self._fitting_panel.poly_check.stateChanged.connect(self.update_plot)
            self._fitting_panel.linear_check.stateChanged.connect(self.update_plot)
            self._fitting_panel.none_check.stateChanged.connect(self.update_plot)
        elif isinstance(obj, ToolsPanel):
            self._tools_panel = obj
        elif isinstance(obj, ElementPanel):
            self._element_panel = obj
            self._element_panel.add_elements(PERSISTANT_ELEMENTS + VARIABLE_ELEMENTS)
            # Connect element check signals
            for check in self._element_panel.element_checks.values():
                check.stateChanged.connect(self.update_plot)
        elif isinstance(obj, MqPlotCanvas):
            self._canvas = obj
        else:
            raise RuntimeError(f"Coordinator passed bad object {obj}")

    def initialize(self):
        self._configure_signals()
        self.refresh_file_lists()
        self.update_connection_status()
        self.update_button_states()

    def _configure_signals(self):
        # Status Panel
        self._status_panel.refresh_btn.clicked.connect(self.refresh_file_lists)
        self._status_panel.change_dir_btn.clicked.connect(self.choose_directory)
        self._status_panel.toggle_mode_btn.clicked.connect(self.toggle_mode)
        
        # File Lists
        self._file_list_panel.available_list.itemSelectionChanged.connect(self.update_button_states)
        self._file_list_panel.plotted_list.itemSelectionChanged.connect(self.update_button_states)
        self._file_list_panel.available_list.itemDoubleClicked.connect(self.plot_selected_file)
        
        # Plot Controls
        self._plot_control_panel.plot_btn.clicked.connect(self.plot_selected_file)
        self._plot_control_panel.autoscale_btn.clicked.connect(self.autoscale_plot)
        self._plot_control_panel.remove_btn.clicked.connect(self.remove_selected_from_plot)
        self._plot_control_panel.clear_btn.clicked.connect(self.clear_plot)
        
        # Tools
        self._tools_panel.compare_btn.clicked.connect(self.open_comparison)
        self._tools_panel.export_btn.clicked.connect(self.export_data)

    def open_comparison(self):
        QMessageBox.information(self._main_window, "Comparison", "Comparison window coming soon.")

        # Menu actions
        self._main_window.open_dir_action.triggered.connect(self.open_data_directory)
        self._main_window.export_action.triggered.connect(self.export_data)
        self._main_window.diagnostic_action.triggered.connect(self.open_diagnostic_window)

    def open_data_directory(self):
        import platform, subprocess
        path = str(self._current_directory)
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def export_data(self):
        if not self.plotted_files:
            QMessageBox.warning(self._main_window, "Error", "No plotted data to export.")
            return
            
        save_path, _ = QFileDialog.getSaveFileName(
            self._main_window, "Save Exported Data", 
            str(self._current_directory), "CSV files (*.csv);;All files (*.*)"
        )
        if save_path:
            from csd_viewer.files.csd_file import export_to_file
            try:
                # Need to convert Paths to what export_to_file expects
                with open(save_path, "w") as f:
                    export_to_file(f, self.plotted_files)
                QMessageBox.information(self._main_window, "Success", "Export successful.")
            except Exception as e:
                QMessageBox.critical(self._main_window, "Error", f"Error exporting: {e}")

    def open_diagnostic_window(self):
        # Placeholder
        QMessageBox.information(self._main_window, "Diagnostic", "Diagnostic window coming soon.")

    def update_button_states(self):
        can_plot = self._file_list_panel.available_list.currentRow() >= 0
        can_remove = self._file_list_panel.plotted_list.currentRow() >= 0
        
        self._plot_control_panel.plot_btn.setEnabled(can_plot)
        self._plot_control_panel.remove_btn.setEnabled(can_remove)
        self._plot_control_panel.clear_btn.setEnabled(len(self.plotted_files) > 0)
        self._tools_panel.compare_btn.setEnabled(len(self.plotted_files) > 1)
        self._tools_panel.export_btn.setEnabled(len(self.plotted_files) > 0)

    def update_connection_status(self):
        update_status = f"Last update {self._last_updated}, {self._files_available} files found"
        if self.mode == FileMode.REMOTE:
            details = f"Connected to {API_URL}\n{update_status}"
            self._status_panel.set_mode("REMOTE", details, COLOR_SUCCESS)
        else:
            details = f"Browsing directory {self._current_directory}\n{update_status}"
            self._status_panel.set_mode("LOCAL", details, COLOR_MUTED)

    def choose_directory(self):
        new_dir = QFileDialog.getExistingDirectory(
            self._main_window, "Choose a directory", str(self._current_directory)
        )
        if new_dir:
            self._current_directory = Path(new_dir)
            self.refresh_file_lists()

    def toggle_mode(self):
        self.mode = FileMode.REMOTE if self.mode == FileMode.LOCAL else FileMode.LOCAL
        self.refresh_file_lists()
        self.update_connection_status()

    def refresh_file_lists(self):
        current_time = time.time()
        self._last_updated = datetime.fromtimestamp(current_time).strftime("%Y-%m-%d %H:%M")
        
        try:
            if self.mode == FileMode.REMOTE:
                found_files = list_files()
                if not found_files:
                    QMessageBox.warning(self._main_window, "Connection Error", "Failed to connect to remote server.")
                    self.mode = FileMode.LOCAL
                    self.refresh_file_lists()
                    return
            else:
                found_files = list_local_files(self._current_directory)
        except Exception as e:
            QMessageBox.critical(self._main_window, "Error", f"Failed to refresh files: {str(e)}")
            found_files = []

        self._files_available = len(found_files)
        
        # Update Available List
        self._file_list_panel.available_list.clear()
        for f in reversed(sorted(found_files)):
            if f not in self.plotted_files:
                item = QListWidgetItem(f.name)
                item.setData(Qt.UserRole, f)
                self._file_list_panel.available_list.addItem(item)
                
        # Update Plotted List
        self._file_list_panel.plotted_list.clear()
        for f in self.plotted_files:
            item = QListWidgetItem(f.name)
            item.setData(Qt.UserRole, f)
            self._file_list_panel.plotted_list.addItem(item)
            
        self.update_connection_status()
        self.update_button_states()

    def plot_selected_file(self):
        item = self._file_list_panel.available_list.currentItem()
        if not item: return
        file_path = item.data(Qt.UserRole)
        
        try:
            if self.mode == FileMode.REMOTE:
                csd_path = download_filepair(file_path)
            else:
                csd_path = file_path
                
            if os.path.getsize(csd_path) < 1:
                QMessageBox.warning(self._main_window, "Invalid File", "File size is 0. CSD may be in progress.")
                return
                
            self.plotted_files.append(file_path)
            self.refresh_file_lists()
            self.update_plot()
            
        except Exception as e:
            QMessageBox.critical(self._main_window, "Plot Error", f"Failed to plot file: {str(e)}")

    def update_plot(self):
        if not self._canvas: return
        
        plotted_files_to_draw = []
        rescaling_methods = []
        if self._fitting_panel.poly_check.isChecked(): rescaling_methods.append(Rescale.POLYNOMIAL)
        if self._fitting_panel.linear_check.isChecked(): rescaling_methods.append(Rescale.LINEAR)
        if self._fitting_panel.none_check.isChecked(): rescaling_methods.append(Rescale.NONE)
        
        from csd_viewer.plotting.plot_csd import plot_file
        
        self._canvas.ax.clear()
        self._canvas.setup_plot()
        
        for f_path in self.plotted_files:
            if self.mode == FileMode.REMOTE:
                full_path = Path(TEMP_FOLDER) / f_path.name
            else:
                full_path = f_path
            
            csd_file = CSDFile(full_path, os.path.getsize(full_path))
            for method in rescaling_methods:
                plot_file(self._canvas.ax, csd_file, method)
        
        if self.plotted_files:
            self._canvas.ax.legend(fontsize=9)
            
        # Draw element indicators
        y_min, y_max = self._canvas.ax.get_ylim()
        delta_y = 0.1 * abs(y_max - y_min)
        
        visible_indicators = [ei for ei in self.element_indicators if ei.is_plotted]
        for i, ei in enumerate(visible_indicators):
            y_val = y_min + delta_y * (i + 1)
            self._canvas._draw_element_indicator(ei, y_val, draw_lines=True)
            
        self._canvas.canvas.draw()

    def autoscale_plot(self):
        self._canvas.ax.relim()
        self._canvas.ax.autoscale_view()
        self._canvas.ax.set_ybound(lower=0)
        self._canvas.canvas.draw()

    def remove_selected_from_plot(self):
        item = self._file_list_panel.plotted_list.currentItem()
        if not item: return
        file_path = item.data(Qt.UserRole)
        if file_path in self.plotted_files:
            self.plotted_files.remove(file_path)
            self.refresh_file_lists()
            self.update_plot()

    def clear_plot(self):
        self.plotted_files = []
        clear_temp_files()
        self.refresh_file_lists()
        self.update_plot()
