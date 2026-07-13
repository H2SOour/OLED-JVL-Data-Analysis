import os
import glob
import math
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from matplotlib.ticker import (
    MultipleLocator,
    LogLocator,
    NullFormatter,
    AutoMinorLocator,
    MaxNLocator
)


# ============================================================
# User-configurable parameters
# ============================================================

DATA_DIR = "./data"
OUTPUT_DIR = "./output"

# Apply the selected voltage range to all plots
# True: CE-L, CE-J, and EQE-J plots also use only data within the selected voltage range
# False: only the JVL and JV plots use voltage-range filtering
APPLY_VRANGE_TO_ALL = True


# ----------------------------
# Legend settings
# ----------------------------

SHOW_LEGEND = True

# Common options:
# "best", "upper left", "upper right", "lower left", "lower right"
LEGEND_LOC = "best"

# Whether to draw a frame around the legend
LEGEND_FRAME = False


# ----------------------------
# JVL plot ranges
# ----------------------------

JVL_V_MIN, JVL_V_MAX = 0, 30

# Luminance uses a logarithmic axis, so the minimum cannot be zero
# To display approximately 0–1000 cd/m², use 1–1000 or 0.1–1000
JVL_LUM_MIN, JVL_LUM_MAX = 1, 1e4

# Current-density range for the right y-axis
JVL_J_MIN, JVL_J_MAX = 0, 16


# ----------------------------
# J-V plot ranges
# ----------------------------

JV_V_MIN, JV_V_MAX = 0, 30
JV_J_MIN, JV_J_MAX = 0, 16

# Whether to use a logarithmic y-axis for the J-V plot
JV_Y_LOG = False


# ----------------------------
# Current efficiency vs luminance plot ranges
# ----------------------------

CE_LUM_X_MIN, CE_LUM_X_MAX = 1, 10000
CE_LUM_Y_MIN, CE_LUM_Y_MAX = 0, 1
CE_LUM_X_LOG = True
CE_LUM_Y_LOG = False


# ----------------------------
# Current efficiency vs current density plot ranges
# ----------------------------

CE_J_X_MIN, CE_J_X_MAX = 0.01, 1000
CE_J_Y_MIN, CE_J_Y_MAX = 0, 1
CE_J_X_LOG = True
CE_J_Y_LOG = False


# ----------------------------
# EQE vs current density plot ranges
# ----------------------------

EQE_J_X_MIN, EQE_J_X_MAX = 0.01, 1000
EQE_J_Y_MIN, EQE_J_Y_MAX = 0, 0.5
EQE_J_X_LOG = True
EQE_J_Y_LOG = False


# ----------------------------
# EQE unit conversion
# ----------------------------

# If EQE is stored as a 0–1 fraction representing 0%–100%, set this to 100
# If EQE is already stored in percent (for example, 2.5 means 2.5%), keep this at 1
EQE_SCALE = 1


# ----------------------------
# Figure and font settings
# ----------------------------

DPI = 600
TRANSPARENT = True

FIGSIZE_JVL = (4.8, 3.8)
FIGSIZE_SINGLE = (4.5, 3.8)

FONT_SIZE_LABEL = 15
FONT_SIZE_TICK = 13
FONT_SIZE_LEGEND = 9

LINEWIDTH = 1.4
MARKERSIZE = 6.0
SPINE_WIDTH = 2.2
TICK_WIDTH = 1.8
MAJOR_TICK_LENGTH = 6
MINOR_TICK_LENGTH = 3.5


# ----------------------------
# Text encodings
# ----------------------------

ENCODINGS_TO_TRY = ["utf-8-sig", "utf-8", "cp932", "shift_jis", "gbk"]


# ============================================================
# High-contrast color palettes
# ============================================================

LUM_AXIS_COLOR = "#8C2D04"
J_AXIS_COLOR = "#123789"

