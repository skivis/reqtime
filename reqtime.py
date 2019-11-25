import logging
from datetime import datetime
from statistics import median, mean

import click
import requests
from tabulate import tabulate

times = []


def do_request(http, url: str, threshold: int) -> None:
    global times

    response = http.get(url)
    elapsed = response.elapsed.total_seconds()
    times.append(elapsed)
    cls = 'green' if int(elapsed * 1000) <= threshold else 'red'
    click.echo(click.style(f'{elapsed:.4f}', fg=cls))


@click.command()
@click.argument('url')
@click.option('--count', default=0, type=int, help='number of requests')
@click.option('--threshold', default=300, type=int, help='number of requests')
@click.option('--session', is_flag=True, help='Use same http session for all requests')
@click.option('--summary', is_flag=True, help='Output summary when stopped')
@click.option('--verbose', is_flag=True, help='Output more than nessecary')
def cli(url, count, threshold, session, summary, verbose):
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger("urllib3").setLevel(logging.DEBUG)

    if session:
        http = requests.Session()
    else:
        http = requests
    
    try:
        if count > 0:
            for i in range(count):
                do_request(http, url, threshold)
        else:
            while True:
                do_request(http, url, threshold)
    except KeyboardInterrupt:
        pass
    finally:
        if hasattr(http, 'close'):
            http.close()

        global times
        
        if not summary or not times:
            return

        table = [
            [
                len(times),
                round(median(times), 4),
                round(mean(times), 4)
            ]
        ]

        print()
        print(tabulate(
            table,
            headers=['# Reqs', 'Median (sec)', 'Average (sec)'],
            tablefmt='psql'))
    

if __name__ == '__main__':
    cli()
