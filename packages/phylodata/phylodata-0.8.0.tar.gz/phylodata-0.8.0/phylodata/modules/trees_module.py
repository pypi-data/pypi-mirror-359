import streamlit as st

from phylodata.data_types import Trees
from phylodata.modules.module import Module
from phylodata.parsers.parse_trees import parse_trees


class TreesModule(Module[Trees]):
    def ui(self): ...

    def validate(self): ...

    def set_dependencies(self, beast2_trees):
        self.beast2_trees = beast2_trees

    def parse(self) -> Trees:
        st.text("Processing the trees...")
        return parse_trees(self.beast2_trees)