# Luminance curves in the JVL plot: high-contrast warm colors
JVL_LUM_COLORS = [
   "#8C2D04",
    "#B33C03",
    "#D94801",
    "#E85D04",
    "#F16913",
    "#FD8D3C",
    "#FDAE6B",
    "#FDBE85",
    "#FDD0A2",
    "#FEE6CE",
    "#FFF0D9",
    "#FFF7EC",
]

# Current-density curves in the JVL plot: high-contrast cool colors
JVL_J_COLORS = [
   "#123789",
    "#1C4E99",
    "#1F72AD",
    "#218FB9",
    "#30A0BC",
    "#51B7BA",
    "#7CC7B4",
    "#98D1B2",
    "#C6E4AD",
    "#E2EDAB",
    "#E8F1B5",
    "#F7F7D2",
]

# J-V plot: high-contrast blue/green/purple/cyan colors for filled triangle markers
JV_COLORS = [
  "#123789",
    "#1C4E99",
    "#1F72AD",
    "#218FB9",
    "#30A0BC",
    "#51B7BA",
    "#7CC7B4",
    "#98D1B2",
    "#C6E4AD",
    "#E2EDAB",
    "#E8F1B5",
    "#F7F7D2",
]

# Current efficiency vs luminance: purple palette
CE_LUM_COLORS = [
   "#7400ff",
    "#7816f0",
    "#7c28e0",
    "#8038d1",
    "#8347c2",
    "#8555b3",
    "#8762a3",
    "#886f94",
    "#897b85",
    "#8a8675",
    "#8a9166",
    "#8a9b54"
]

# Current efficiency vs current density: blue-green-purple palette
CE_J_COLORS = [
    "#00b32c",
    "#11ab36",
    "#1da33e",
    "#279a45",
    "#2f924b",
    "#368a50",
    "#3d8154",
    "#427958",
    "#47705b",
    "#4b685e",
    "#4e6060",
    "#515861"
]

# EQE vs current density: orange-red-brown palette
EQE_COLORS = [
    "#e65c00",
    "#dc5e14",
    "#d16022",
    "#c6612d",
    "#ba6237",
    "#ae623f",
    "#a26247",
    "#96624e",
    "#896154",
    "#7c605a",
    "#6e5f5f",
    "#605e5e"
]

# Fallback colors
DEFAULT_COLORS = [
    "#0072b2",
    "#d55e00",
    "#009e73",
    "#cc79a7",
    "#56b4e9",
    "#e69f00",
    "#f0e442",
    "#000000",
    "#9467bd",
    "#8c564b",
    "#17becf",
    "#bcbd22",
]


# ----------------------------
# Marker settings
# ----------------------------

JV_MARKER = "^"
JVL_LUM_MARKER = "^"
JVL_J_MARKER = "o"
CE_MARKER = "D"
EQE_MARKER = "^"


# ============================================================
# File loading and parsing
# ============================================================

def read_lines_robust(filepath):
    """Try multiple encodings and return the decoded lines and successful encoding."""
    last_err = None

    for enc in ENCODINGS_TO_TRY:
        try:
            with open(filepath, "r", encoding=enc, errors="strict") as f:
                lines = f.readlines()
            return lines, enc

        except (UnicodeDecodeError, UnicodeError) as e:
            last_err = e
            continue

    raise RuntimeError(
        f"Unable to read file: {filepath}\n"
        f"Encodings attempted: {ENCODINGS_TO_TRY}\n"
        f"Last error: {last_err}"
    )


def find_header_row(lines):
    """Locate the actual table-header row."""
    for idx, line in enumerate(lines):
        if "Drive voltage" in line:
            return idx

    raise ValueError("Could not find a header row containing 'Drive voltage'.")


def find_col(columns, keyword):
    """Find a column by case-insensitive keyword matching."""
    for c in columns:
        if keyword.lower() in str(c).lower():
            return c

    return None


