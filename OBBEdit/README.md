# OBBEdit
## Files
- fail.txt: file with the last errors
- options.json: settings for unpacking (see below)
- patch.py a tool to patch 1bsr and pgsr
- README.md: this file
- unpack.py a tool to unpack 1bsr and pgsr
- versions.cfg (old configuration file)

## options.json
key | purpose
--- | ---
smfExtensions | Only unpack SMFs with these extensions
smfPacked | path to packed smf (blank for manual input)
smfUnpacked | path to unpacked smf (blank for manual input)
smfUnpackLevel | Level to unpack SMFs to (negative / 0 for manual input)
/ | /
rsbExtensions | Only unpack RSBs/SMFs with these extensions
rsbPacked | path to packed rsb (blank for manual input)
rsbPatched | path to patched rsb (blank for manual input)
rsbUnpacked | path to unpacked rsb (blank for manual input)
rsbUnpackLevel | Level to unpack RSBs/SMFs to (negative / 0 for manual input)
rsgpEndsWith | Only unpack RSGPs ending with these strings
rsgpEndsWithIgnore | Ignore the end of RSGPs
rsgpStartsWith | Only unpack RSGPs starting with these strings
rsgpStartsWithIgnore | Ignore the start of RSGPs
/ | /
overrideDataCompression | Override data compression (negative / 0 for manual input)
overrideEncryption | Override image data compression (negative / 0 for manual input)
overrideImageDataCompression | Override image data compression (negative / 0 for manual input)
pathEndsWith | Only unpack paths ending with these strings
pathEndsWithIgnore | Ignore the end of the path
pathStartsWith | Only unpack paths starting with these strings
pathStartsWithIgnore | Ignore the start of the path
rsgExtensions | Only encrypt RSG/RSBs/SMFs with these extensions
rsgPacked | path to packed rsg (blank for manual input)
rsgPatched | path to patched rsg (blank for manual input)
rsgUnpacked | path to unpacked rsg (blank for manual input)
rsgUnpackLevel | Level to unpack RSG/RSBs/SMFs to (negative / 0 for manual input)
/ | /
encryptedExtensions | Only encrypt ENCRYPTED with these extensions
encryptedPacked | path to packed encrypted (blank for manual input)
encryptedUnpacked | path to unpacked encrypted (blank for manual input)
encryptedUnpackLevel | Level to unpack ENCRYPTED to (negative / 0 for manual input)
encryptionKey | Key used for encrypting, the default is not right, search it if you want to decrypt
/ | /
comma | Spaces between values in JSON (negative to disable)
doublePoint | Spaces between key & value in JSON (negative to disable)
encodedPacked | path to packed encoded (blank for manual input)
encodedUnpacked | path to unpacked encoded (blank for manual input)
encodedUnpackLevel | Level to unpack ENCODED to (negative / 0 for manual input)
ensureAscii | escape non-ASCII characters with \uXXXX sequences
indent | Spaces as indent, negative for tab, *null:* no indent
repairFiles | Repair RTON files that end abruptly
RTONExtensions | Extensions of RTON files
RTONNoExtensions | Start of RTON files with no extension
shortNames | Remove RTON extensions for JSON files
sortKeys | Sort keys in object
sortValues | Sort values in array

## Data Formats
Please help me finishing this documentation and correcting errors.

### 1BSR Header
Byte | what
--- | ---
4 | HEADER (1bsr)
4 | VERSION (3/4)
4 | /
4 | FILE_DATA_OFFSET
4 | DIRECTORY_0_LENGTH
4 | DIRECTORY_0_OFFSET
8 | /
4 | DIRECTORY_1_LENGTH
4 | DIRECTORY_1_OFFSET
4 | DIRECTORY_4_ENTRIES
4 | DIRECTORY_4_OFFSET
4 | DIRECTORY_4_ENTRY_SIZE (204)
4 | DIRECTORY_2_ENTRIES
4 | DIRECTORY_2_OFFSET
4 | DIRECTORY_2_ENTRY_SIZE (1156)
4 | DIRECTORY_3_LENGTH
4 | DIRECTORY_3_OFFSET
4 | DIRECTORY_5_ENTRIES
4 | DIRECTORY_5_OFFSET
4 | DIRECTORY_5_ENTRY_SIZE (152)
4 | DIRECTORY_6_ENTRIES
4 | DIRECTORY_6_OFFSET
4 | DIRECTORY_6_ENTRY_SIZE (16)
4 | DIRECTORY_7 ?
4 | DIRECTORY_8 ?
4 | DIRECTORY_9 ?

### 1BSR smart pathnames -> GET_NAME()
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

### PGSR Header -> GET_SECTION():
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
