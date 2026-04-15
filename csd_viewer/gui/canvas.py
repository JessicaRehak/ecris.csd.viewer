import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PySide6.QtWidgets import QWidget, QVBoxLayout

class MqPlotCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.figure = Figure(figsize=(8, 6), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)
        
        self.setup_plot()
        
    def setup_plot(self):
        self.ax.grid(True, alpha=0.3, linestyle="--")
        self.ax.set_xlabel("Mass/Charge (m/q)")
        self.ax.set_ylabel("Current (uA)")
        self.ax.set_facecolor("white")
        self.figure.patch.set_facecolor("#fdfdfd")
        
    def redraw(self, plotted_files, element_indicators, draw_lines=False, title=None):
        self.ax.clear()
        self.setup_plot()
        
        if title:
            self.ax.set_title(title)
            
        for file_info in plotted_files:
            # file_info should be a tuple (csd, label)
            csd, label = file_info
            self.ax.plot(csd.m_over_q, csd.beam_current, label=label)
            
        if plotted_files:
            self.ax.legend(fontsize=9)
            
        # Draw element indicators
        # This will need the logic from ElementIndicator but adapted
        y_min, y_max = self.ax.get_ylim()
        delta_y = 0.1 * abs(y_max - y_min)
        
        visible_indicators = [ei for ei in element_indicators if ei.is_plotted]
        for i, ei in enumerate(visible_indicators):
            y_val = y_min + delta_y * (i + 1)
            self._draw_element_indicator(ei, y_val, draw_lines)
            
        self.canvas.draw()

    def _draw_element_indicator(self, ei, y_val, draw_lines):
        # Simplified version of ElementIndicator.draw
        m_over_q = ei.m_over_q_values
        q_values = range(1, ei.element.atomic_number + 1)
        
        xlim = self.ax.get_xlim()
        mask = [xlim[0] <= mq <= xlim[1] for mq in m_over_q]
        
        mq_visible = [mq for mq, m in zip(m_over_q, mask) if m]
        q_visible = [q for q, m in zip(q_values, mask) if m]
        
        color = self.ax.plot(mq_visible, [y_val]*len(mq_visible), 'v', ms=8, markeredgecolor='black')[0].get_color()
        
        for mq, q in zip(mq_visible, q_visible):
            self.ax.text(mq, y_val + 0.02 * (self.ax.get_ylim()[1] - self.ax.get_ylim()[0]), 
                         str(q), ha='center', va='bottom', fontsize=8, weight='bold')
            if draw_lines:
                self.ax.axvline(mq, color=color, alpha=0.2, linestyle='--')
                
        self.ax.text(1.01, self.ax.transLimits.transform((0, y_val))[1], 
                     f"{ei.element.symbol}-{round(ei.element.atomic_mass)}",
                     transform=self.ax.transAxes, color=color, weight='bold', va='center')
