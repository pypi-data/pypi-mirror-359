from datetime import date

from enum import Enum

import bibtexparser
import streamlit as st

from phylodata.data_types import (
    Experiment,
    ExperimentType,
    FileType,
    Metadata,
    Paper,
    PaperWithExperiment,
)
from phylodata.errors import ValidationError
from phylodata.parsers.parse_beast2_samples import parse_beast2_samples
from phylodata.parsers.parse_evolutionary_model import parse_evolutionary_model
from phylodata.parsers.parse_files import parse_file
from phylodata.parsers.parse_trees import parse_trees
from phylodata.version import __version__
from phylodata.utils.output_utils import create_output_folder


class Stage(str, Enum):
    INPUT = "Input"
    NEXT_STEPS = "Next Steps"


STAGE = "stage"
OUTPUT_FOLDER = "output_folder"

if STAGE not in st.session_state:
    st.session_state[STAGE] = Stage.INPUT


if st.session_state[STAGE] == Stage.INPUT:
    """
    # 🌴 Process Experiment

    Let's process your Bayesian Phylogenetics experiment to prepare it for upload to the PhyloData repository.

    Note that right now, we only support BEAST 2 experiments.

    This usually takes less than five minutes.
    """

    with st.container(border=True):
        """
        ### Paper

        Enter the following general information about your paper:
        """

        title = st.text_input("Title")
        abstract = st.text_area("Abstract")
        authors = st.text_area("Authors (one per line)")
        bibtext = st.text_area("BibTex citation")
        doi = st.text_input("DOI (optional)")
        url = st.text_input("URL (optional)")

    with st.container(border=True):
        """
        ### Experiment

        Optionally, enter some additional information about your experiment. This is useful if you want to register multiple experiments for the same paper.
        """

        experiment_title = st.text_input("Experiment title (optional)")
        experiment_description = st.text_area("Experiment description (optional)")

    with st.container(border=True):
        """
        ### Files

        Select the following files:
        """

        beast2_configuration = st.file_uploader(
            "BEAST 2 XML configuration", type=["xml"]
        )
        beast2_logs = st.file_uploader("BEAST 2 log file", type=["log"])
        beast2_trees = st.file_uploader("BEAST 2 posterior trees", type=["trees"])

        """
        Optionally, you can also select other files (like summary trees) which you consider an important part of your analysis.
        """

        other_files = st.file_uploader(
            "Other files (optional)", type=["*"], accept_multiple_files=True
        )

    """
    Almost done!
    """

    def process_input():
        if not title.strip():
            st.toast("Specify a paper title.")
            return
        if not abstract.strip():
            st.toast("Specify a paper abstract.")
            return
        if not authors.strip():
            st.toast("Specify at least one paper author.")
            return
        if len(bibtexparser.parse_string(bibtext).entries) != 1:
            st.toast("Specify exactly one bibtex entry.")
            return
        if not beast2_configuration:
            st.toast("Specify a BEAST 2 configuration file.")
            return
        if not beast2_logs:
            st.toast("Specify a BEAST 2 log file.")
            return
        if not beast2_trees:
            st.toast("Specify a BEAST 2 trees file.")
            return

        with st.spinner("Processing your analysis..."):
            paper = Paper(
                title=title.strip(),
                authors=[author.strip() for author in authors.split("\n")],
                abstract=abstract.strip(),
                bibtex=bibtext.strip(),
                doi=doi.strip() or None,
                url=url.strip() or None,
            )

            experiment = Experiment(
                title=experiment_title.strip() or None,
                description=experiment_description.strip() or None,
                origin="manualUpload",
                upload_date=date.today(),
                type=ExperimentType.BEAST2_Experiment,
            )

            metadata = Metadata(evo_data_pipeline_version=__version__)

            try:
                st.text("Processing the given files...")
                parsed_beast2_configuration = parse_file(
                    beast2_configuration, FileType.BEAST2_CONFIGURATION
                )
                parsed_beast2_logs = parse_file(
                    beast2_logs, FileType.BEAST2_POSTERIOR_LOGS
                )
                parsed_beast2_trees = parse_file(
                    beast2_trees, FileType.BEAST2_POSTERIOR_TREES
                )

                files = [
                    parsed_beast2_configuration,
                    parsed_beast2_logs,
                    parsed_beast2_trees,
                ]

                for other_file in other_files:
                    parsed_other_file = parse_file(other_file, FileType.UNKNOWN)
                    files.append(parsed_other_file)

                st.text("Detecting the evolutionary model...")
                parsed_evolutionary_model = parse_evolutionary_model(
                    beast2_configuration
                )

                st.text(
                    "Detecting the samples (e.g. using BEAST2 or language lookup). This might take a while, especially for amino acid sequences..."
                )
                parsed_samples = parse_beast2_samples(
                    beast2_configuration, parsed_evolutionary_model
                )

                st.text("Processing the trees...")
                parsed_trees = parse_trees(beast2_trees)
            except ValidationError as error:
                st.toast(error.message)
                return

            paper_with_experiment = PaperWithExperiment(
                experiment=experiment,
                paper=paper,
                files=files,
                evolutionary_model=parsed_evolutionary_model,
                samples=parsed_samples,
                trees=parsed_trees,
                metadata=metadata,
            )

            st.text("Creating PhyloData folder...")

            output_folder = create_output_folder(
                title,
                beast2_configuration,
                beast2_logs,
                beast2_trees,
                other_files,
                paper_with_experiment,
            )

            st.session_state[STAGE] = Stage.NEXT_STEPS
            st.session_state[OUTPUT_FOLDER] = output_folder
            st.rerun()

    process_experiment_button = st.button("Process experiment", type="primary")
    if process_experiment_button:
        process_input()


if st.session_state[STAGE] == Stage.NEXT_STEPS:
    """
    # 🚀 Next Steps

    You successfully processed your experiment! These are your next steps:

    1. Create a ZIP file of the newly created folder.
    2. Upload it on the [PhyloData website](http://phylodata.com/new-experiment).
    """
