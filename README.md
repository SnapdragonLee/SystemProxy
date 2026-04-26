# SystemProxy

![GitHub stars](https://img.shields.io/github/stars/SnapdragonLee/SystemProxy?style=flat-square)
![GitHub last commit](https://img.shields.io/github/last-commit/SnapdragonLee/SystemProxy?style=flat-square)
![License](https://img.shields.io/github/license/SnapdragonLee/SystemProxy?style=flat-square)

A simple automation project that aggregates public proxy sources and exports Clash compatible subscription files.

## Table of Contents
- [Overview](#overview)
- [Subscription Files](#subscription-files)
- [Quick Start](#quick-start)
- [Run Locally](#run-locally)
- [Repository Structure](#repository-structure)
- [Notes](#notes)
- [License](#license)

## Overview

`SystemProxy` collects public proxy endpoints from the open internet and converts them into Clash configuration files.
It is useful for users who want a continuously refreshed subscription without manually merging multiple sources.

The repository currently includes both the generator scripts and the generated output files in `dist/`.

## Subscription Files

Available generated files:

- `dist/clash_config.yaml`
- `dist/clash_config_extra.yaml`
- `dist/clash_config_extra_US.yaml`

Raw GitHub URLs:

- `https://raw.githubusercontent.com/SnapdragonLee/SystemProxy/master/dist/clash_config.yaml`
- `https://raw.githubusercontent.com/SnapdragonLee/SystemProxy/master/dist/clash_config_extra.yaml`
- `https://raw.githubusercontent.com/SnapdragonLee/SystemProxy/master/dist/clash_config_extra_US.yaml`

## Quick Start

1. Open your Clash compatible client.
2. Import one of the raw subscription URLs above.
3. Refresh the profile when you want the latest generated proxy list.

For most users, `clash_config.yaml` is the safest default.

## Run Locally

### Prerequisites

- Python 3.9+
- `pip`

### Install dependencies

```bash
pip install -r requirements.txt
```

### Generate configs

```bash
python clash.py
python clash_extra.py
```

After the scripts finish, import the generated files from `./dist/` into your client.

### Automated updates

The repository includes `.github/workflows/main.yml`, which suggests updates can be refreshed automatically with GitHub Actions.

## Repository Structure

```text
.
├── .github/workflows/main.yml
├── clash.py
├── clash_extra.py
├── clash.config.template.yaml
├── blacklists.txt
├── dist/
│   ├── clash_config.yaml
│   ├── clash_config_extra.yaml
│   └── clash_config_extra_US.yaml
└── requirements.txt
```

## Notes

- All proxies are collected from public internet sources, so availability and safety can change at any time.
- Review the generated config before using it in a production or privacy-sensitive environment.
- If maintainers want, a future README pass could also add source provenance and update schedule details.

## License

This project is distributed under the MIT License.
