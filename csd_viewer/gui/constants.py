from pathlib import Path

# --- CONSTANTS ---
CURRENT_DIR = Path(__file__).parent.parent
DATA_PATH = CURRENT_DIR / "data"
TEMP_FOLDER = CURRENT_DIR / "tmp"

# Retro Cassette Futurism Palette
COLOR_BG = "#f4f1ea"            # Primary enclosure/chassis
COLOR_PLOT_BG = "#fdfdfd"       # High-contrast readout area
COLOR_GRID = "#e0e0e0"          # Subtle grid lines
COLOR_TEXT = "#262626"          # Primary legend/data text

# Functional Status Colors
COLOR_ACTION = "#d55e00"        # Vermilion: Primary actions (Plot, Export)
COLOR_INFO = "#0072b2"          # Dark Blue: Informational, Selection
COLOR_SUCCESS = "#009e73"       # Green: Plotted data, Connected status
COLOR_CAUTION = "#e69f00"       # Amber: Warnings, Rescale off
COLOR_MUTED = "#909090"         # Grey: Inactive, Background data

# Styling
FONT_MONO = "Consolas, 'Liberation Mono', Menlo, Monaco, 'DejaVu Sans Mono', monospace"
FONT_SANS = "'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Liberation Sans', sans-serif"
