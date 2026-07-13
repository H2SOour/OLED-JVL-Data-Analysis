# OLED JVL Data Plotter

[![DOI](https://zenodo.org/badge/1298731714.svg)](https://doi.org/10.5281/zenodo.21330070)

A Python toolkit for batch-processing electrical and optical characterization data from OLEDs and other LED-based devices, with automated generation of publication-ready J–V–L, current-efficiency, and EQE plots.

<img width="1594" height="846" alt="ScreenShot_2026-07-13_121926_316" src="https://github.com/user-attachments/assets/de1d5031-8cca-4c86-aab9-b1dbdee6ff05" />

## Overview

The script reads compatible CSV files from a selected directory and generates:

1. **J–V–L plot** — voltage vs luminance and current density
2. **J–V plot** — voltage vs current density
3. **Current efficiency vs luminance**
4. **Current efficiency vs current density**
5. **EQE vs current density**

The plotting style, axis limits, logarithmic scales, markers, color palettes, legends, resolution, and transparency can be adjusted in the configuration section of the script.

## Features

- Batch processing of multiple CSV files
- Automatic detection of the actual CSV header row
- Support for UTF-8, Shift-JIS, CP932, and GBK encodings
- Automatic selection of `Actual luminance` or `Relative luminance`
- Independent control of axis ranges and logarithmic scales
- Optional voltage-range filtering for efficiency and EQE plots
- High-resolution PNG output
- Optional transparent figure backgrounds
- Distinct color palettes for different plot types
- Automatic skipping of incompatible files while continuing with valid files
- Automatic use of CSV filenames as data-series labels

## Repository Structure

```text
OLED-JVL-Data-Plotter/
├── oled_jvl_plotter.py
├── README.md
├── requirements.txt
├── LICENSE
├── CITATION.cff
├── data/
│   ├── sample_01.csv
│   └── sample_02.csv
└── output/
```

The `data/` and `output/` folders are relative to the directory from which the script is executed. These paths can be changed in the configuration section.

## Requirements

- Python 3.9 or later
- NumPy
- pandas
- Matplotlib

Install the dependencies with:

```bash
pip install -r requirements.txt
```

Alternatively:

```bash
pip install numpy pandas matplotlib
```

## Input Data Format

Place the measurement CSV files in the `data/` directory.

The script searches for a row containing `Drive voltage` and uses that row as the table header. Instrument metadata may therefore appear above the data table.

Each CSV file must contain columns whose names include the following keywords:

| Required quantity | Keyword searched by the script |
|---|---|
| Voltage | `Drive voltage` |
| Current density | `Current density` |
| External quantum efficiency | `EQE` |
| Current efficiency | `Luminous efficacy` |
| Luminance | `Actual luminance` or `Relative luminance` |

Column matching is case-insensitive and allows additional text in the column names.

### Important Note About Current Efficiency

The script currently reads the column containing `Luminous efficacy` and plots it as **Current efficiency (cd/A)**.

Before using the results, confirm that this column in your instrument export actually represents current efficiency in cd/A.

If your CSV uses a column named `Current efficiency`, change:

```python
col_eff = find_col(df.columns, "Luminous efficacy")
```

to:

```python
col_eff = find_col(df.columns, "Current efficiency")
```

## Configuration

Open `oled_jvl_plotter.py` and edit the parameters near the beginning of the file.

### Input and Output Directories

```python
DATA_DIR = "./data"
OUTPUT_DIR = "./output"
```

Absolute paths can also be used:

```python
DATA_DIR = "/path/to/your/csv/files"
OUTPUT_DIR = "/path/to/save/figures"
```

### Voltage Filtering

```python
APPLY_VRANGE_TO_ALL = True
```

- `True`: the selected voltage range is also applied to CE–L, CE–J, and EQE–J plots.
- `False`: voltage filtering is applied only to the J–V–L and J–V plots.

### Axis Ranges

Example:

```python
JVL_V_MIN, JVL_V_MAX = 0, 30
JVL_LUM_MIN, JVL_LUM_MAX = 1, 1e4
JVL_J_MIN, JVL_J_MAX = 0, 16
```

Because luminance is displayed on a logarithmic axis in the J–V–L plot, the minimum luminance value must be greater than zero.

### EQE Scaling

```python
EQE_SCALE = 1
```

Use:

- `EQE_SCALE = 1` when a value such as `2.5` means `2.5%`
- `EQE_SCALE = 100` when a value such as `0.025` means `2.5%`

### Figure Export

```python
DPI = 600
TRANSPARENT = True
```

Set `TRANSPARENT = False` for an opaque background.

### Legends

```python
SHOW_LEGEND = True
LEGEND_LOC = "best"
LEGEND_FRAME = False
```

## Usage

From the repository directory, run:

```bash
python oled_jvl_plotter.py
```

The script prints the filename and number of valid rows for each successfully loaded dataset. Files that do not match the expected format are skipped, and the reason is printed in the terminal.

## Output Files

The script generates:

```text
1_JVL_transparent.png
2_JV_transparent.png
3_CE_vs_Luminance_transparent.png
4_CE_vs_CurrentDensity_transparent.png
5_EQE_vs_CurrentDensity_transparent.png
```

Each CSV filename, without its extension, is used as the corresponding data-series label.

## Troubleshooting

### No CSV Files Found

Confirm that:

- `DATA_DIR` points to the correct directory
- the input files use the `.csv` extension
- the script is being run from the expected working directory when relative paths are used

### Header Row Not Found

The CSV must contain a row with the text `Drive voltage`. Modify `find_header_row()` if your instrument uses a different voltage-column name.

### Missing Required Columns

Check the column names against the table in the **Input Data Format** section. The keywords used in `load_one_file()` can be modified to support different export formats.

### Empty Logarithmic Plots

Logarithmic axes cannot display zero or negative values. The script removes non-positive values for log-scaled variables. Confirm that the selected axis limits overlap with the valid data range.

### EQE Values Appear 100 Times Too Small or Too Large

Adjust `EQE_SCALE` according to whether the original data stores EQE as a fraction or as a percentage.

## Intended Use and Scientific Validation

This toolkit is intended for research and engineering workflows involving OLED and other LED-based devices.

Measurement systems, column names, units, calibration methods, and export formats vary between laboratories. Users are responsible for verifying:

- column definitions
- physical units
- device area
- EQE scaling
- current-efficiency definitions
- instrument calibration
- suitability of the generated plots for publication or quantitative comparison

The author does not guarantee that the default configuration is appropriate for every measurement system.

## Development note

This toolkit was developed from a practical OLED characterization workflow and implemented with the assistance of AI-based coding tools.

The scientific requirements, data-processing workflow, calculation logic, validation, testing, and documentation were defined and reviewed by the author. Users are encouraged to independently verify calculated results before using them in publications.

## Citation

If you use this toolkit in academic research, publications, presentations, theses, reports, or publicly distributed analysis workflows, please cite this repository and acknowledge the author.

Suggested citation:

> Siyuan Liu, *OLED JVL Data Plotter*, version 0.1.0, 2026. GitHub repository.

For easier citation, this repository should also include a `CITATION.cff` file. After a stable release is published, a DOI may be created through Zenodo.

## License

This project is licensed under the MIT License.

You may use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software, provided that the original copyright notice and license notice are retained in copies or substantial portions of the software.

See the `LICENSE` file for the full license text.

## Copyright

Copyright © 2026 Siyuan Liu.

The copyright and license notices must be retained in copies or substantial portions of this software.

## Author

**Siyuan Liu**  
PhD Candidate, The University of Tokyo

## Development Status

This project is under active development.

Planned future improvements may include:

- automatic extraction of turn-on voltage
- maximum luminance, current efficiency, and EQE
- batch statistical comparison
- error bars and standard-deviation analysis
- OLED lifetime analysis
- LT95, LT90, LT80, and LT50 extraction
- automated report generation
- graphical user interface