def load_one_file(filepath):
    """Read and parse one CSV file."""
    lines, enc = read_lines_robust(filepath)
    header_idx = find_header_row(lines)

    df = pd.read_csv(filepath, encoding=enc, skiprows=header_idx)
    df.columns = [str(c).strip() for c in df.columns]

    col_v = find_col(df.columns, "Drive voltage")
    col_jd = find_col(df.columns, "Current density")
    col_eqe = find_col(df.columns, "EQE")
    col_eff = find_col(df.columns, "Luminous efficacy")

    col_lum_actual = find_col(df.columns, "Actual luminance")
    col_lum_rel = find_col(df.columns, "Relative luminance")
    col_lum = col_lum_actual if col_lum_actual is not None else col_lum_rel

    required = {
        "Drive voltage": col_v,
        "Current density": col_jd,
        "EQE": col_eqe,
        "Luminous efficacy": col_eff,
        "Actual/Relative luminance": col_lum,
    }

    missing = [k for k, v in required.items() if v is None]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}\n"
            f"Detected columns: {list(df.columns)}"
        )

    out = pd.DataFrame({
        "voltage": pd.to_numeric(df[col_v], errors="coerce"),
        "current_density": pd.to_numeric(df[col_jd], errors="coerce"),
        "luminance": pd.to_numeric(df[col_lum], errors="coerce"),
        "efficiency": pd.to_numeric(df[col_eff], errors="coerce"),
        "eqe": pd.to_numeric(df[col_eqe], errors="coerce") * EQE_SCALE,
    })

    out = out.dropna(subset=["voltage"]).reset_index(drop=True)
    return out


def load_all_files(data_dir):
    """Load all CSV files in a directory."""
    paths = sorted(glob.glob(os.path.join(data_dir, "*.csv")))

    if not paths:
        raise FileNotFoundError(f"No CSV files found in directory: {data_dir}")

    datasets = {}

    for p in paths:
        name = os.path.splitext(os.path.basename(p))[0]

        try:
            datasets[name] = load_one_file(p)
            print(f"Loaded: {name} | valid rows: {len(datasets[name])}")

        except Exception as e:
            print(f"Skipped file: {p}\nReason: {e}")

    if not datasets:
        raise RuntimeError("All CSV files failed to parse. Check the input format.")

    return datasets


# ============================================================
# General helper functions
# ============================================================

def filter_voltage(df, v_min, v_max):
    """Filter a dataset by voltage range."""
    d = df.copy()

    if v_min is not None:
        d = d[d["voltage"] >= v_min]

    if v_max is not None:
        d = d[d["voltage"] <= v_max]

    return d


def auto_voltage_tick_step(v_min, v_max):
    """
    Choose a suitable major tick interval for the voltage axis.
    Target approximately 5–6 major ticks, preferably at integer intervals.

    Examples:
      0–10 V -> 2 V
      0–15 V -> 3 V
      0–20 V -> 4 V
      0–30 V -> 5 V
    """
    span = abs(v_max - v_min)

    if span <= 5:
        return 1
    elif span <= 10:
        return 2
    elif span <= 15:
        return 3
    elif span <= 20:
        return 4
    elif span <= 30:
        return 5
    elif span <= 60:
        return 10
    else:
        return int(math.ceil(span / 6 / 5) * 5)


def style_log_x(ax):
    """Configure major and minor ticks for a logarithmic x-axis."""
    ax.set_xscale("log")
    ax.xaxis.set_major_locator(LogLocator(base=10.0))
    ax.xaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2, 10) * 0.1))
    ax.xaxis.set_minor_formatter(NullFormatter())


def style_log_y(ax):
    """Configure major and minor ticks for a logarithmic y-axis."""
    ax.set_yscale("log")
    ax.yaxis.set_major_locator(LogLocator(base=10.0))
    ax.yaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2, 10) * 0.1))
    ax.yaxis.set_minor_formatter(NullFormatter())


