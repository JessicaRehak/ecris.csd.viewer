from dataclasses import dataclass
from typing import List, Optional
from PySide6.QtCore import Qt

class ElementIndicator:
    def __init__(self, element, is_plotted_func):
        self.element = element
        self.is_plotted_func = is_plotted_func
        
        q_values = range(1, element.atomic_number + 1)
        self.m_over_q_values = [element.atomic_mass / q for q in q_values]
        self.color = None

    @property
    def is_plotted(self) -> bool:
        return self.is_plotted_func(self.element)
