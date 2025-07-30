"""Generate JSON schema for PaperWithExperiment data type."""

import msgspec

from phylodata.data_types import PaperWithExperiment

schema = msgspec.json.schema(PaperWithExperiment)

with open("../website/src/lib/schema.json", "wb") as f:
    f.write(msgspec.json.format(msgspec.json.encode(schema)))