def style_axes(ax, xlabel=None, ylabel=None, x_color="black", y_color="black"):
    """
    Apply the shared axis style.
    The spines are not forcibly set to black here,
    so the orange and blue axes in the JVL plot are preserved.
    """
    if xlabel is not None:
        ax.set_xlabel(
            xlabel,
            fontsize=FONT_SIZE_LABEL,
            fontweight="bold",
            labelpad=8
        )

    if ylabel is not None:
        ax.set_ylabel(
            ylabel,
            fontsize=FONT_SIZE_LABEL,
            fontweight="bold",
            color=y_color,
            labelpad=10
        )

    ax.tick_params(
        axis="x",
        which="major",
        direction="out",
        length=MAJOR_TICK_LENGTH,
        width=TICK_WIDTH,
        labelsize=FONT_SIZE_TICK,
        colors=x_color,
        labelcolor=x_color
    )

    ax.tick_params(
        axis="x",
        which="minor",
        direction="out",
        length=MINOR_TICK_LENGTH,
        width=TICK_WIDTH * 0.8,
        colors=x_color
    )

    ax.tick_params(
        axis="y",
        which="major",
        direction="out",
        length=MAJOR_TICK_LENGTH,
        width=TICK_WIDTH,
        labelsize=FONT_SIZE_TICK,
        colors=y_color,
        labelcolor=y_color
    )

    ax.tick_params(
        axis="y",
        which="minor",
        direction="out",
        length=MINOR_TICK_LENGTH,
        width=TICK_WIDTH * 0.8,
        colors=y_color
    )

    for side in ["left", "right", "bottom", "top"]:
        ax.spines[side].set_linewidth(SPINE_WIDTH)

    ax.grid(False)

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontweight("bold")


def add_legend(ax):
    """Add a legend when enabled."""
    if SHOW_LEGEND:
        ax.legend(
            fontsize=FONT_SIZE_LEGEND,
            frameon=LEGEND_FRAME,
            loc=LEGEND_LOC,
            handlelength=1.8,
            handletextpad=0.5,
            borderaxespad=0.4
        )


def save_figure(fig, save_path):
    """
    Save a figure, optionally with a transparent background.
    Keep enough padding to prevent y-axis labels from being clipped.
    """
    fig.savefig(
        save_path,
        dpi=DPI,
        transparent=TRANSPARENT,
        bbox_inches="tight",
        pad_inches=0.18
    )

    plt.close(fig)
    print(f"Saved: {save_path}")


# ============================================================
# Plotting functions
# ============================================================

