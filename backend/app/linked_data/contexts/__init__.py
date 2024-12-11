"""JSON-LD Contexts."""

from .credential_v1 import CREDENTIAL_V1
from .credential_v2 import CREDENTIAL_V2
from .example_v2 import EXAMPLES_V2

CACHED_CONTEXTS = {
    "https://www.w3.org/2018/credentials/v1": CREDENTIAL_V1,
    "https://www.w3.org/ns/credentials/v2": CREDENTIAL_V2,
    "https://www.w3.org/ns/credentials/examples/v2": EXAMPLES_V2,
}

__all__ = ["CACHED_CONTEXTS"]
