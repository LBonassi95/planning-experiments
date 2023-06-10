import click
import json
import os
from planning_experiments.data_processor.utils import *
from planning_experiments.data_processor.logs_parser import LogsParser



@click.command()
@click.argument('info_path')
@click.argument('output_path')
def main(info_path, output_path):

    info = json.load(open(info_path, 'r'))
    df = LogsParser(info).logs2df()
    df.to_csv(output_path, index=False)


if __name__ == '__main__':
    main()