def plot_jvl(datasets, save_path):
    """Create a JVL plot: voltage vs luminance and current density."""

    fig, ax_lum = plt.subplots(figsize=FIGSIZE_JVL)
    ax_j = ax_lum.twinx()

    fig.patch.set_alpha(0)
    ax_lum.patch.set_alpha(0)
    ax_j.patch.set_alpha(0)

    for i, (name, df) in enumerate(datasets.items()):
        d = filter_voltage(df, JVL_V_MIN, JVL_V_MAX)

        c_lum = JVL_LUM_COLORS[i % len(JVL_LUM_COLORS)]
        c_j = JVL_J_COLORS[i % len(JVL_J_COLORS)]

        d_lum = d[d["luminance"] > 0]

        if not d_lum.empty:
            ax_lum.plot(
                d_lum["voltage"],
                d_lum["luminance"],
                marker=JVL_LUM_MARKER,
                linestyle="-",
                color=c_lum,
                markerfacecolor=c_lum,
                markeredgecolor="black",
                markeredgewidth=0.7,
                linewidth=LINEWIDTH,
                markersize=MARKERSIZE,
                label=name
            )

        if not d.empty:
            ax_j.plot(
                d["voltage"],
                d["current_density"],
                marker=JVL_J_MARKER,
                linestyle="-",
                color=c_j,
                markerfacecolor=c_j,
                markeredgecolor="black",
                markeredgewidth=0.6,
                linewidth=LINEWIDTH,
                markersize=MARKERSIZE
            )

    # ----------------------------
    # Axis ranges
    # ----------------------------

    ax_lum.set_xlim(JVL_V_MIN, JVL_V_MAX)
    ax_lum.set_ylim(JVL_LUM_MIN, JVL_LUM_MAX)
    ax_j.set_ylim(JVL_J_MIN, JVL_J_MAX)

    # ----------------------------
    # Axis scales and tick configuration
    # ----------------------------

    style_log_y(ax_lum)

    v_step = auto_voltage_tick_step(JVL_V_MIN, JVL_V_MAX)
    ax_lum.xaxis.set_major_locator(MultipleLocator(v_step))
    ax_lum.xaxis.set_minor_locator(MultipleLocator(max(1, v_step / 2)))

    ax_j.yaxis.set_major_locator(MaxNLocator(nbins=5, integer=True))
    ax_j.yaxis.set_minor_locator(AutoMinorLocator(2))

    # ----------------------------
    # Base styling for the left axis
    # ----------------------------

    style_axes(
        ax_lum,
        xlabel="Voltage (V)",
        ylabel="Luminance (cd/m$^2$)",
        x_color="black",
        y_color=LUM_AXIS_COLOR
    )

    # Style the left luminance axis in orange
    ax_lum.spines["left"].set_color(LUM_AXIS_COLOR)
    ax_lum.spines["left"].set_linewidth(SPINE_WIDTH)

    ax_lum.tick_params(
        axis="y",
        which="major",
        colors=LUM_AXIS_COLOR,
        labelcolor=LUM_AXIS_COLOR,
        width=TICK_WIDTH,
        length=MAJOR_TICK_LENGTH
    )

    ax_lum.tick_params(
        axis="y",
        which="minor",
        colors=LUM_AXIS_COLOR,
        width=TICK_WIDTH * 0.8,
        length=MINOR_TICK_LENGTH
    )

    ax_lum.yaxis.label.set_color(LUM_AXIS_COLOR)

    # Keep the bottom and top spines black
    ax_lum.spines["bottom"].set_color("black")
    ax_lum.spines["top"].set_color("black")

    # Prevent an extra black line on the left
    ax_lum.spines["right"].set_visible(False)

    # ----------------------------
    # Right current-density axis
    # ----------------------------

    ax_j.set_ylabel(
        "Current density (mA/cm$^2$)",
        fontsize=FONT_SIZE_LABEL,
        fontweight="bold",
        color=J_AXIS_COLOR,
        labelpad=10
    )

    ax_j.tick_params(
        axis="y",
        which="major",
        direction="out",
        length=MAJOR_TICK_LENGTH,
        width=TICK_WIDTH,
        labelsize=FONT_SIZE_TICK,
        colors=J_AXIS_COLOR,
        labelcolor=J_AXIS_COLOR
    )

    ax_j.tick_params(
        axis="y",
        which="minor",
        direction="out",
        length=MINOR_TICK_LENGTH,
        width=TICK_WIDTH * 0.8,
        colors=J_AXIS_COLOR
    )

    ax_j.spines["right"].set_color(J_AXIS_COLOR)
    ax_j.spines["right"].set_linewidth(SPINE_WIDTH)

    # Hide the twin axis left spine to avoid covering the orange axis
    ax_j.spines["left"].set_visible(False)
    ax_j.spines["bottom"].set_visible(False)
    ax_j.spines["top"].set_color("black")
    ax_j.spines["top"].set_linewidth(SPINE_WIDTH)

    for label in ax_j.get_yticklabels():
        label.set_fontweight("bold")

    # Show only luminance-series labels in the JVL legend to reduce clutter
    add_legend(ax_lum)

    save_figure(fig, save_path)


