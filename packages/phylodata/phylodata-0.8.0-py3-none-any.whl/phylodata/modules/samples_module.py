import streamlit as st

from phylodata.data_types import Sample
from phylodata.modules.module import Module
from phylodata.parsers.parse_beast2_samples import parse_beast2_samples


class SamplesModule(Module[list[Sample]]):
    def ui(self): ...

    def validate(self): ...

    def set_dependencies(self, beast2_configuration):
        self.beast2_configuration = beast2_configuration

    def parse(self) -> list[Sample]:
        st.text(
            "Detecting the samples (e.g. using BEAST2 or language lookup). "
            "This might take a while, especially for amino acid sequences..."
        )
        return parse_beast2_samples(self.beast2_configuration)
