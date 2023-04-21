from collections import namedtuple

LookupArgs = namedtuple("fk_lookup_args", ["fk_primary", "related_table", "pk_related"])
