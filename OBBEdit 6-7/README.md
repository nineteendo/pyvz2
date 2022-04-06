# OBBEdit
- fail.txt: file with the last errors
- options.json: settings for unpacking (see below)
- patch.py a tool to patch 1bsr and pgsr
- README.md: this file
- unpack.py a tool to unpack 1bsr and pgsr
- versions.cfg (old configuration file)

# options.json
key | purpose
--- | ---
smfExtensions | Only unpack SMFs with these extensions
smfUnpackLevel | Level to unpack SMFs to (make negative for manual input)
 | 
endsWith | Only unpack paths ending with these strings
endsWithIgnore | Ignore the end of the path
rsbExtensions | Only unpack RSBs/OBBs/SMFs with these extensions
rsbUnpackLevel | Level to unpack RSBs/OBBs/SMFs to (make negative for manual input)
rsgpEndsWith | Only unpack RSGPs ending with these strings
rsgpEndsWithIgnore | Ignore the end of RSGPs
rsgpStartsWith | Only unpack RSGPs starting with these strings
rsgpStartsWithIgnore | Ignore the start of RSGPs
startsWith | Only unpack paths starting with these strings
startsWithIgnore | Ignore the start of the path
 | 
encryptedExtensions | Only encrypt ENCRYPTED with these extensions
encryptedUnpackLevel | Level to unpack ENCRYPTED to (make negative for manual input)
encryptionKey | Key used for encrypting, the default is not right, search it if you want to decrypt
 | 
comma | Spaces between values in JSON (make negative to disable)
doublePoint | Spaces between key & value in JSON (make negative to disable)
encodedUnpackLevel | Level to unpack ENCODED to (make negative for manual input)
ensureAscii | escape non-ASCII characters with \uXXXX sequences
indent | Spaces as indent, negative for tab, *null:* no indent
repairFiles | Repair RTON files that end abruptly
RTONExtensions | Extensions of RTON files
RTONNoExtensions | Start of RTON files with no extension
shortNames | Remove RTON extensions for JSON files
sortKeys | Sort keys in object
sortValues | Sort values in array

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
