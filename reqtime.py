from statistics import median, mean
from timeit import default_timer

import requests
from click import command, option, argument, style, echo
from tabulate import tabulate



@command()
@option('-c', '--count', default=0, type=int, help='Number of requests to run, defaults to infinite')
@option('-t', '--threshold', default=0, type=int, help='Threshold in ms for marking a request as slow')
@option('-p', '--persistent', is_flag=True, help='Use a persistent http connection for all requests')
@option('-s', '--summary', is_flag=True, help='Output summary when done (or stopped)')
@option('-v', '--verbose', is_flag=True, help='Turn on DEBUG logging')
@argument('url')
def cli(count, threshold, persistent, summary, verbose, url):
    if verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        for package in ['urllib3', 'requests']:
            logging.getLogger(package).setLevel(logging.DEBUG)

    if persistent:
        http = requests.Session()
    else:
        http = requests
    
    durations = []
    
    try:
        start = default_timer()
        index = count
        while True:
            response = http.get(url)
            elapsed = response.elapsed.total_seconds() * 1000
            status = response.status_code
            durations.append(elapsed)
            output = f'{elapsed:.2f}'
            if threshold > 0:
                color = 'bright_green' if int(elapsed) <= threshold else 'bright_red'
                output = style(f'{output:^14}', fg=color)
            else:
                output = f'{output:^14}'
            
            echo(f'({style(str(status), fg="bright_black")}) {output}')
            
            if count == 0:
                continue
            index -= 1
            if index == 0:
                break
    except KeyboardInterrupt:
        pass
    finally:
        end = default_timer()
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
