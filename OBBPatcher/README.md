# OBBPatcher
- extract.py
- options.json
- patch.py
- README.md: this file
- versions.cfg version configuration file

# options.json
key | purpose
--- | ---
DEBUG_MODE | Show full error traceback
enteredPath | Don't use hybrid paths that can be escaped

# versions.cfg
- name:			can be any alphanumeric character plus underscore "_" and dot "."
- file_size:	size of the entire OBB file in bytes
- offset:		offset where the compressed data starts
- packed_size:	size of the compressed block in bytes; 
-				if this number is negative then it treats it as the end offset 

name:	file_size,	offset,	packed_size