import sys
import logging
from PySide6.QtWidgets import QApplication
from csd_viewer.gui.main_window import MainWindow
from csd_viewer.coordinator import Coordinator
from csd_viewer.files.configuration import load_configuration, create_configuration

def main():
    app = QApplication(sys.argv)
    app.setStyle("GTK")
    
    # Load configuration
    config = load_configuration()
    if config is None:
        config = create_configuration()
    
    # Create the visual shell
    window = MainWindow()
    
    # Create the Coordinator
    coordinator = Coordinator(window, config.default_directory)
    
    # Attach widgets to the Coordinator
    coordinator.attach(window.canvas)
    coordinator.attach(window.status_panel)
    coordinator.attach(window.file_list_panel)
    coordinator.attach(window.plot_control_panel)
    coordinator.attach(window.fitting_panel)
    coordinator.attach(window.tools_panel)
    coordinator.attach(window.element_panel)
    
    # Wire everything together
    window.set_coordinator(coordinator)
    
    # Initialize state and show
    coordinator.initialize()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
