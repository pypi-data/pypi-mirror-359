import bibtexparser
import streamlit as st

from phylodata.data_types import Paper
from phylodata.errors import ValidationError
from phylodata.modules.module import Module


class PaperModule(Module[Paper]):
    def ui(self):
        with st.container(border=True):
            st.write("""
            ### Paper

            Enter the following general information about your paper:
            """)

            self.title = st.text_input("Title")
            self.abstract = st.text_area("Abstract")
            self.authors = st.text_area("Authors (one per line)")
            self.bibtext = st.text_area("BibTex citation")
            self.doi = st.text_input("DOI")
            st.write(
                """Experiments with the same paper DOI will be linked to the same paper."""
            )
            self.url = st.text_input("URL (optional)")

    def validate(self):
        if not self.title.strip():
            raise ValidationError("Specify a paper title.")
        if not self.abstract.strip():
            raise ValidationError("Specify a paper abstract.")
        if not self.authors.strip():
            raise ValidationError("Specify at least one paper author.")
        if len(bibtexparser.parse_string(self.bibtext).entries) != 1:
            st.toast("Specify exactly one bibtex entry.")
            return
        if not self.doi.strip():
            st.toast("Specify a DOI.")
            return

    def parse(self) -> Paper:
        return Paper(
            title=self.title.strip(),
            authors=[author.strip() for author in self.authors.split("\n")],
            abstract=self.abstract.strip(),
            bibtex=self.bibtext.strip(),
            doi=self.doi.strip(),
            url=self.url.strip() or None,
        )
