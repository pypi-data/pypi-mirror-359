import streamlit as st

from phylodata.data_types import EvolutionaryModel
from phylodata.modules.module import Module
from phylodata.parsers.parse_evolutionary_model import parse_evolutionary_model


class EvolutionaryModelModule(Module[EvolutionaryModel]):
    def ui(self): ...

    def validate(self): ...

    def set_dependencies(self, beast2_configuration):
        self.beast2_configuration = beast2_configuration

    def parse(self) -> EvolutionaryModel:
        st.text("Detecting the evolutionary model...")
        return parse_evolutionary_model(self.beast2_configuration)
