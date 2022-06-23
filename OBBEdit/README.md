# OBBEdit
## Folders
- libraries: 3th party libraries from PyVZ2. **GPL-3.0 LICENCE**
- options: templates (see below)
- options_unused: unused templates
## Files
- fail.txt: file with the last errors
- patch.py a tool to patch 1bsr and pgsr
- README.md: this file
- unpack.py a tool to unpack 1bsr and pgsr
- versions.cfg (old configuration file)

## Templates
All info is sorted alphabetically on **FILE NAME**
### Group Format:
```
[KEY]--[INFO]
````
* [KEY], **case-sensitive**, is the key for selecting a template
* [INFO], is the info displayed about the group
* Example:
	```
	a--Android Templates
	```
* Displayed: `Android Templates`

### Naming Format:
```
[KEY]--[UNPACK_INFO]--[PATCH_INFO].json
````
* [KEY], **case-sensitive**, is the key for selecting a template
* [UNPACK_INFO], is the info displayed during unpacking
* [PATCH_INFO], is the info displayed during patching
* Example:
	```
	5--Decode RTON--Encode JSON.json
	```
* Displayed: `5: Decode RTON`

### JSON options
Key | Purpose
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
4 | HEADER_SIZE #obsr__size
4 | FILE_LIST_SIZE
4 | FILE_LIST_OFFSET
8 | /
4 | SUBGROUP_LIST_SIZE
4 | SUBGROUP_LIST_OFFSET
4 | SUBGROUP_INFO_ENTRIES
4 | SUBGROUP_INFO_OFFSET
4 | SUBGROUP_INFO_ENTRY_SIZE (204)
4 | GROUP_INFO_ENTRIES
4 | GROUP_INFO_OFFSET
4 | GROUP_INFO_ENTRY_SIZE (1156)
4 | GROUP_LIST_SIZE
4 | GROUP_LIST_OFFSET
4 | AUTOPOOL_INFO_ENTRIES
4 | AUTOPOOL_INFO_OFFSET
4 | AUTOPOOL_INFO_ENTRY_SIZE (152)
4 | PTX_INFO_ENTRIES
4 | PTX_INFO_OFFSET
4 | PTX_INFO_ENTRY_SIZE (16)
4 | DIRECTORY_7 ?
4 | DIRECTORY_8 ?
4 | DIRECTORY_9 ?
4 | HEADER_SIZE_2 #obsr__size

### 1BSR smart pathnames -> GET_NAME()
What | Type | Purpose
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
COMPRESSION_FLAGS | long | 0/1/3
HEADER_LENGTH | long | length of header
DATA_OFFSET | long | start of files
COMPRESSED_DATA_SIZE | long | compressed size of files
DECOMPRESSED_DATA_SIZE | long | decompressed of files
NOTHING | long | NOTHING
IMAGE_DATA_OFFSET | long | start of images
COMPRESSED_IMAGE_DATA_SIZE | long | compressed size of images
DECOMPRESSED_IMAGE_DATA_SIZE | long | decompressed size of images

Get Data of files:
```
def rsg_extract(RSG_NAME, file, pathout_data, out, pathout, level):
	try:
		HEADER = file.read(4)
		VERSION = unpack("<I", file.read(4))[0]
		
		file.seek(8, 1)
		COMPRESSION_FLAGS = unpack("<I", file.read(4))[0]
		HEADER_LENGTH = unpack("<I", file.read(4))[0]

		DATA_OFFSET = unpack("<I", file.read(4))[0]
		COMPRESSED_DATA_SIZE = unpack("<I", file.read(4))[0]
		DECOMPRESSED_DATA_SIZE = unpack("<I", file.read(4))[0]
		
		file.seek(4, 1)
		IMAGE_DATA_OFFSET = unpack("<I", file.read(4))[0]
		COMPRESSED_IMAGE_DATA_SIZE = unpack("<I", file.read(4))[0]
		DECOMPRESSED_IMAGE_DATA_SIZE = unpack("<I", file.read(4))[0]
		
		file.seek(20, 1)
		INFO_SIZE = unpack("<I", file.read(4))[0]
		INFO_OFFSET = unpack("<I", file.read(4))[0]
		INFO_LIMIT = INFO_OFFSET + INFO_SIZE
		
		if COMPRESSION_FLAGS & 2 == 0: # Decompressed files
			data = bytearray(pathout_data[DATA_OFFSET: DATA_OFFSET + COMPRESSED_DATA_SIZE])
		elif COMPRESSED_DATA_SIZE != 0: # Compressed files
			data = bytearray(decompress(pathout_data[DATA_OFFSET: DATA_OFFSET + COMPRESSED_DATA_SIZE]))
			
		if DECOMPRESSED_IMAGE_DATA_SIZE != 0:
			file.seek(IMAGE_DATA_OFFSET)
			if COMPRESSION_FLAGS & 1 == 0: # Decompressed files
				image_data = bytearray(pathout_data[IMAGE_DATA_OFFSET: IMAGE_DATA_OFFSET + COMPRESSED_IMAGE_DATA_SIZE])
			else: # Compressed files
				image_data = bytearray(decompress(pathout_data[IMAGE_DATA_OFFSET: IMAGE_DATA_OFFSET + COMPRESSED_IMAGE_DATA_SIZE]))
	except Exception as e:
		error_message(type(e).__name__ + " while extracting " + file.name + str(e))
```
