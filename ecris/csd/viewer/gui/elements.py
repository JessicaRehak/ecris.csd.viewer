import tkinter as tk
from typing import List

from ecris.csd.viewer.analysis import Element

class ElementButtons(tk.Frame):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(owner, *args, **kwargs)
        self.create_widgets()

    def create_widgets(self):
        pass