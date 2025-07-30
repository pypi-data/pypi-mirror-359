from datetime import date

import streamlit as st

from phylodata.data_types import Experiment, ExperimentType
from phylodata.modules.module import Module


class ExperimentModule(Module[Experiment]):
    def ui(self):
        with st.container(border=True):
            """
            ### Experiment

            Optionally, enter some additional information about your experiment. This is useful if you want to register multiple experiments for the same paper.
            """

            self.title = st.text_input("Experiment title (optional)")
            self.description = st.text_area("Experiment description (optional)")

    def validate(self): ...

    def parse(self) -> Experiment:
        return Experiment(
            title=self.title.strip() or None,
            description=self.description.strip() or None,
            origin="manualUpload",
            upload_date=date.today(),
            type=ExperimentType.BEAST2_Experiment,
        )
