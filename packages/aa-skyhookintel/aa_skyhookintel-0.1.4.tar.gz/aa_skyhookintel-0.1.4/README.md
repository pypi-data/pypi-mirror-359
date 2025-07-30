# Skyhook Intel

AA module for gathering skyhook timers.

[![release](https://img.shields.io/pypi/v/aa-skyhookintel?label=release)](https://pypi.org/project/aa-skyhookintel/)
[![python](https://img.shields.io/pypi/pyversions/aa-skyhookintel)](https://pypi.org/project/aa-skyhookintel/)
[![django](https://img.shields.io/pypi/djversions/aa-skyhookintel?label=django)](https://pypi.org/project/aa-skyhookintel/)
[![license](https://img.shields.io/badge/license-MIT-green)](https://gitlab.com/r0kym/aa-skyhookintel/-/blob/master/LICENSE)

## Features:

- Load skyhooks in a constellation/region through admin commands
- Displays Skyhooks with and without timers in separate tables
- Extracts data from the information on the skyhook in space window that can be copied to a clipboard
- Automatically populates times in the timberboard or structuretimers application

### Screenshots

## Installation

### Step 1 - Check prerequisites

Skyhook Intel is a plugin for Alliance Auth. If you don't have Alliance Auth running already, please install it first before proceeding. (see the official [AA installation guide](https://allianceauth.readthedocs.io/en/latest/installation/auth/allianceauth/) for details)

### Step 2 - Install app

Make sure you are in the virtual environment (venv) of your Alliance Auth installation. Then install the newest release from PyPI:

```bash
pip install aa-skyhookintel
```

### Step 3 - Configure Auth settings

Configure your Auth settings (`local.py`) as follows:

- Add `'skyhookintel'` to `INSTALLED_APPS`

### Step 4 - Finalize App installation

Run migrations & copy static files

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

Restart your supervisor services for Auth.

### Step 5 - Load data

You can load data using 2 commands depending on the area you want to cover.
Commands can take some time to execute so avoid loading an entire region if you only need a few systems.

#### Region:

```shell
python manage.py skyhook_intel_create_region [[region_id]]
```

#### Constellation:

```shell
python manage.py skyhook_intel_create_constellation [[constellation_id]]
```

Once the data is loaded you can add skyhooks owners using in the admin panel.

## Settings

| Name                               | Description                                                                           | Default value |
|------------------------------------|---------------------------------------------------------------------------------------|---------------|
| SKYHOOK_INTEL_POPULATE_TIMERBOARDS | If the application should try to find known timerboards and populate them with timers | True          |
