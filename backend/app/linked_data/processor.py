from pyld import jsonld
from pyld.jsonld import JsonLdError
from app.linked_data.contexts import CACHED_CONTEXTS
from deepdiff import DeepDiff, grep
from pprint import pprint
import json


class LDProcessorError(Exception):
    """Generic LDProcessorError Error."""


class LDProcessor:
    def __init__(self, strict=True, allowed_ctx=[]):
        self.strict = strict
        self.allowed_ctx = allowed_ctx

    def safe_test(self, document):
        contexts = document['@context'] if isinstance(document['@context'], list) else [document['@context']]
        document.pop('@context')
        context = [self.load_cached_ctx(context_url) for context_url in contexts]
        compacted = jsonld.compact(document, context, {'base': 'invalid:'})
        # diff = DeepDiff(document, compacted)
        # pprint(diff)
        # compacted = jsonld.compact(document, document['@context'])
        diff = DeepDiff(document, compacted)
        undefined_properties = []
        undefined_types = []
        if diff.get('dictionary_item_removed'):
            pass
        dropped_attributes = [item for item in diff.get('dictionary_item_removed')] if diff.get('dictionary_item_removed') else []
        #     pprint(removed_items)
        #     removed_items = list(diff.get('dictionary_item_removed'))
        #     removed_items = removed_items[0].path()
        #     pprint(removed_items)
        # pprint(dropped_attributes)
        # pprint(diff)

    def detect_undefined_terms(self, document):
        if not document.get('@context', None):
            raise LDProcessorError("No context")
        contexts = document['@context'] if isinstance(document['@context'], list) else [document['@context']]
        document['@context'] = [self.load_cached_ctx(context_url) for context_url in contexts]
        diff = DeepDiff(
            document, 
            jsonld.compact(document, document['@context'], {'base': 'undefined:'})
        )
        # pprint(diff)
        if diff.get('dictionary_item_removed'):
            raise LDProcessorError("Missing term definition")
        if diff.get('values_changed'):
            raise LDProcessorError("Missing term definition")
        return False

    def dropped_types(self):
        pass

    def dropped_attributes(self):
        pass

    def load_cached_ctx(self, context_url):
        if isinstance(context_url, dict):
            return context_url
        if context_url in CACHED_CONTEXTS:
            return CACHED_CONTEXTS[context_url]
        elif context_url in self.allowed_ctx:
            # TODO Fetch and cache context
            return context_url
        else:
            if self.strict:
                raise LDProcessorError("Strict mode on, rejecting unknown context.")

    def try_compact(self, context):
        try:
            jsonld.compact({}, context)
            return True
        except Exception:
            raise LDProcessorError("Error compacting context.")

    def is_valid_context(self, context):
        for idx, ctx_entry in enumerate(context):
            if isinstance(ctx_entry, str):
                context[idx] = self.load_cached_ctx(ctx_entry)
            elif isinstance(ctx_entry, dict):
                return False
        return self.try_compact(context)
