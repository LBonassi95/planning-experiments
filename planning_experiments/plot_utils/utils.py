from matplotlib import pyplot as plt

DEFAULT_COLORS = plt.rcParams['axes.prop_cycle'].by_key()['color']
DEFAULT_LINE_STYLE = '-'
DEFAULT_COLORS = plt.rcParams['axes.prop_cycle'].by_key()['color']
DEFAULT_MARKER = '.'


def get_markers_style(markers_styles: dict, elem: str) -> str:
    if markers_styles.get(elem, None) is None:
        return DEFAULT_MARKER
    else:
        return markers_styles[elem]

def get_color(colors: dict, system: str, index: int) -> str:
    if colors.get(system, None) is None:
        color = DEFAULT_COLORS[index % len(DEFAULT_COLORS)]
        return color
    else:
        return colors[system]

def get_linestyle(line_styles: dict, system: str) -> str:
    if line_styles.get(system, None) is None:
        return DEFAULT_LINE_STYLE
    else:
        return line_styles[system]
    
def get_legend_entry(legend_entries: dict, system: str) -> str:
    if legend_entries.get(system, None) is None:
        return system
    else:
        return legend_entries[system]