# Expected values for a valid Sims4 .package file
# See: https://thesims4moddersreference.org/reference/dbpf-format/

# Python struct unpack format for DBPF header
# ref: https://docs.python.org/3/library/struct.html#format-characters
import struct

HEADER_STRUCT_FORMAT = "<4s 11I 12s I Q 24s"
HEADER_SIZE = 96  # <- Must match size of HEADER_STRUCT_FORMAT

INDEX_HEADER_STRUCT_FORMAT = "<I"
INDEX_HEADER_SIZE = struct.calcsize(INDEX_HEADER_STRUCT_FORMAT)
INDEX_VERSION_MAJOR = 0
INDEX_VERSION_MINOR = 3

STATIC_ENTRY_STRUCT_FORMAT = "<4I"
STATIC_ENTRY_SIZE = struct.calcsize(STATIC_ENTRY_STRUCT_FORMAT)

# File identifier for Sims4 .package file
FILE_IDENTIFIER = b"DBPF"

# At the very least, a valid package file must be at least as large as the header size
MIN_FILE_SIZE = HEADER_SIZE

# DBPF header constants
EXPECTED_MAJOR_FORMAT_VERSION = 2
EXPECTED_MINOR_FORMAT_VERSION = 1
EXPECTED_UNKNOWN_CONSTANT_ONE = 0
EXPECTED_HOLE_OFFSET = 3
