from statistics import median, mean
from timeit import default_timer as timer

import requests
from click import command, option, argument, style, echo, UsageError
from tabulate import tabulate


SUPPORTED_HTTP_METHODS = ['GET', 'POST', 'EOD']


def log(status: int, elapsed: float, threshold: int):
    output = f'{elapsed:9.2f}'
    if threshold > 0:
        color = 'bright_green' if int(elapsed) <= threshold else 'bright_red'
        output = style(output, fg=color)
    
    echo(f'({style(str(status), fg="bright_black")}) {output}')


@command()
@argument('args', nargs=-1)
@option('-c', '--count', default=0, type=int, help='Number of requests to run, defaults to infinite')
@option('-t', '--threshold', default=0, type=int, help='Threshold in ms for marking a request as slow')
@option('-p', '--persistent', is_flag=True, help='Use a persistent http connection for all requests')
@option('-s', '--summary', is_flag=True, help='Output summary when done (or stopped)')
@option('-v', '--verbose', is_flag=True, help='Turn on DEBUG logging')
def cli(args, count, threshold, persistent, summary, verbose):
    if not args or len(args) > 2:
        raise UsageError('Incorrect argument, either specify <METHOD> <url> or just <url>')

    try:
        method, url = args
        if method not in SUPPORTED_HTTP_METHODS:
            raise UsageError(f'Unsupported HTTP method: {method}')
    except ValueError:
        method = 'GET'
        url = args[0]
    
    if verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('urllib3').setLevel(logging.DEBUG)

    if persistent:
        http = requests.Session()
    else:
        http = requests
    
    durations = []
    
    try:
        func = getattr(http, method.lower())
        start = timer()
        index = count
        while True:
            r = func(url)
            elapsed = r.elapsed.total_seconds() * 1000
            durations.append(elapsed)
            
            log(r.status_code, elapsed, threshold)
            
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

        table = [
            ['# Reqs', 'Median (ms)', 'Mean (ms)', 'Runtime (sec)'],
            [
                len(durations),
                round(median(durations), 2),
                round(mean(durations), 2),
                round(end - start, 2)
            ]
        ]

        print()
        print(tabulate(table, tablefmt='psql', headers="firstrow"))
    

if __name__ == '__main__':
    cli()