def plot_jv(datasets, save_path):
    """
    J-V plot:
    - use a black y-axis
    - use high-contrast colors and filled triangle markers for every series
    """

    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)

    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    for i, (name, df) in enumerate(datasets.items()):
        d = filter_voltage(df, JV_V_MIN, JV_V_MAX)

        if JV_Y_LOG:
            d = d[d["current_density"] > 0]

        if d.empty:
            continue

        c = JV_COLORS[i % len(JV_COLORS)]

        ax.plot(
            d["voltage"],
            d["current_density"],
            marker=JV_MARKER,
            linestyle="-",
            color=c,
            markerfacecolor=c,
            markeredgecolor="black",
            markeredgewidth=0.7,
            linewidth=LINEWIDTH,
            markersize=MARKERSIZE,
            label=name
        )

    ax.set_xlim(JV_V_MIN, JV_V_MAX)
    ax.set_ylim(JV_J_MIN, JV_J_MAX)

    if JV_Y_LOG:
        style_log_y(ax)
    else:
        ax.yaxis.set_major_locator(MaxNLocator(nbins=5, integer=True))
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))

    v_step = auto_voltage_tick_step(JV_V_MIN, JV_V_MAX)
    ax.xaxis.set_major_locator(MultipleLocator(v_step))
    ax.xaxis.set_minor_locator(MultipleLocator(max(1, v_step / 2)))

    # Use black styling for the entire J-V y-axis
    style_axes(
        ax,
        xlabel="Voltage (V)",
        ylabel="Current density (mA/cm$^2$)",
        x_color="black",
        y_color="black"
    )

    for side in ["left", "right", "bottom", "top"]:
        ax.spines[side].set_color("black")
        ax.spines[side].set_linewidth(SPINE_WIDTH)

    ax.tick_params(
        axis="y",
        which="major",
        colors="black",
        labelcolor="black"
    )

    ax.tick_params(
        axis="y",
        which="minor",
        colors="black"
    )

    ax.yaxis.label.set_color("black")

    add_legend(ax)

    save_figure(fig, save_path)


def plot_xy(
    datasets,
    xcol,
    ycol,
    xlabel,
    ylabel,
    save_path,
    x_min=None,
    x_max=None,
    y_min=None,
    y_max=None,
    xlog=False,
    ylog=False,
    use_voltage_filter=False,
    color_mode="default",
    marker_mode="triangle"
):
    """Create a general-purpose XY plot."""

    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)

    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    for i, (name, df) in enumerate(datasets.items()):
        d = df.copy()

        if use_voltage_filter:
            d = filter_voltage(d, JVL_V_MIN, JVL_V_MAX)

        if xlog:
            d = d[d[xcol] > 0]

        if ylog:
            d = d[d[ycol] > 0]

        if x_min is not None:
            d = d[d[xcol] >= x_min]

        if x_max is not None:
            d = d[d[xcol] <= x_max]

        if y_min is not None:
            d = d[d[ycol] >= y_min]

        if y_max is not None:
            d = d[d[ycol] <= y_max]

        if d.empty:
            continue

        if color_mode == "ce_lum":
            c = CE_LUM_COLORS[i % len(CE_LUM_COLORS)]
        elif color_mode == "ce_j":
            c = CE_J_COLORS[i % len(CE_J_COLORS)]
        elif color_mode == "eqe":
            c = EQE_COLORS[i % len(EQE_COLORS)]
        elif color_mode == "jv":
            c = JV_COLORS[i % len(JV_COLORS)]
        elif color_mode == "jvl_lum":
            c = JVL_LUM_COLORS[i % len(JVL_LUM_COLORS)]
        elif color_mode == "jvl_j":
            c = JVL_J_COLORS[i % len(JVL_J_COLORS)]
        else:
            c = DEFAULT_COLORS[i % len(DEFAULT_COLORS)]

        if marker_mode == "diamond":
            m = "D"
        elif marker_mode == "circle":
            m = "o"
        elif marker_mode == "eqe":
            m = EQE_MARKER
        elif marker_mode == "ce":
            m = CE_MARKER
        else:
            m = "^"

        ax.plot(
            d[xcol],
            d[ycol],
            marker=m,
            linestyle="-",
            color=c,
            markerfacecolor=c,
            markeredgecolor="black",
            markeredgewidth=0.7,
            linewidth=LINEWIDTH,
            markersize=MARKERSIZE,
            label=name
        )

    if xlog:
        style_log_x(ax)

    if ylog:
        style_log_y(ax)

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    if not xlog:
        ax.xaxis.set_major_locator(MaxNLocator(nbins=5, integer=True))
        ax.xaxis.set_minor_locator(AutoMinorLocator(2))

    if not ylog:
        ax.yaxis.set_major_locator(MaxNLocator(nbins=5))
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))

    style_axes(
        ax,
        xlabel=xlabel,
        ylabel=ylabel,
        x_color="black",
        y_color="black"
    )

    for side in ["left", "right", "bottom", "top"]:
        ax.spines[side].set_color("black")
        ax.spines[side].set_linewidth(SPINE_WIDTH)

    add_legend(ax)

    save_figure(fig, save_path)


