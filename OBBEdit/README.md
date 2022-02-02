# OBBEdit
- fail.txt: file with the latest errors
- options.json: settings for unpacking (see below)
- patch.py a tool to patch 1bsr and pgsr
- README.md: this file
- unpack.py a tool to unpack 1bsr and pgsr

# options.json
key | purpose
--- | ---
confirmPath | Confirm or change parsed path before conversion
DEBUG_MODE | Show full error traceback
endswith | Only unpack paths ending with these strings
endswithIgnore | Ignore the end of the path
enteredPath | Don't use hybrid paths that can be escaped
rsbExtensions | Only unpack from OBBs with these extensions
rsbUnpackLevel | Level to unpack OBBs to (make negative for manual input)
rsgpExtensions | Only unpack from RSGPs with these extensions
rsgpEndswith | Only unpack RSGPs ending with these strings
rsgpEndswithIgnore | Ignore the end of RSGPs
rsgpStartswith | Only unpack RSGPs starting with these strings
rsgpStartswithIgnore | Ignore the start of RSGPs
rsgpUnpackLevel | Level to unpack RSGPs to (make negative for manual input)
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

## PGSR Header -> GET_SECTION():
what | type | purpose
--- | --- | ---
HEADER | string 4 | pgsr
VERSION | < long | 3/4
NOTHING | 8 bytes | NOTHING
TYPE | long | 1/3
PGSR_BASE | long | start of file data
OFFSET_A | long | start A of files
COMPRESSED_SIZE_A | long | compressed size A of files
UNCOMPRESSED_SIZE_A | long | uncompressed A of files
NOTHING | long | NOTHING
OFFSET_B | long | start B of files
COMPRESSED_SIZE_B | long | compressed size B of files
UNCOMPRESSED_SIZE_B | long | uncompressed size B  of files

Get Data of files:
```
def rsgp_extract(rsgp_NAME, rsgp_OFFSET, file, out, pathout, level):
	if file.read(4) == b"pgsr":
		try:
			VER = struct.unpack("<I", file.read(4))[0]
			
			file.seek(8, 1)
			TYPE = struct.unpack("<I", file.read(4))[0]
			rsgp_BASE = struct.unpack("<I", file.read(4))[0]

			data = None
			OFFSET = struct.unpack("<I", file.read(4))[0]
			ZSIZE = struct.unpack("<I", file.read(4))[0]
			SIZE = struct.unpack("<I", file.read(4))[0]
			if SIZE != 0:
				file.seek(rsgp_OFFSET + OFFSET)
				if TYPE == 0: # Encypted files
					# Insert encyption here
					data = file.read(ZSIZE)
				elif TYPE == 1: # Uncompressed files
					data = file.read(ZSIZE)
				elif TYPE == 3: # Compressed files
					blue_print("Decompressing ...")
					data = zlib.decompress(file.read(ZSIZE))
				else: # Unknown files
					raise TypeError(TYPE)
			else:
				file.seek(4, 1)
				OFFSET = struct.unpack("<I", file.read(4))[0]
				ZSIZE = struct.unpack("<I", file.read(4))[0]
				SIZE = struct.unpack("<I", file.read(4))[0]
				if SIZE != 0:
					file.seek(rsgp_OFFSET + OFFSET)
					if TYPE == 0: # Encypted files
						# Insert encyption here
						data = file.read(ZSIZE)
					elif TYPE == 1: # Compressed files
						blue_print("Decompressing ...")
						data = zlib.decompress(file.read(ZSIZE))
					elif TYPE == 3: # Compressed files
						blue_print("Decompressing ...")
						data = zlib.decompress(file.read(ZSIZE))
					else: # Unknown files
						raise TypeError(TYPE)
		except:
			error_message("%s while extracting %s.rsgp: %s" % (type(e).__name__, rsgp_NAME, e))
```
