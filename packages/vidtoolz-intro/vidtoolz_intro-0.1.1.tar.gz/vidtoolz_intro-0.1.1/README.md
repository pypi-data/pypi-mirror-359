# vidtoolz-intro

[![PyPI](https://img.shields.io/pypi/v/vidtoolz-intro.svg)](https://pypi.org/project/vidtoolz-intro/)
[![Changelog](https://img.shields.io/github/v/release/sukhbinder/vidtoolz-intro?include_prereleases&label=changelog)](https://github.com/sukhbinder/vidtoolz-intro/releases)
[![Tests](https://github.com/sukhbinder/vidtoolz-intro/workflows/Test/badge.svg)](https://github.com/sukhbinder/vidtoolz-intro/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/sukhbinder/vidtoolz-intro/blob/main/LICENSE)

Create intro video from a series of videos

## Installation

First install [vidtoolz](https://github.com/sukhbinder/vidtoolz).

```bash
pip install vidtoolz
```

Then install this plugin in the same environment as your vidtoolz application.

```bash
vidtoolz install vidtoolz-intro
```
## Usage

type ``vid intro --help`` to get help

```bash
usage: vid intro [-h] [-t TEXTFILE] [-i INPUT] [-o OUTPUT] [-cd CHANGE_DIR]

Create intro video from a series of videos

optional arguments:
  -h, --help            show this help message and exit
  -t TEXTFILE, --textfile TEXTFILE
                        Text file containg. IMG102.mov,1,5 IMG200.mov,2,4
  -i INPUT, --input INPUT
                        Input like IMG102.mov,1,5
  -o OUTPUT, --output OUTPUT
                        Output filename, default None
  -cd CHANGE_DIR, --change-dir CHANGE_DIR
                        if Provided, go to this folder

```
## Example

```bash
 vid intro -i "small.mp4,1,3" -i "small.mp4,8,10" -cd /tmp
```
produces `small_intro.mp4` and `small_intro.mp4.txt` in the same folder as `small.mp4`

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:
```bash
cd vidtoolz-intro
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
