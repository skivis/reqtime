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
    
    times = []
    
    try:
        start = default_timer()
        index = count
        while True:
            response = http.get(url)
            elapsed = response.elapsed.total_seconds()
            status = response.status_code
            times.append(elapsed)
            output = f'{elapsed:.4f}'
            if threshold > 0:
                color = 'bright_green' if int(elapsed * 1000) <= threshold else 'bright_red'
                output = style(output, fg=color)
            echo(f'{output} ({style(str(status), fg="bright_black")})')
            
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
        
        if not summary or not times:
            return

        table = [
            ['# Reqs','Median (sec)', 'Average (sec)', 'Total time'],
            [
                len(times),
                round(median(times), 4),
                round(mean(times), 4),
                round(end - start, 4)
            ]
        ]

        print()
        print(tabulate(table, tablefmt='psql', headers="firstrow"))
    

if __name__ == '__main__':
    cli()