# ============================================================
# Main program
# ============================================================

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    datasets = load_all_files(DATA_DIR)

    use_v_filter = APPLY_VRANGE_TO_ALL

    # 1. JVL plot
    plot_jvl(
        datasets,
        os.path.join(OUTPUT_DIR, "1_JVL_transparent.png")
    )

    # 2. J-V plot
    plot_jv(
        datasets,
        os.path.join(OUTPUT_DIR, "2_JV_transparent.png")
    )

    # 3. Current efficiency vs luminance
    plot_xy(
        datasets,
        xcol="luminance",
        ycol="efficiency",
        xlabel="Luminance (cd/m$^2$)",
        ylabel="Current efficiency (cd/A)",
        save_path=os.path.join(OUTPUT_DIR, "3_CE_vs_Luminance_transparent.png"),
        x_min=CE_LUM_X_MIN,
        x_max=CE_LUM_X_MAX,
        y_min=CE_LUM_Y_MIN,
        y_max=CE_LUM_Y_MAX,
        xlog=CE_LUM_X_LOG,
        ylog=CE_LUM_Y_LOG,
        use_voltage_filter=use_v_filter,
        color_mode="ce_lum",
        marker_mode="ce"
    )

    # 4. Current efficiency vs current density
    plot_xy(
        datasets,
        xcol="current_density",
        ycol="efficiency",
        xlabel="Current density (mA/cm$^2$)",
        ylabel="Current efficiency (cd/A)",
        save_path=os.path.join(OUTPUT_DIR, "4_CE_vs_CurrentDensity_transparent.png"),
        x_min=CE_J_X_MIN,
        x_max=CE_J_X_MAX,
        y_min=CE_J_Y_MIN,
        y_max=CE_J_Y_MAX,
        xlog=CE_J_X_LOG,
        ylog=CE_J_Y_LOG,
        use_voltage_filter=use_v_filter,
        color_mode="ce_j",
        marker_mode="ce"
    )

    # 5. EQE vs current density
    plot_xy(
        datasets,
        xcol="current_density",
        ycol="eqe",
        xlabel="Current density (mA/cm$^2$)",
        ylabel="EQE (%)",
        save_path=os.path.join(OUTPUT_DIR, "5_EQE_vs_CurrentDensity_transparent.png"),
        x_min=EQE_J_X_MIN,
        x_max=EQE_J_X_MAX,
        y_min=EQE_J_Y_MIN,
        y_max=EQE_J_Y_MAX,
        xlog=EQE_J_X_LOG,
        ylog=EQE_J_Y_LOG,
        use_voltage_filter=use_v_filter,
        color_mode="eqe",
        marker_mode="eqe"
    )

    print("\nFinished. Figures were saved to:")
    print(OUTPUT_DIR)


if __name__ == "__main__":
    main()