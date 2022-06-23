# Import libraries
import datetime
from hashlib import md5
from io import BytesIO
from os import makedirs, listdir, getcwd, sep
from os.path import isdir, isfile, join as osjoin, dirname, relpath, splitext
#from PIL import Image
from struct import pack, unpack
from zlib import compress, decompress

# 3th party libraries
from libraries.pyvz2nineteendo import LogError, blue_print, green_print, initialize, path_input, list_levels
from libraries.pyvz2rijndael import RijndaelCBC
from libraries.pyvz2rton import JSONDecoder

options = {
# Default options
	# SMF options
	"smfExtensions": (
		".rsb.smf",
	),
	"smfPacked": "",
	"smfUnpacked": "",
	"smfUnpackLevel": 1,
	# RSB options
	"rsbExtensions": (
		".rsb.smf",
		
		".1bsr",
		".rsb1",
		".rsb",
		".obb"
	),
	"rsbPacked": "",
	"rsbPatched": "",
	"rsbUnpacked": "",
	"rsbUnpackLevel": 2,
	"rsgEndsWith": (),
	"rsgEndsWithIgnore": True,
	"rsgStartsWith": (
		"packages",
		"worldpackages_"
	),
	"rsgStartsWithIgnore": False,
	# RSG options
	"overrideDataCompression": 1,
	"overrideEncryption": 2,
	"overrideImageDataCompression": 1,
	"pathEndsWith": (
		".rton",
	),
	"pathEndsWithIgnore": False,
	"pathStartsWith": (
		"packages/",
	),
	"pathStartsWithIgnore": False,
	"rsgExtensions": (
		".rsb.smf",
		
		".1bsr",
		".rsb1",
		".rsb",
		".obb",
		
		".pgsr",
		".rsgp",
		".rsg",
		".rsg.smf"
	),
	"rsgPacked": "",
	"rsgPatched": "",
	"rsgUnpacked": "",
	"rsgUnpackLevel": 7,
	# Encryption options
	"encryptedExtensions": (
		".rton",
	),
	"encryptedPacked": "",
	"encryptedUnpacked": "",
	"encryptedUnpackLevel": 5,
	"encryptionKey": "00000000000000000000000000000000",
	# RTON options
	"comma": 0,
	"doublePoint": 1,
	"encodedPacked": "",
	"encodedUnpacked": "",
	"encodedUnpackLevel": 6,
	"ensureAscii": False,
	"indent": 4,
	"repairFiles": False,
	"RTONExtensions": (
		".bin",
		".dat",
		".json",
		".rton",
		".section"
	),
	"RTONNoExtensions": (
		"draper_",
		"local_profiles",
		"loot",
		"_saveheader_rton"
	),
	"sortKeys": False,
	"sortValues": False
}
# RSG Patch functions
class SectionError(Exception):
	pass
def extend_to_4096(number):
	return b"\0" * ((4096 - number) & 4095)
