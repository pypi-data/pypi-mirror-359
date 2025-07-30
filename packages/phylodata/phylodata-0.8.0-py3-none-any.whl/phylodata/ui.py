from enum import Enum

import streamlit as st

from phylodata.data_types import (
    Metadata,
    PaperWithExperiment,
)
from phylodata.errors import ValidationError
from phylodata.modules.evolutionary_model_module import EvolutionaryModelModule
from phylodata.modules.experiment_module import ExperimentModule
from phylodata.modules.files_module import FilesModule
from phylodata.modules.paper_module import PaperModule
from phylodata.modules.samples_module import SamplesModule
from phylodata.modules.trees_module import TreesModule
from phylodata.utils.output_utils import create_output_folder
from phylodata.version import __version__


class Stage(str, Enum):
    INPUT = "Input"
    NEXT_STEPS = "Next Steps"


STAGE = "stage"
OUTPUT_FOLDER = "output_folder"

paper_module = PaperModule()
experiment_module = ExperimentModule()
files_module = FilesModule()
evolutionary_model_module = EvolutionaryModelModule()
samples_module = SamplesModule()
trees_module = TreesModule()

if STAGE not in st.session_state:
    st.session_state[STAGE] = Stage.INPUT


if st.session_state[STAGE] == Stage.INPUT:
    """
    # 🌴 Process Experiment

    Let's process your Bayesian Phylogenetics experiment to prepare it for upload to the PhyloData repository.

    Note that right now, we only support BEAST 2 experiments.

    This usually takes less than five minutes.
    """

    paper_module.ui()
    experiment_module.ui()
    files_module.ui()

    """
    Almost done!
    """

    def process_input():
        with st.spinner("Processing your analysis..."):
            try:
                paper_module.validate()
                files_module.validate()

                paper = paper_module.parse()
                experiment = experiment_module.parse()

                st.text("Processing the given files...")
                files = files_module.parse()

                evolutionary_model_module.set_dependencies(
                    files_module.beast2_configuration
                )
                parsed_evolutionary_model = evolutionary_model_module.parse()

                samples_module.set_dependencies(files_module.beast2_configuration)
                parsed_samples = samples_module.parse()

                trees_module.set_dependencies(files_module.beast2_trees)
                parsed_trees = trees_module.parse()

            except ValidationError as error:
                st.toast(error.message)
                return

            metadata = Metadata(evo_data_pipeline_version=__version__)

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
                paper.title,
                files_module.beast2_configuration,  # type: ignore
                files_module.beast2_logs,  # type: ignore
                files_module.beast2_trees,  # type: ignore
                files_module.other_files,
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
