import os
import shutil
from io import BytesIO

import msgspec
from streamlit.runtime.uploaded_file_manager import UploadedFile

from phylodata.data_types import PaperWithExperiment

WASABI_BUCKET_NAME = "phylodata-experiments"


def create_output_folder(
    title: str,
    beast2_configuration: BytesIO,
    beast2_logs: BytesIO,
    beast2_trees: BytesIO,
    other_files: list[UploadedFile],
    paper_with_experiment: PaperWithExperiment,
) -> str:
    """
    Creates a folder with a name based on the given title and writes the provided
    files and the PhyloData metadata into it.
    """
    output_folder = f"{title}-phylodata"

    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.mkdir(output_folder)

    with open(f"{output_folder}/phylodata_metadata.json", "wb") as f:
        f.write(
            msgspec.json.format(msgspec.json.encode(paper_with_experiment), indent=2)
        )

    used_filenames = set("phylodata_metadata.json")
    all_files = [beast2_configuration, beast2_logs, beast2_trees] + other_files

    for file in all_files:
        filename = file.name
        base, ext = os.path.splitext(file.name)

        while filename in used_filenames:
            filename = f"{base}_{len(used_filenames)}{ext}"

        used_filenames.add(filename)
        with open(f"{output_folder}/{filename}", "wb") as f:
            f.write(file.getbuffer())

    return output_folder