def rsg_patch_data(RSG_NAME, file, pathout_data, patch, patchout, level):
# Patch RGSP file
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

	data = None
	if level < 5:
		try:
			patch_data = open(osjoin(patch, RSG_NAME + ".section"), "rb").read()
			patch_length = len(patch_data)
			if patch_length == DECOMPRESSED_DATA_SIZE:
				data = patch_data
			else:
				raise SectionError("Incompatible section size, found " + repr(patch_length) + ", expected: " + repr(DECOMPRESSED_DATA_SIZE))
		except FileNotFoundError:
			pass
	elif COMPRESSION_FLAGS & 2 == 0: # Decompressed files
		data = bytearray(pathout_data[DATA_OFFSET: DATA_OFFSET + COMPRESSED_DATA_SIZE])
	elif COMPRESSED_DATA_SIZE != 0: # Compressed files
		data = bytearray(decompress(pathout_data[DATA_OFFSET: DATA_OFFSET + COMPRESSED_DATA_SIZE]))
		
	image_data = None
	if DECOMPRESSED_IMAGE_DATA_SIZE != 0:
		if level < 5:
			try:
				patch_data = open(osjoin(patch, RSG_NAME + ".section2"), "rb").read()
				patch_length = len(patch_data)
				if len(patch_data) == DECOMPRESSED_IMAGE_DATA_SIZE:
					image_data = patch_data
				else:
					raise SectionError("Incompatible section size, found " + repr(patch_length) + ", expected: " + repr(DECOMPRESSED_IMAGE_DATA_SIZE))
			except FileNotFoundError:
				pass
		elif COMPRESSION_FLAGS & 1 == 0: # Decompressed files
			image_data = bytearray(pathout_data[IMAGE_DATA_OFFSET: IMAGE_DATA_OFFSET + COMPRESSED_IMAGE_DATA_SIZE])
		else: # Compressed files
			image_data = bytearray(decompress(pathout_data[IMAGE_DATA_OFFSET: IMAGE_DATA_OFFSET + COMPRESSED_IMAGE_DATA_SIZE]))

	if 4 < level:
		DATA_DICT = {
			"": {
				"FILE_OFFSET": DECOMPRESSED_DATA_SIZE
			}
		}
		IMAGE_DATA_DICT = {
			"": {
				"FILE_OFFSET": DECOMPRESSED_IMAGE_DATA_SIZE
			}
		}
		NAME_DICT = {}
		temp = INFO_OFFSET
		file.seek(INFO_OFFSET)
		while temp < INFO_LIMIT:
			FILE_NAME = b""
			for key in list(NAME_DICT.keys()):
				if NAME_DICT[key] + INFO_OFFSET < temp:
					NAME_DICT.pop(key)
				else:
					FILE_NAME = key
			BYTE = b""
			while BYTE != b"\0":
				FILE_NAME += BYTE
				BYTE = file.read(1)
				LENGTH = 4 * unpack("<I", file.read(3) + b"\0")[0]
				if LENGTH != 0:
					NAME_DICT[FILE_NAME] = LENGTH

			DECODED_NAME = FILE_NAME.decode().replace("\\", sep)
			IS_IMAGE = unpack("<I", file.read(4))[0] == 1
			FILE_OFFSET = unpack("<I", file.read(4))[0]
			FILE_SIZE = unpack("<I", file.read(4))[0]
			if IS_IMAGE:
				file.seek(20, 1)
				#IMAGE_ENTRY = unpack("<I", file.read(4))[0]
				#file.seek(8, 1)
				#WIDHT = unpack("<I", file.read(4))[0]
				#HEIGHT = unpack("<I", file.read(4))[0]
				temp = file.tell()
				IMAGE_DATA_DICT[DECODED_NAME] = {
					"FILE_INFO": temp,
					"FILE_OFFSET": FILE_OFFSET
				}
			else:
				temp = file.tell()
				DATA_DICT[DECODED_NAME] = {
					"FILE_INFO": temp,
					"FILE_OFFSET": FILE_OFFSET
				}
		
		DECODED_NAME = ""
		DATA_SHIFT = 0
		for DECODED_NAME_NEW in sorted(DATA_DICT, key = lambda key: DATA_DICT[key]["FILE_OFFSET"]):
			FILE_OFFSET_NEW = DATA_SHIFT + DATA_DICT[DECODED_NAME_NEW]["FILE_OFFSET"]
			if DECODED_NAME:
				NAME_CHECK = DECODED_NAME.replace("\\", "/").lower()
				FILE_INFO = DATA_DICT[DECODED_NAME]["FILE_INFO"]
				if NAME_CHECK.startswith(pathStartsWith) and NAME_CHECK.endswith(pathEndsWith):
					try:
						if level < 7:
							file_name = osjoin(patch, DECODED_NAME)
							patch_data = open(file_name, "rb").read()
						elif NAME_CHECK[-5:] == ".rton":
							file_name = osjoin(patch, DECODED_NAME[:-5] + ".JSON")
							patch_data = encode_root_object(open(file_name, "rb"))
						else:
							raise FileNotFoundError

						if NAME_CHECK[-5:] == ".rton" and 5 < level and (overrideEncryption == 1 or overrideEncryption < 0 and data[FILE_OFFSET: FILE_OFFSET + 2] == b"\x10\0") and patch_data[0:2] != b"\x10\0":
							patch_data = b'\x10\0' + rijndael_cbc.encrypt(patch_data)
						
						FILE_SIZE = len(patch_data)
						patch_data += extend_to_4096(FILE_SIZE)
						data[FILE_OFFSET: FILE_OFFSET_NEW] = patch_data
						pathout_data[FILE_INFO - 4: FILE_INFO] = pack("<I", FILE_SIZE)
						DATA_SHIFT += FILE_OFFSET + len(patch_data) - FILE_OFFSET_NEW
						FILE_OFFSET_NEW = FILE_OFFSET + len(patch_data)
						print("patched " + relpath(file_name, patchout))
					except FileNotFoundError:
						pass
					except Exception as e:
						error_message(e, " while patching " + file_name)
				pathout_data[FILE_INFO - 8: FILE_INFO - 4] = pack("<I", FILE_OFFSET)
			FILE_OFFSET = FILE_OFFSET_NEW
			DECODED_NAME = DECODED_NAME_NEW
		
		DECODED_NAME = ""
		IMAGE_DATA_SHIFT = 0
		for DECODED_NAME_NEW in sorted(IMAGE_DATA_DICT, key = lambda key: IMAGE_DATA_DICT[key]["FILE_OFFSET"]):
			FILE_OFFSET_NEW = IMAGE_DATA_SHIFT + IMAGE_DATA_DICT[DECODED_NAME_NEW]["FILE_OFFSET"]
			if DECODED_NAME:
				NAME_CHECK = DECODED_NAME.replace("\\", "/").lower()
				FILE_INFO = IMAGE_DATA_DICT[DECODED_NAME]["FILE_INFO"]
				if NAME_CHECK.startswith(pathStartsWith) and NAME_CHECK.endswith(pathEndsWith):
					try:
						#if level < 7:
						file_name = osjoin(patch, DECODED_NAME)
						patch_data = open(file_name, "rb").read()
						#else:
						#	raise FileNotFoundError

						FILE_SIZE = len(patch_data)
						if FILE_SIZE == 0:
							warning_message("No PTX: " + file_name)
						else:
							patch_data += extend_to_4096(FILE_SIZE)
							image_data[FILE_OFFSET: FILE_OFFSET_NEW] = patch_data
							pathout_data[FILE_INFO - 24: FILE_INFO - 20] = pack("<I", FILE_SIZE)
							IMAGE_DATA_SHIFT += FILE_OFFSET + len(patch_data) - FILE_OFFSET_NEW
							FILE_OFFSET_NEW = FILE_OFFSET + len(patch_data)
							print("patched " + relpath(file_name, patchout))
					except FileNotFoundError:
						pass
					except Exception as e:
						error_message(e, " while patching " + file_name)
				pathout_data[FILE_INFO - 28: FILE_INFO - 24] = pack("<I", FILE_OFFSET)
			FILE_OFFSET = FILE_OFFSET_NEW
			DECODED_NAME = DECODED_NAME_NEW
	
	if data != None:
		if overrideDataCompression >= 0:
			COMPRESSION_FLAGS += overrideDataCompression - (COMPRESSION_FLAGS & 2)

		data += extend_to_4096(len(data))
		DECOMPRESSED_DATA_SIZE = len(data)
		if COMPRESSION_FLAGS & 2 == 0: # Decompressed files
			COMPRESSED_DATA_SIZE = DECOMPRESSED_DATA_SIZE
		else:
			data = compress(data, 9)
			data += extend_to_4096(len(data))
			COMPRESSED_DATA_SIZE = len(data)
			
		pathout_data[DATA_OFFSET: IMAGE_DATA_OFFSET] = data
		pathout_data[28:36] = pack("<I", COMPRESSED_DATA_SIZE) + pack("<I", DECOMPRESSED_DATA_SIZE)
		pathout_data[40:44] = pack("<I", DATA_OFFSET + COMPRESSED_DATA_SIZE)
		if level < 5:
			print("patched " + relpath(osjoin(patch, RSG_NAME + ".section"), patchout))
		
	if image_data != None:
		if overrideImageDataCompression >= 0:
			COMPRESSION_FLAGS += overrideImageDataCompression - (COMPRESSION_FLAGS & 1)

		image_data += extend_to_4096(len(image_data))
		DECOMPRESSED_IMAGE_DATA_SIZE = len(image_data)
		if COMPRESSION_FLAGS & 1 == 0: # Decompressed files
			COMPRESSED_IMAGE_DATA_SIZE = DECOMPRESSED_IMAGE_DATA_SIZE
		else:
			image_data = compress(image_data, 9)
			image_data += extend_to_4096(len(image_data))
			COMPRESSED_IMAGE_DATA_SIZE = len(image_data)
		
		pathout_data[IMAGE_DATA_OFFSET:] = image_data
		pathout_data[44:52] = pack("<I", COMPRESSED_IMAGE_DATA_SIZE) + pack("<I", DECOMPRESSED_IMAGE_DATA_SIZE)
		if level < 5:
			print("patched " + relpath(osjoin(patch, RSG_NAME + ".section2"), patchout))
	
	pathout_data[16:20] = pack("<I", COMPRESSION_FLAGS)
	return pathout_data
