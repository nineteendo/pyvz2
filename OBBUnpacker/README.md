# OBBUnpacker
- 1bsr_pgsr.bms outdated script this was based upon
- fail.txt: file with the latest errors
- options.json: settings (see below)
- README.md: this file
- unpack.py a tool to unpack 1bsr and pgsr

# options.json
key | purpose
--- | ---
DEBUG_MODE | Show full error traceback
dumpRsgp | Extract RSGPs from OBB
endswith |  Only unpack paths ending with these strings
endswithIgnore | Ignore the end of the path
enteredPath | Don't replace "\ " with " "
extractRsgp | Extract files directly from OBBs
extensions | Only unpack from files with these extensions
startswith | Only unpack paths starting with these strings
startswithIgnore | Ignore the start of the path

# Data Formats
Please help me finishing this documentation and correcting errors.

## 1BSR Header
what | type | purpose
--- | --- | ---
HEADER | string 4 | 1bsr
VERSION | < long | 3/4
NOTHING | long | NOTHING
FIRST_PGSR_OFFSET | < long | start of first pgsr file
FILE_NAME_SIZE | < long | size of unpacked files names segment
FILE_NAME_OFFSET | < long | start of file names
NOTHING | 12 bytes | NOTHING
PGSR_NAME_SIZE | < long | size of  of pgsr files names
PGSR_NAME_OFFSET | < long | start of pgsr names
PGSRS | < long | # of PGSR files
PGSR_OFFSET | < long | start of PGSR files
??? | long | ???
??? | long | ???
COMPOSITE_GROUP_OFFSET | long | start of composite groups
??? | long | ???
??? | long | ???
COMPOSITE_GROUP_NAME_OFFSET | long | start of composite groups names
??? | long | ???
AUTOPOOL_OFFSET | long | start of autopool
??? | long | ???
??? | long | ???
???_OFFSET | long | start of ???
??? | long | ???
NOTHING | 12 bytes | NOTHING
FIRST_PGSR_OFFSET | < long | start of first pgsr file

## 1BSR smart pathnames -> GET_NAME()
what | type | purpose
--- | --- | ---
CHAR | string 1 | character of path name
END_OFFSET | < 3 bytes | offset after which the current read characters expire

code:
```
def GET_NAME(file, OFFSET, NAME_DICT):
	NAME = b""
	temp = file.tell()
	for key in list(NAME_DICT.keys()):
		if NAME_DICT[key] + OFFSET < temp:
			NAME_DICT.pop(key)
		else:
			NAME = key
	TMP_BYTE = b""
	while TMP_BYTE != b"\x00":
		NAME += TMP_BYTE
		TMP_BYTE = file.read(1)
		TMP_LENGTH = 4 * struct.unpack('<L', file.read(3) + b"\x00")[0]
		if TMP_LENGTH != 0:
			NAME_DICT[NAME] = TMP_LENGTH
	return (NAME, NAME_DICT)
```

## PGSR Header
what | type | purpose
--- | --- | ---
HEADER | string 4 | pgsr
VERSION | < long | 3/4
NOTHING | 8 bytes | NOTHING
TYPE | long | 1/3
PGSR_BASE | long | start of file data
SINGLE_OFFSET | long | start of single files
SINGLE_COMPRESSED_SIZE | long | compressed size of single files
SINGLE_UNCOMPRESSED_SIZE | long | uncompressed size of single files
NOTHING | long | NOTHING
MULTIPLE_OFFSET | long | start of multiple files
MULTIPLE_COMPRESSED_SIZE | long | compressed size of multiple files
MULTIPLE_UNCOMPRESSED_SIZE | long | uncompressed size of multiple files
