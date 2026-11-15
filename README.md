# Lunar Landing Site Navigator

A NASA Space Apps project for evaluating lunar landing sites using real astronomical and terrain data.

The application combines:

- Real NASA SPICE ephemeris calculations for the Sun and Earth
- Real LOLA lunar terrain data
- Terrain-aware horizon and visibility calculations
- Lunar landing-site analysis
- Mission timeline and lighting/communication metrics
- Landing-site comparison
- Custom landing locations
- Terrain/visibility heatmaps
- Lunar horizon geometry visualization
- PDF mission reports

## 1. Clone the Repository

```bash
git clone https://github.com/shivam8368215871-sys/lunar-landing-site-navigator.git
cd lunar-landing-site-navigator
```

## 2. Check Required Software

The project is developed and tested on Linux/Arch Linux.

You should have:

- Python 3.13+
- Git
- wget
- Qt/PySide6-compatible desktop environment

Check the basic tools:

```bash
python --version
git --version
wget --version
```

## 3. Create the Python Virtual Environment

From the project directory:

```bash
python -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

After activation, your terminal should show `(.venv)`.

## 4. Install Python Dependencies

Install the project dependencies:

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not present in your checkout, install the dependencies listed by the project's current environment or contact the project maintainer.

## 5. Download the Required SPICE Kernels

The SPICE kernels are intentionally **not stored in Git** because they are large NASA data files.

The repository contains a setup script that downloads the required kernel set.

Run:

```bash
chmod +x download-kernels.sh
./download-kernels.sh
```

The script verifies these required files:

```text
data/kernels/de440s.bsp
data/kernels/moon_pa_de440_200625.bpc
data/kernels/naif0012.tls
data/kernels/pck00011.tpc
```

If the files already exist, the script keeps them and reports them as ready.

## 6. Terrain Data

The project also uses lunar terrain data under:

```text
data/terrain/
```

Large terrain data files are intentionally excluded from Git.

Make sure the required terrain/LOLA data used by your project is available in the expected `data/terrain/` location before running terrain-dependent analysis.

## 7. Run the Application

Make sure the virtual environment is active:

```bash
source .venv/bin/activate
```

Run the application from the repository root:

```bash
python -m app.main
```

### Important

Use:

```bash
python -m app.main
```

rather than:

```bash
python app/main.py
```

The project uses the `app` package, so module execution from the repository root is the correct launch method.

## 8. Verify the Installation

Before launching the GUI, you can run a syntax check:

```bash
python -m py_compile     app/ui/compare.py     app/ui/main_window.py     app/science/engine.py
```

You should see no Python errors.

You can also verify the SPICE kernels:

```bash
./download-kernels.sh
```

## 9. Basic Application Workflow

After launching the application:

1. Open the analysis page.
2. Select a lunar landing site.
3. Run the analysis.
4. Review Sun and Earth elevation/azimuth.
5. Review the LOLA terrain horizon and terrain-aware visibility.
6. Open the mission timeline.
7. Review lighting and communication metrics.
8. Use Compare to compare landing sites.
9. Use Custom Location to evaluate another coordinate.
10. Use the heatmap and horizon-geometry views for additional terrain analysis.
11. Export the mission analysis as PDF if required.

## 10. Available Reference Landing Sites

The project currently includes:

- Shackleton Crater
- Cabeus Crater
- Malapert Massif

The Compare page also supports a custom landing location using latitude and longitude.

## 11. Science/Data Architecture

The core analysis follows this pipeline:

```text
NASA SPICE
    ↓
LunarObserver
    ↓
Sun/Earth azimuth + elevation
    ↓
LOLA terrain horizon
    ↓
Terrain-aware visibility
    ↓
Mission analysis
    ↓
Timeline / metrics / comparison / reports
```

The application does not use mocked astronomical positions for the core analysis.

Mission visibility is based on the SPICE-derived body-center elevation compared with the LOLA terrain horizon at the computed body azimuth.

The model does not apply lunar-limb, atmospheric, or refraction corrections.

## 12. Development Checks

From the repository root:

```bash
source .venv/bin/activate
```

Python syntax check:

```bash
python -m py_compile     app/ui/compare.py     app/ui/main_window.py     app/science/engine.py
```

Run the real science regression tests:

```bash
python tests/test_real_science.py
```

Run the horizon reference checks:

```bash
python tests/test_horizons_reference.py
```

Run the real heatmap checks:

```bash
PYTHONPATH=. python tests/test_real_heatmap.py
```

Run the real mission-condition checks:

```bash
python tests/test_real_conditions.py
```

## 13. Git / Large Data Policy

Large NASA data files are not committed to the repository.

The following directories are ignored by Git:

```text
data/kernels/
data/terrain/
```

The SPICE kernel setup is reproducible through:

```bash
./download-kernels.sh
```

This keeps the Git repository lightweight while allowing a fresh clone to recreate the required SPICE kernel set.

## 14. Troubleshooting

### `ModuleNotFoundError: No module named 'app'`

Make sure you are in the repository root:

```bash
cd ~/Documents/vscode/lunar-landing-site-navigator
```

Then run:

```bash
python -m app.main
```

Do not run:

```bash
python app/main.py
```

### SPICE kernel directory not found

Run:

```bash
./download-kernels.sh
```

Then check:

```bash
ls -lh data/kernels
```

You should have:

```text
de440s.bsp
moon_pa_de440_200625.bpc
naif0012.tls
pck00011.tpc
```

### Permission denied for `download-kernels.sh`

Run:

```bash
chmod +x download-kernels.sh
```

Then:

```bash
./download-kernels.sh
```

### Python dependency problems

Make sure the virtual environment is active:

```bash
source .venv/bin/activate
```

Then upgrade pip:

```bash
python -m pip install --upgrade pip
```

and install the project requirements:

```bash
pip install -r requirements.txt
```

## 15. Quick Start

For an already-cloned repository, the typical startup sequence is:

```bash
cd lunar-landing-site-navigator

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

chmod +x download-kernels.sh
./download-kernels.sh

python -m app.main
```

## 16. Repository

GitHub:

https://github.com/shivam8368215871-sys/lunar-landing-site-navigator

## 17. Project Status

Lunar Landing Site Navigator is an actively developed NASA Space Apps project.

The repository is designed so that the source code can be cloned independently of large SPICE and terrain datasets, while the required SPICE kernel set can be recreated using the included download script.

## 13. Screenshots

### Lunar Landing Site Navigator

![Lunar Landing Site Navigator - Screenshot 1](images/Screenshot%20From%202026-11-15%2018-56-09.png)

![Lunar Landing Site Navigator - Screenshot 2](images/Screenshot%20From%202026-11-15%2018-56-18.png)

![Lunar Landing Site Navigator - Screenshot 3](images/Screenshot%20From%202026-11-15%2018-56-29.png)

![Lunar Landing Site Navigator - Screenshot 4](images/Screenshot%20From%202026-11-15%2018-56-39.png)

![Lunar Landing Site Navigator - Screenshot 5](images/Screenshot%20From%202026-11-15%2018-56-47.png)

![Lunar Landing Site Navigator - Screenshot 6](images/Screenshot%20From%202026-11-15%2018-57-15.png)

## 14. Example Mission Output

A generated PDF mission report is included as an example of the application's analysis output.

**Download the example mission report:**

[Download Lunar Landing Mission Report](outputs/lunar-landing-mission-report.pdf)

