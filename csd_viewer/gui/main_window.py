import sys
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter, QStatusBar
from PySide6.QtCore import Qt

from csd_viewer.gui.constants import COLOR_BG
from csd_viewer.gui.canvas import MqPlotCanvas
from csd_viewer.gui.panels import (
    StatusPanel, FileListPanel, PlotControlPanel, 
    FittingPanel, ToolsPanel, ElementPanel
)

from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter, QStatusBar, QMenu
from PySide6.QtGui import QAction

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSD Viewer (Renovated)")
        self.resize(1280, 800)
        self.setStyleSheet(f"background: {COLOR_BG};")
        
        self.create_widgets()
        self.create_menu()
        self.setup_layout()

    def create_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        
        self.open_dir_action = QAction("Open Data Directory", self)
        file_menu.addAction(self.open_dir_action)
        
        file_menu.addSeparator()
        
        self.export_action = QAction("Export Data...", self)
        file_menu.addAction(self.export_action)
        
        file_menu.addSeparator()
        
        self.quit_action = QAction("Quit", self)
        self.quit_action.triggered.connect(self.close)
        file_menu.addAction(self.quit_action)
        
        tools_menu = menu.addMenu("Tools")
        self.diagnostic_action = QAction("Diagnostic Window", self)
        tools_menu.addAction(self.diagnostic_action)

    def create_widgets(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.canvas = MqPlotCanvas()
        self.status_panel = StatusPanel()
        self.file_list_panel = FileListPanel()
        self.plot_control_panel = PlotControlPanel()
        self.fitting_panel = FittingPanel()
        self.tools_panel = ToolsPanel()
        self.element_panel = ElementPanel()
        
        self.setStatusBar(QStatusBar())

    def setup_layout(self):
        main_layout = QHBoxLayout(self.central_widget)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # Left Panel (Controls)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        left_layout.addWidget(self.status_panel)
        left_layout.addWidget(self.file_list_panel, 1)
        left_layout.addWidget(self.plot_control_panel)
        left_layout.addWidget(self.fitting_panel)
        left_layout.addWidget(self.tools_panel)
        
        # Plot (Center)
        plot_widget = QWidget()
        plot_layout = QVBoxLayout(plot_widget)
        plot_layout.addWidget(self.canvas)
        
        # Right Panel (Elements)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.addWidget(self.element_panel)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(plot_widget)
        splitter.addWidget(right_widget)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        splitter.setStretchFactor(2, 1)
        
        main_layout.addWidget(splitter)

    def set_coordinator(self, coordinator):
        self.coordinator = coordinator
        # Coordinator will attach its signals here or via its own attach() calls
