from statistics import median, mean
from timeit import default_timer as timer

import requests
from click import UsageError, command, option, argument, style, echo
from tabulate import tabulate


SUPPORTED_HTTP_METHODS = ['GET', 'POST']


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

    echo(f'({style(str(status), fg="bright_black")}) {output} {style("ms", fg="bright_black")}')


def print_summary(title, durations, runtime):
    table = [
        ['# Reqs', 'Median (ms)', 'Mean (ms)', 'Runtime (sec)'],
        [
            len(durations),
            median(durations),
            mean(durations),
            runtime
        ]
    ]

    echo(f'\n{title}')
    echo(tabulate(table, tablefmt='psql', headers="firstrow", floatfmt=".2f"))


@command()
@argument('args', nargs=-1, metavar='<METHOD> <URL>')
@option('-c', '--count', default=0, type=int, help='Number of requests to run, defaults to infinite')
@option('-t', '--threshold', default=0, type=int, help='Threshold in ms for marking a request as slow')
@option('-p', '--persistent', is_flag=True, help='Use a persistent http connection for all requests')
@option('-s', '--summary', is_flag=True, help='Output summary when done (or stopped)')
@option('-v', '--verbose', is_flag=True, help='Turn on DEBUG logging')
def cli(args, count, threshold, persistent, summary, verbose):
    method, url = parse_args(args)
    durations = []
    
    if verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('urllib3').setLevel(logging.DEBUG)

    http = requests.Session() if persistent else requests

    try:
        func = getattr(http, method)
        index = count
        start = timer()
        while True:
            r = func(url)
            elapsed = r.elapsed.total_seconds() * 1000
            durations.append(elapsed)
            
            println(r.status_code, elapsed, threshold)
            
            if count == 0:
                continue
            index -= 1
            if index == 0:
                break
    except KeyboardInterrupt:
        pass
    finally:
        end = timer()
        if hasattr(http, 'close'):
            http.close()
        
        if not summary or not durations:
            return

        runtime = end - start
        print_summary(url, durations, runtime)
    

if __name__ == '__main__':
    cli()
