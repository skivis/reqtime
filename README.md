# Reqtime
Simple script for measuring (GET) request durations and get the median and average numbers.

## Prerequisite

Python 3.7+ installed

## Installation

```sh
$ pip install git+https://github.com/skivis/reqtime.git
```

## Usage

Run `reqtime --help` for information on supported flags and such.

```sh
$ reqtime -s http://example.com
(200)    362.30 ms
(200)    205.95 ms
(200)    204.85 ms
(200)    205.80 ms
(200)    209.07 ms
(200)    204.46 ms
(200)    208.09 ms
(200)    199.52 ms
(200)    202.22 ms
(200)    201.51 ms
(200)    204.63 ms
(200)    201.09 ms
(200)    200.37 ms

http://example.com
+----------+---------------+-------------+------------+------------+------------+
|     Reqs |   Median (ms) |   Mean (ms) |   Min (ms) |   Max (ms) |   P90 (ms) |
|----------+---------------+-------------+------------+------------+------------|
|       13 |        204.63 |      216.14 |     199.52 |     362.30 |     209.07 |
+----------+---------------+-------------+------------+------------+------------+
```

## Uninstall
```sh
$ pip uninstall reqtime
```