def rsb_patch_data(file, pathout_data, patch, patchout, level):
	VERSION = unpack('<L', file.read(4))[0]

	file.seek(4, 1)
	HEADER_SIZE = unpack('<L', file.read(4))[0]

	FILE_LIST_SIZE = unpack('<L', file.read(4))[0]
	FILE_LIST_OFFSET = unpack('<L', file.read(4))[0]

	file.seek(8, 1)
	SUBGROUP_LIST_SIZE = unpack('<L', file.read(4))[0]
	SUBGROUP_LIST_OFFSET = unpack('<L', file.read(4))[0]
	SUBGROUP_INFO_ENTRIES = unpack("<I", file.read(4))[0]
	SUBGROUP_INFO_OFFSET = unpack("<I", file.read(4))[0]
	SUBGROUP_INFO_ENTRY_SIZE = unpack('<L', file.read(4))[0]

	GROUP_INFO_ENTRIES = unpack('<L', file.read(4))[0]
	GROUP_INFO_OFFSET = unpack('<L', file.read(4))[0]
	GROUP_INFO_ENTRY_SIZE = unpack('<L', file.read(4))[0]

	GROUP_LIST_SIZE = unpack('<L', file.read(4))[0]
	GROUP_LIST_OFFSET = unpack('<L', file.read(4))[0]

	AUTOPOOL_INFO_ENTRIES = unpack('<L', file.read(4))[0]
	AUTOPOOL_INFO_OFFSET = unpack('<L', file.read(4))[0]
	AUTOPOOL_INFO_ENTRY_SIZE = unpack('<L', file.read(4))[0]

	PTX_INFO_ENTRIES = unpack('<L', file.read(4))[0]
	PTX_INFO_OFFSET = unpack('<L', file.read(4))[0]
	PTX_INFO_ENTRY_SIZE = unpack('<L', file.read(4))[0]

	DIRECTORY_7_OFFSET = unpack('<L', file.read(4))[0]
	DIRECTORY_8_OFFSET = unpack('<L', file.read(4))[0]
	DIRECTORY_9_OFFSET = unpack('<L', file.read(4))[0]

	if VERSION == 4:
		HEADER_SIZE_2 = unpack('<L', file.read(4))[0]

	# TEXTURE_FORMATS = []
	# file.seek(DIRECTORY_6_OFFSET)
	# for IMAGE_ID in range(0, DIRECTORY_6_ENTRIES):
	# 	WIDHT = unpack("<I", file.read(4))[0]
	# 	HEIGHT = unpack("<I", file.read(4))[0]
	# 	WIDHT_BYTES = unpack("<I", file.read(4))[0]
	# 	TEXTURE_FORMAT = unpack("<I", file.read(4))[0]
	# 	if DIRECTORY_6_ENTRY_SIZE == 24:
	# 		COMPRESSED_IMAGE_SIZE = unpack("<I", file.read(4))[0]
	# 		HUNDRED = unpack("<I", file.read(4))[0]

	# 	TEXTURE_FORMATS.append(TEXTURE_FORMAT)
	
	file.seek(SUBGROUP_INFO_OFFSET)
	SUBGROUP_LIST = {}
	for i in range(0, SUBGROUP_INFO_ENTRIES):
		RSG_INFO = file.tell()
		RSG_NAME = file.read(128).strip(b"\0").decode()
		RSG_OFFSET = unpack("<I", file.read(4))[0]
		RSG_SIZE = unpack("<I", file.read(4))[0]
		SUBGROUP_ID = unpack("<I", file.read(4))[0]

		RSG_COMPRESSION_FLAGS = unpack("<I", file.read(4))[0]
		RSG_HEADER_LENGTH = unpack("<I", file.read(4))[0]

		RSG_DATA_OFFSET = unpack("<I", file.read(4))[0]
		RSG_COMPRESSED_DATA_SIZE = unpack("<I", file.read(4))[0]
		RSG_DECOMPRESSED_DATA_SIZE = unpack("<I", file.read(4))[0]
		RSG_DECOMPRESSED_DATA_SIZE_B = unpack("<I", file.read(4))[0]
		
		RSG_IMAGE_DATA_OFFSET = unpack("<I", file.read(4))[0]
		RSG_COMPRESSED_IMAGE_DATA_SIZE = unpack("<I", file.read(4))[0]
		RSG_DECOMPRESSED_IMAGE_DATA_SIZE = unpack("<I", file.read(4))[0]

		file.seek(20, 1)
		IMAGE_ENTRIES = unpack("<I", file.read(4))[0]
		IMAGE_ID = unpack("<I", file.read(4))[0]
		
		SUBGROUP_LIST[RSG_NAME] = {
			"RSG_OFFSET": RSG_OFFSET,
			"RSG_SIZE": RSG_IMAGE_DATA_OFFSET + RSG_COMPRESSED_IMAGE_DATA_SIZE,
			"RSG_INFO": RSG_INFO
		}
	
	RSG_SHIFT = 0
	for RSG_NAME in sorted(SUBGROUP_LIST, key = lambda key: SUBGROUP_LIST[key]["RSG_OFFSET"]):
		RSG_OFFSET = RSG_SHIFT + SUBGROUP_LIST[RSG_NAME]["RSG_OFFSET"]
		RSG_SIZE = SUBGROUP_LIST[RSG_NAME]["RSG_SIZE"]
		info_start = SUBGROUP_LIST[RSG_NAME]["RSG_INFO"]
		RSG_CHECK = RSG_NAME.lower()
		if RSG_CHECK.startswith(rsgStartsWith) and RSG_CHECK.endswith(rsgEndsWith):
			try:
				if level < 4:
					file_path = osjoin(patch, RSG_NAME + ".rsg")
					subdata = bytearray(open(file_path, "rb").read())
				else:
					subdata = pathout_data[RSG_OFFSET: RSG_OFFSET + RSG_SIZE]
					subdata[16:36] = pathout_data[info_start + 140:info_start + 160]
					subdata[40:52] = pathout_data[info_start + 164:info_start + 176]
					subdata = rsg_patch_data(RSG_NAME, BytesIO(subdata), subdata, patch, patchout, level)
				
				subdata[:4] = b"pgsr"
				subdata += extend_to_4096(len(subdata))
				pathout_data[RSG_OFFSET: RSG_OFFSET + RSG_SIZE] = subdata
				pathout_data[info_start + 132:info_start + 136] = pack("<I", len(subdata)) #RSG_SIZE
				pathout_data[info_start + 140:info_start + 176] = subdata[16:36] + subdata[32:36] + subdata[40:52]
				RSG_SHIFT += len(subdata) - RSG_SIZE
				if level < 4:
					print("applied " + relpath(file_path, patchout))
			except FileNotFoundError:
				pass
			except Exception as e:
				error_message(e, " while patching " + RSG_NAME + ".rsg")
		pathout_data[info_start + 128:info_start + 132] = pack("<I", RSG_OFFSET)
	return pathout_data
