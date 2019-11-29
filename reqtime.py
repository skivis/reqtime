import math
from time import sleep
from statistics import median, mean

import requests
from click import UsageError, command, option, argument, style
from tabulate import tabulate


SUPPORTED_HTTP_METHODS = ['GET', 'POST']


def percentile(data, percentile):
    size = len(data)
    return sorted(data)[int(math.ceil((size * percentile) / 100)) - 1]


def parse_args(args):
    if not args or len(args) > 2:
        raise UsageError('Incorrect arguments, either specify <METHOD> <url> or just <url>')
    try:
        method, url = args
        if method not in SUPPORTED_HTTP_METHODS:
            raise UsageError(f'Unsupported HTTP method: {method}')
    except ValueError:
        method = 'GET'
        url = args[0]
    return method.lower(), url


def println(status: int, elapsed: float, threshold: int):
    output = f'{elapsed:9.2f}'
    if threshold > 0:
        color = 'bright_green' if int(elapsed) <= threshold else 'bright_red'
        output = style(output, fg=color)
    status = style(str(status), fg='bright_black')
    millis = style('ms', fg='bright_black')
    print(f'({status}) {output} {millis}')


def display_statistics(data, title='Summary'):
    table = [['# Reqs', 'Median (ms)', 'Mean (ms)', 'Min (ms)', 'Max (ms)',
              'P90 (ms)'],
             [len(data), median(data), mean(data), min(data), max(data),
              percentile(data, 90)]]
    print()
    print(f'{title}')
    print(tabulate(table, headers='firstrow', floatfmt='.2f', tablefmt='psql'))


@command()
@argument('args', nargs=-1, metavar='<METHOD> <URL>')
@option('-c', '--count', default=0, type=int, help='Number of requests to run, defaults to infinite')
@option('-t', '--threshold', default=0, type=int, help='Threshold in ms for marking a request as slow')
@option('-p', '--persistent', is_flag=True, help='Use a persistent http connection for all requests')
@option('-d', '--delay', default=0, type=int, help='Milliseconds to wait between requests')
@option('-s', '--summary', is_flag=True, help='Output summary when done (or stopped)')
def cli(args, count, threshold, persistent, delay, summary):
    method, url = parse_args(args)
    data = []

    http = requests.Session() if persistent else requests

    try:
        func = getattr(http, method)
        index = count
        while True:
            r = func(url)
            elapsed = r.elapsed.total_seconds() * 1000
            data.append(elapsed)
            println(r.status_code, elapsed, threshold)

            if delay != 0 and index != 1:
                sleep(delay / 1000)

            if count == 0:
                continue
            index -= 1
            if index == 0:
                break
    except KeyboardInterrupt:
        pass
    finally:
        if hasattr(http, 'close'):
            http.close()

        if not summary and not data:
            return

        display_statistics(data, title=url)


if __name__ == '__main__':
    cli()
