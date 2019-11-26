# Reqtime
Simple script for measuring (GET) request durations and get the median and average numbers.

## Prerequisite

Python 3.6+ installed

## Installation

```sh
$ pip install git+https://github.com/skivis/reqtime.git
```

## Usage
```sh
$ reqtime --help
$ reqtime --summary http://example.com
$ reqtime -c20 -t300 -s http://example.com
```

## Uninstall
```sh
$ pip uninstall reqtime
```