def file_to_folder(inp, out, patch, level, extensions, pathout, patchout):
# Recursive file convert function
	if isfile(inp):
		try:
			file = open(inp, "rb")
			HEADER = file.read(4)
			COMPRESSED = HEADER == b"\xD4\xFE\xAD\xDE" and 2 < level
			if COMPRESSED:
				DECOMPRESSED_SIZE = unpack("<I", file.read(4))[0]
				pathout_data = decompress(file.read())
				file = BytesIO(pathout_data)
				file.name = inp
				HEADER = file.read(4)

			if HEADER == b"1bsr":
				if not COMPRESSED:
					pathout_data = HEADER + file.read()
					file.seek(4)
				
				if level > 2:
					pathout_data = rsb_patch_data(file, bytearray(pathout_data), patch, patchout, level)
				if level < 3 or COMPRESSED:
					tag, extension = splitext(out)
					tag += ".tag" + extension
					open(tag, "wb").write(md5(pathout_data).hexdigest().upper().encode() + b"\r\n")
					green_print("wrote " + relpath(tag, pathout))
					pathout_data = b"\xD4\xFE\xAD\xDE" + pack("<I", len(pathout_data)) + compress(pathout_data, level = 9)
				
				open(out, "wb").write(pathout_data)
				green_print("wrote " + relpath(out, pathout))
			elif HEADER == b"pgsr":
				try:
					pathout_data = bytearray(HEADER + file.read())
					file.seek(0)
					pathout_data = rsg_patch_data("data", file, pathout_data, patch, patchout, level)
					open(out, "wb").write(pathout_data)
					green_print("wrote " + relpath(out, pathout))
				except Exception as e:
					error_message(e, " while patching " + inp)
			elif 2 < level:
				warning_message("UNKNOWN 1BSR HEADER (" + HEADER.hex() + ") in " + inp)
		except Exception as e:
			error_message(e, " in " + inp + " pos " + repr(file.tell()), "Failed OBBPatch: ")
	elif isdir(inp):
		makedirs(out, exist_ok = True)
		makedirs(patch, exist_ok = True)
		for entry in sorted(listdir(inp)):
			input_file = osjoin(inp, entry)
			output_file = osjoin(out, entry)
			patch_file = osjoin(patch, entry)
			if isfile(input_file):
				if level < 3:
					output_file += ".smf"
				if entry.lower().endswith(extensions):
					file_to_folder(input_file, output_file, splitext(patch_file)[0], level, extensions, pathout, patchout)
			elif input_file != pathout and inp != patchout:
				file_to_folder(input_file, output_file, patch_file, level, extensions, pathout, patchout)
