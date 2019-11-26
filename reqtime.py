from statistics import median, mean
from timeit import default_timer as timer

import click
import requests
from tabulate import tabulate


times = []


def do_request(http, url: str, threshold: int) -> None:
    global times

    response = http.get(url)
    elapsed = response.elapsed.total_seconds()
    times.append(elapsed)
    output = f'{elapsed:.4f}'
    if threshold > 0:
        color = 'green' if int(elapsed * 1000) <= threshold else 'red'
        output = click.style(output, fg=color)
    click.echo(output)


@click.command()
@click.option('-c', '--count', default=0, type=int, help='Number of requests to run, defaults to infinite')
@click.option('-t', '--threshold', default=0, type=int, help='Threshold in ms for marking a request as slow')
@click.option('-p', '--persistent', is_flag=True, help='Use a persistent http connection for all requests')
@click.option('-s', '--summary', is_flag=True, help='Output summary when done (or stopped)')
@click.option('-v', '--verbose', is_flag=True, help='Turn on DEBUG logging')
@click.argument('url')
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
    
    try:
        start = timer()
        index = count
        while True:
            do_request(http, url, threshold)
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

        global times
        
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
