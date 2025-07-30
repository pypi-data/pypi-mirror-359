from yw_core.yw_core import extract_code_cells, extract_records, records2annotations
import click, sys, os

@click.command()
@click.option('--filepath', '-f', required=True, type=str, help='Path of a Python notebook to extract YesWorkflow annotations')
@click.option('--upper', '-u', is_flag=True, show_default=True, default=False, help='Extract upper estimate of cell I/O sets for YesWorkflow annotations')
def main(filepath, upper):
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File '{filepath}' not found")
    code_cells = extract_code_cells(filepath)
    records = extract_records(code_cells, is_upper_estimate=upper)
    annotations = records2annotations(records)
    print(annotations)
