"""Main CSD Viewer App"""
from pathlib import Path
import tkinter as tk
import matplotlib

from ecris.csd.viewer.gui.elements import ElementButtons

from .gui import FileList, PlotControls, Plot, FileListControls
from .analysis.element import PERSISTANT_ELEMENTS, VARIABLE_ELEMENTS

__version__ = "1.0.1"

matplotlib.rc('font', size=14)


class CSDViewer(tk.Tk):
    def __init__(self, default_path: Path):
        super().__init__()
        self.default_path = default_path.absolute()
        self.title(f"CSD Viewer (v{__version__})")
        # self.columnconfigure(0, weight=5)
        # self.columnconfigure(1, weight=1)
        # self.rowconfigure(0, weight=1)
        # self.rowconfigure(1, weight=20)
        # self.rowconfigure(2, weight=10)
        # self.rowconfigure(3, weight=1)
        self.pad = 5.0
        
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.quit)

    def quit(self):
        self.plot.destroy()
        self.destroy()

    def create_widgets(self):
        self.file_list = FileList(self.default_path)
        self.file_list_controls = FileListControls(self, self.file_list)
        self.plot = Plot(self) 
        self.element_buttons = ElementButtons(self, self.plot, PERSISTANT_ELEMENTS, VARIABLE_ELEMENTS)
        self.controls = PlotControls(self, self.plot, self.file_list, self.element_buttons)
        self.plot.set_element_indicators(self.element_buttons.element_visibility)

        self.plot.pack(side='left', fill='both', expand=True)
        self.file_list_controls.pack()
        self.file_list.pack(padx=10, pady=10)
        self.controls.pack()
        self.element_buttons.pack(fill="both", padx=10, pady=10)
