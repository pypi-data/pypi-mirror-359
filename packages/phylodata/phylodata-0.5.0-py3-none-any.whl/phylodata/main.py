import click
import subprocess
from phylodata.data_types import validate_json, get_schema


@click.group()
def phylodata(): ...


@phylodata.command(help="Process an experiment before uploading it to PhyloData.")
def process():
    subprocess.Popen(["streamlit", "run", "phylodata/ui.py"])


@phylodata.command(
    help="Validate if a given JSON file contains valid PhyloData metadata."
)
@click.argument("file_path", type=click.Path(exists=True))
def validate(file_path: str):
    validate_json(file_path)
    print("File is valid!")


@phylodata.command(help="Prints the JSON schema for valid PhyloData metadata files.")
def schema():
    print(get_schema())
