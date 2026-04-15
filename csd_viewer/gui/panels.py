from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QGroupBox, QPushButton, 
    QCheckBox, QLabel, QGridLayout, QFrame, QScrollArea, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal
from csd_viewer.gui.constants import (
    FONT_SANS, COLOR_ACTION, COLOR_SUCCESS, COLOR_CAUTION, COLOR_MUTED, COLOR_INFO
)
from csd_viewer.gui.styles import (
    GROUP_BOX_STYLE, LIST_STYLE, BUTTON_STYLE, add_button, add_label, MODE_INDICATOR_STYLE
)

class StatusPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Status", parent)
        self.setStyleSheet(GROUP_BOX_STYLE)
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)
        
        self.mode_badge = QLabel("MODE: LOCAL")
        self.mode_badge.setStyleSheet(MODE_INDICATOR_STYLE + f"background: {COLOR_MUTED};")
        self.mode_badge.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.mode_badge)
        
        self.status_text = QLabel("Browsing local directory...")
        self.status_text.setWordWrap(True)
        self.status_text.setStyleSheet(f"font-family: {FONT_SANS}; font-size: 11px;")
        layout.addWidget(self.status_text)
        
        btn_row = QHBoxLayout()
        self.change_dir_btn = add_button(btn_row, "Choose dir")
        self.refresh_btn = add_button(btn_row, "Refresh")
        self.toggle_mode_btn = add_button(btn_row, "Connect Remote")
        layout.addLayout(btn_row)

    def set_mode(self, mode_str, details, color):
        self.mode_badge.setText(f"MODE: {mode_str}")
        self.mode_badge.setStyleSheet(MODE_INDICATOR_STYLE + f"background: {color};")
        self.status_text.setText(details)
        self.toggle_mode_btn.setText("Disconnect Remote" if mode_str == "REMOTE" else "Connect Remote")
        self.change_dir_btn.setEnabled(mode_str == "LOCAL")

class FileListPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Files", parent)
        self.setStyleSheet(GROUP_BOX_STYLE)
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)
        
        add_label(layout, "Available files")
        self.available_list = QListWidget()
        self.available_list.setStyleSheet(LIST_STYLE)
        self.available_list.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.available_list, 3)
        
        add_label(layout, "Plotted files")
        self.plotted_list = QListWidget()
        self.plotted_list.setStyleSheet(LIST_STYLE)
        self.plotted_list.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.plotted_list, 2)

class PlotControlPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Controls", parent)
        self.setStyleSheet(GROUP_BOX_STYLE)
        self.create_widgets()

    def create_widgets(self):
        layout = QGridLayout(self)
        
        self.plot_btn = QPushButton("Plot CSD")
        self.plot_btn.setStyleSheet(f"background: {COLOR_SUCCESS}; color: white; font-weight: bold; font-family: {FONT_SANS};")
        layout.addWidget(self.plot_btn, 0, 0)
        
        self.autoscale_btn = add_button(layout, "Reset Scale")
        layout.addWidget(self.autoscale_btn, 0, 1)
        
        self.remove_btn = add_button(layout, "Remove")
        layout.addWidget(self.remove_btn, 1, 0)
        
        self.clear_btn = add_button(layout, "Clear Plot")
        layout.addWidget(self.clear_btn, 1, 1)

class FittingPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Fitting Methods", parent)
        self.setStyleSheet(GROUP_BOX_STYLE)
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)
        
        self.poly_check = QCheckBox("Polynomial")
        self.poly_check.setChecked(True)
        layout.addWidget(self.poly_check)
        
        self.linear_check = QCheckBox("Linear")
        layout.addWidget(self.linear_check)
        
        self.none_check = QCheckBox("None")
        layout.addWidget(self.none_check)

class ToolsPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Tools", parent)
        self.setStyleSheet(GROUP_BOX_STYLE)
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)
        self.compare_btn = add_button(layout, "Compare plotted files")
        self.export_btn = add_button(layout, "Export selected data...")

class ElementPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Elements", parent)
        self.setStyleSheet(GROUP_BOX_STYLE)
        self.element_checks = {}
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll_content = QWidget()
        self.grid = QGridLayout(scroll_content)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

    def add_elements(self, elements, cols=3):
        for i, el in enumerate(elements):
            check = QCheckBox(f"{el.symbol}")
            check.setProperty("element", el)
            row, col = divmod(i, cols)
            self.grid.addWidget(check, row, col)
            self.element_checks[el] = check