def conversion(inp, out, level, extensions, pathout):
# Convert file
	if isfile(inp):
		try:
			file = open(inp, "rb")
			if file.read(4) == b"RTON":
				if level < 7:
					open(out,"wb").write(b'\x10\0' + rijndael_cbc.encrypt(b"RTON" + file.read()))
					print("wrote " + relpath(out, pathout))
			elif level > 6:
				file.seek(0)
				encoded_data = encode_root_object(file)
				open(out, "wb").write(encoded_data)
				print("wrote " + relpath(out, pathout))
		except Exception as e:
			error_message(e, " in " + inp)
	elif isdir(inp):
		makedirs(out, exist_ok = True)
		for entry in listdir(inp):
			input_file = osjoin(inp, entry)
			output_file = osjoin(out, entry)
			if isfile(input_file):
				check = entry.lower()
				if level > 6:
					output_file = output_file[:-5]
					if "" == splitext(output_file)[1] and not check.startswith(RTONNoExtensions):
						output_file += ".rton"
				if check[-5:] == extensions:
					conversion(input_file, output_file, level, extensions, pathout)
			elif input_file != pathout:
				conversion(input_file, output_file, level, extensions, pathout)
# Start of the code
try:
	application_path = initialize()
	logerror = LogError(osjoin(application_path, "fail.txt"))
	error_message = logerror.error_message
	warning_message = logerror.warning_message
	input_level = logerror.input_level
	logerror.check_version(3, 9, 0)
	
	print("""\033[95m
\033[1mOBBPatcher v1.2.0 (c) 2022 Nineteendo\033[22m
\033[1mCode based on:\033[22m Luigi Auriemma, Small Pea & 1Zulu
\033[1mDocumentation:\033[22m Watto Studios, YingFengTingYu, TwinKleS-C & h3x4n1um
\033[1mFollow PyVZ2 development:\033[22m \033[4mhttps://discord.gg/CVZdcGKVSw\033[24m
\033[0m""")
	options = logerror.load_template(options, osjoin(application_path, "options"), 2)
	level_to_name = ["SPECIFY", "SMF", "RSB", "RSG", "SECTION", "ENCRYPTED", "ENCODED", "DECODED"]
	list_levels(level_to_name)
	options["encodedUnpackLevel"] = input_level("ENCODED Unpack Level", 6, 7, options["encodedUnpackLevel"])
	options["encryptedUnpackLevel"] = input_level("ENCRYPTED Unpack Level", 5, 6, options["encryptedUnpackLevel"])
	options["rsgUnpackLevel"] = input_level("RSG/RSB/SMF Unpack Level", 3, 7, options["rsgUnpackLevel"])
	options["rsbUnpackLevel"] = input_level("RSB/SMF Unpack Level", 2, 3, options["rsbUnpackLevel"])
	options["smfUnpackLevel"] = input_level("SMF Unpack Level", 1, 2, options["smfUnpackLevel"])
	
	if options["rsgStartsWithIgnore"]:
		rsgStartsWith = ""
	else:
		rsgStartsWith = options["rsgStartsWith"]	
	if options["rsgEndsWithIgnore"]:
		rsgEndsWith = ""
	else:
		rsgEndsWith = options["rsgEndsWith"]
	
	rijndael_cbc = RijndaelCBC(str.encode(options["encryptionKey"]), 24)
	if 7 >= options["rsgUnpackLevel"] > 3:
		list_levels(["SPECIFY", "DEFAULT", "DISABLE", "ENABLE"])
		overrideDataCompression = 2 * (input_level("Compress Data Override", 1, 3, options["overrideDataCompression"]) - 2)
		overrideImageDataCompression = input_level("Compress Image Data Override", 1, 3, options["overrideImageDataCompression"]) - 2
	if 7 >= options["rsgUnpackLevel"] > 5:
		overrideEncryption = input_level("Encrypt Override", 1, 3, options["overrideEncryption"]) - 2
	
	if options["pathEndsWithIgnore"]:
		pathEndsWith = ""
	else:
		pathEndsWith = options["pathEndsWith"]
	if options["pathStartsWithIgnore"]:
		pathStartsWith = ""
	else:
		pathStartsWith = options["pathStartsWith"]
	RTONNoExtensions = options["RTONNoExtensions"]
	encode_root_object = JSONDecoder().encode_root_object

	blue_print("\nWorking directory: " + getcwd())
	if 7 >= options["encodedUnpackLevel"] > 6:
		encoded_input = path_input("ENCODED " + level_to_name[options["encodedUnpackLevel"]] + " Input file or directory", options["encodedUnpacked"])
		if isfile(encoded_input):
			encoded_output = path_input("ENCODED Output file", options["encodedPacked"])
		else:
			encoded_output = path_input("ENCODED Output directory", options["encodedPacked"])
	if 6 >= options["encryptedUnpackLevel"] > 5:
		encrypted_input = path_input("ENCRYPTED " + level_to_name[options["encryptedUnpackLevel"]] + " Input file or directory", options["encryptedUnpacked"])
		if isfile(encrypted_input):
			encrypted_output = path_input("ENCRYPTED Output file", options["encryptedPacked"])
		else:
			encrypted_output = path_input("ENCRYPTED Output directory", options["encryptedPacked"])
	if 7 >= options["rsgUnpackLevel"] > 3:
		rsg_input = path_input("RSG/RSB/SMF Input file or directory", options["rsgPacked"])
		if isfile(rsg_input):
			rsg_output = path_input("RSG/RSB/SMF Modded file", options["rsgPatched"])
		else:
			rsg_output = path_input("RSG/RSB/SMF Modded directory", options["rsgPatched"])
		rsg_patch = path_input("RSG/RSB/SMF " + level_to_name[options["rsgUnpackLevel"]] + " Patch directory", options["rsgUnpacked"])
	
	if 3 >= options["rsbUnpackLevel"] > 2:
		rsb_input = path_input("RSB/SMF Input file or directory", options["rsbPacked"])
		if isfile(rsb_input):
			rsb_output = path_input("RSB/SMF Modded file", options["rsbPatched"])
		else:
			rsb_output = path_input("RSB/SMF Modded directory", options["rsbPatched"])
		rsb_patch = path_input("RSB/SMF " + level_to_name[options["rsbUnpackLevel"]] + " Patch directory", options["rsbUnpacked"])
	
	if 2 >= options["smfUnpackLevel"] > 1:
		smf_input = path_input("SMF " + level_to_name[options["smfUnpackLevel"]] + " Input file or directory", options["smfUnpacked"])
		if isfile(smf_input):
			smf_output = path_input("SMF Output file", options["smfPacked"])
		else:
			smf_output = path_input("SMF Output directory", options["smfPacked"])

	# Start file_to_folder
	start_time = datetime.datetime.now()
	if 7 >= options["encodedUnpackLevel"] > 6:
		conversion(encoded_input, encoded_output, options["encodedUnpackLevel"], ".json", dirname(encoded_output))
	if 6 >= options["encryptedUnpackLevel"] > 5:
		conversion(encrypted_input, encrypted_output, options["encryptedUnpackLevel"], ".rton", dirname(encrypted_output))
	if 7 >= options["rsgUnpackLevel"] > 3:
		file_to_folder(rsg_input, rsg_output, rsg_patch, options["rsgUnpackLevel"], options["rsgExtensions"], dirname(rsg_output), rsg_patch)
	if 3 >= options["rsbUnpackLevel"] > 2:
		file_to_folder(rsb_input, rsb_output, rsb_patch, options["rsbUnpackLevel"], options["rsbExtensions"], dirname(rsb_output), rsb_patch)
	if 2 >= options["smfUnpackLevel"] > 1:
		file_to_folder(smf_input, smf_output, smf_output, options["smfUnpackLevel"], options["rsbExtensions"], dirname(smf_output), dirname(smf_output))

	logerror.finish_program("finished patching in", start_time)
except Exception as e:
	error_message(e)
except BaseException as e:
	warning_message(type(e).__name__ + " : " + str(e))
logerror.close() # Close log