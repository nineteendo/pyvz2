# Import libraries
import datetime
from hashlib import md5
from io import BytesIO
from json import load
from libraries.pyvz2rijndael import RijndaelCBC
from libraries.pyvz2rton import JSONDecoder
from os import makedirs, listdir, system, getcwd, sep
from os.path import isdir, isfile, realpath, join as osjoin, dirname, relpath, basename, splitext
#from PIL import Image
from struct import pack, unpack
import sys
from traceback import format_exc
from zlib import compress, decompress

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
	"overrideEncryption": 1,
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
	"indent": -1,
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
def error_message(string):
# Print & log error
	string += "\n" + format_exc()
	fail.write(string + "\n")
	fail.flush()
	print("\033[91m" + string + "\033[0m")
def warning_message(string):
# Print & log warning
	fail.write("\t" + string + "\n")
	fail.flush()
	print("\33[93m" + string + "\33[0m")
def blue_print(text):
# Print in blue text
	print("\033[94m"+ text + "\033[0m")
def green_print(text):
# Print in green text
	print("\033[32m"+ text + "\033[0m")
def bold_input(text):
# Input in bold text
	return input("\033[1m"+ text + "\033[0m: ")
def path_input(text, preset):
# Input hybrid path
	if preset != "":
		print("\033[1m"+ text + "\033[0m: " + preset)
		return preset
	else:
		string = ""
		newstring = bold_input(text)
		while newstring or string == "":
			string = ""
			quoted = 0
			escaped = False
			temp_string = ""
			confirm = False
			for char in newstring:
				if escaped:
					if quoted != 1 and char == "'" or quoted != 2 and char == '"' or quoted == 0 and char in "\\ ":
						string += temp_string + char
						confirm = True
					else:
						string += temp_string + "\\" + char
					temp_string = ""
					escaped = False
				elif char == "\\":
					escaped = True
				elif quoted != 2 and char == "'":
					quoted = 1 - quoted
				elif quoted != 1 and char == '"':
					quoted = 2 - quoted
				elif quoted != 0 or char != " ":
					string += temp_string + char
					temp_string = ""
				else:
					temp_string += " "
			if string == "":
				newstring = bold_input("\033[91mEnter a path")
			else:
				newstring = ""
				string = realpath(string)
				if confirm:
					newstring = bold_input("Confirm \033[100m" + string)
		return string
# RSG Patch functions
class SectionError(Exception):
	pass
def extend_to_4096(number):
	return b"\0" * ((4096 - number) & 4095)
def rsg_patch_data(RSG_NAME, file, pathout_data, patch, patchout, level):
# Patch RGSP file
	if file.read(4) == b"pgsr":
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
			blue_print("Decompressing...")
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
				blue_print("Decompressing...")
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
								patch_data = parse_json(open(file_name, "rb"))
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
							error_message(type(e).__name__ + " while patching " + file_name + ": " + str(e))	
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
							if level < 7:
								file_name = osjoin(patch, DECODED_NAME)
								patch_data = open(file_name, "rb").read()
							else:
								raise FileNotFoundError

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
							error_message(type(e).__name__ + " while patching " + file_name + ": " + str(e))
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
				blue_print("Compressing...")
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
				blue_print("Compressing...")
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
	FILE_DATA_OFFSET = unpack('<L', file.read(4))[0]

	DIRECTORY_0_LENGTH = unpack('<L', file.read(4))[0]
	DIRECTORY_0_OFFSET = unpack('<L', file.read(4))[0]

	file.seek(8, 1)
	DIRECTORY_1_LENGTH = unpack('<L', file.read(4))[0]
	DIRECTORY_1_OFFSET = unpack('<L', file.read(4))[0]
	DIRECTORY_4_ENTRIES = unpack("<I", file.read(4))[0]
	DIRECTORY_4_OFFSET = unpack("<I", file.read(4))[0]
	DIRECTORY_4_ENTRY_SIZE = unpack('<L', file.read(4))[0]

	DIRECTORY_2_ENTRIES = unpack('<L', file.read(4))[0]
	DIRECTORY_2_OFFSET = unpack('<L', file.read(4))[0]
	DIRECTORY_2_ENTRY_SIZE = unpack('<L', file.read(4))[0]

	DIRECTORY_3_LENGTH = unpack('<L', file.read(4))[0]
	DIRECTORY_3_OFFSET = unpack('<L', file.read(4))[0]

	DIRECTORY_5_ENTRIES = unpack('<L', file.read(4))[0]
	DIRECTORY_5_OFFSET = unpack('<L', file.read(4))[0]
	DIRECTORY_5_ENTRY_SIZE = unpack('<L', file.read(4))[0]

	DIRECTORY_6_ENTRIES = unpack('<L', file.read(4))[0]
	DIRECTORY_6_OFFSET = unpack('<L', file.read(4))[0]
	DIRECTORY_6_ENTRY_SIZE = unpack('<L', file.read(4))[0]

	DIRECTORY_7_OFFSET = unpack('<L', file.read(4))[0]
	DIRECTORY_8_OFFSET = unpack('<L', file.read(4))[0]
	DIRECTORY_9_OFFSET = unpack('<L', file.read(4))[0]

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
	
	RSG_SHIFT = 0
	file.seek(DIRECTORY_4_OFFSET)
	for i in range(0, DIRECTORY_4_ENTRIES):
		info_start = file.tell()
		RSG_NAME = file.read(128).strip(b"\0").decode()
		RSG_OFFSET = RSG_SHIFT + unpack("<I", file.read(4))[0]
		RSG_SIZE = unpack("<I", file.read(4))[0]
		
		RSG_ID = unpack("<I", file.read(4))[0]

		COMPRESSION_FLAGS = unpack("<I", file.read(4))[0]
		HEADER_LENGTH = unpack("<I", file.read(4))[0]

		DATA_OFFSET = unpack("<I", file.read(4))[0]
		COMPRESSED_DATA_SIZE = unpack("<I", file.read(4))[0]
		DECOMPRESSED_DATA_SIZE = unpack("<I", file.read(4))[0]
		DECOMPRESSED_DATA_SIZE_B = unpack("<I", file.read(4))[0]
		
		IMAGE_DATA_OFFSET = unpack("<I", file.read(4))[0]
		COMPRESSED_IMAGE_DATA_SIZE = unpack("<I", file.read(4))[0]
		DECOMPRESSED_IMAGE_DATA_SIZE = unpack("<I", file.read(4))[0]

		file.seek(20, 1)
		IMAGE_ENTRIES = unpack("<I", file.read(4))[0]
		IMAGE_ID = unpack("<I", file.read(4))[0]
		RSG_NAME_TESTS = RSG_NAME.lower()
		if RSG_NAME_TESTS.startswith(rsgStartsWith) and RSG_NAME_TESTS.endswith(rsgEndsWith):
			try:
				if level < 4:
					file_path = osjoin(patch, RSG_NAME + ".rsg")
					patch_data = open(file_path, "rb").read()
				else:
					patch_data = rsg_patch_data(RSG_NAME, BytesIO(pathout_data[RSG_OFFSET: RSG_OFFSET + RSG_SIZE]), pathout_data[RSG_OFFSET: RSG_OFFSET + RSG_SIZE], patch, patchout, level)
				
				patch_data += extend_to_4096(len(patch_data))
				pathout_data[RSG_OFFSET: RSG_OFFSET + RSG_SIZE] = patch_data
				pathout_data[info_start + 132:info_start + 136] = pack("<I", len(patch_data)) #RSG_SIZE
				pathout_data[info_start + 140:info_start + 176] = patch_data[16:36] + patch_data[32:36] + patch_data[40:52]
				RSG_SHIFT += len(patch_data) - RSG_SIZE
				if level < 4:
					print("applied " + relpath(file_path, patchout))
			except FileNotFoundError:
				pass
			except Exception as e:
				error_message(type(e).__name__ + " while patching " + RSG_NAME + ".rsg: " + str(e))
		pathout_data[info_start + 128:info_start + 132] = pack("<I", RSG_OFFSET)
	return pathout_data
def file_to_folder(inp, out, patch, level, extensions, pathout, patchout):
# Recursive file convert function
	check = inp.lower()
	if isdir(inp):
		makedirs(out, exist_ok = True)
		makedirs(patch, exist_ok = True)
		for entry in sorted(listdir(inp)):
			input_file = osjoin(inp, entry)
			output_file = osjoin(out, entry)
			patch_file = osjoin(patch, entry)
			if isfile(input_file):
				file_to_folder(input_file, output_file, splitext(patch_file)[0], level, extensions, pathout, patchout)
			elif input_file != pathout and inp != patchout:
				file_to_folder(input_file, output_file, patch_file, level, extensions, pathout, patchout)
	elif isfile(inp) and check.endswith(extensions):
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
				
				if level < 3:
					out += ".smf"
				else:
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
					error_message(type(e).__name__ + " while patching " + inp + str(e))
		except Exception as e:
			error_message("Failed OBBPatch " + type(e).__name__ + " in " + inp + " pos " + str(file.tell()) + ": " + str(e))
def conversion(inp, out, pathout, level, extension):
# Convert file
	if isfile(inp) and inp.lower()[-5:] == extension:
		try:
			file = open(inp, "rb")
			if file.read(4) != b"RTON": # Ignore CDN files
				file.seek(0)
				encoded_data = parse_json(file)
				# No extension
				if out.lower()[-5:] == ".json":
					out = out[:-5]
				if "" == splitext(out)[1] and not basename(out).lower().startswith(RTONNoExtensions):
					out += ".rton"
				open(out, "wb").write(encoded_data)
				print("wrote " + relpath(out, pathout))
			elif level < 7:
				open(out,"wb").write(b'\x10\0' + rijndael_cbc.encrypt(b"RTON" + file.read()))
				print("wrote " + relpath(out, pathout))
		except Exception as e:
			error_message(type(e).__name__ + " in " + inp + ": " + str(e))
	elif isdir(inp):
		makedirs(out, exist_ok = True)
		for entry in listdir(inp):
			input_file = osjoin(inp, entry)
			if isfile(input_file) or input_file != pathout:
				conversion(input_file, osjoin(out, entry), pathout, level, extension)
def list_levels(levels):
	blue_print(" ".join([repr(i) + "-" + levels[i] for i in range(len(levels))]))
def input_level(text, minimum, maximum):
# Set input level for conversion
	try:
		return max(minimum, min(maximum, int(bold_input(text + " (" + str(minimum) + "-" + str(maximum) + ")"))))
	except Exception as e:
		error_message(type(e).__name__ + " : " + str(e))
		warning_message("Defaulting to " + str(minimum))
		return minimum
# Start of the code
try:
	system("")
	if getattr(sys, "frozen", False):
		application_path = dirname(sys.executable)
	else:
		application_path = sys.path[0]
	fail = open(osjoin(application_path, "fail.txt"), "w")
	if sys.version_info[0] < 3:
		raise RuntimeError("Must be using Python 3")
	
	print("\033[95m\033[1mOBBUnpacker v1.1.6b (C) 2022 by Nineteendo\nCode based on: Luigi Auriemma, Small Pea & 1Zulu\nDocumentation: Watto Studios, YingFengTingYu & h3x4n1um\033[0m\n")
	try:
		folder = osjoin(application_path, "options")
		templates = {}
		blue_print("\033[1mTEMPLATES:\033[0m")
		for entry in sorted(listdir(folder)):
			if isfile(osjoin(folder, entry)):
				file, extension = splitext(entry)
				if extension == ".json" and entry.count("--") == 2:
					key, unpack_name, patch_name = file.split("--")
					if not key in templates:
						blue_print("\033[1m" + key + "\033[0m: " + patch_name)
						templates[key] = unpack_name + "--" + patch_name + ".json"
				elif entry.count("--") > 0:
					print(file.split("--")[1])
		length = len(templates)
		if length == 0:
			green_print("Loaded default template")
		else:
			if length > 1:
				key = bold_input("Choose template")
			
			name = key + "--" + templates[key]
			newoptions = load(open(osjoin(folder, name), "rb"))
			for key in options:
				if key in newoptions and newoptions[key] != options[key]:
					if type(options[key]) == type(newoptions[key]):
						options[key] = newoptions[key]
					elif isinstance(options[key], tuple) and isinstance(newoptions[key], list):
						options[key] = tuple([str(i).lower() for i in newoptions[key]])
					elif key == "indent" and newoptions[key] == None:
						options[key] = newoptions[key]
			green_print("Loaded template " + name)
	except Exception as e:
		error_message(type(e).__name__ + " while loading options: " + str(e))
		warning_message("Falling back to default options.")
	
	level_to_name = ["SPECIFY", "SMF", "RSB", "RSG", "SECTION", "ENCRYPTED", "ENCODED", "DECODED"]
	if options["smfUnpackLevel"] <= 0 or options["rsbUnpackLevel"] <= 1 or options["rsgUnpackLevel"] <= 2 or options["encryptedUnpackLevel"] <= 4 or options["encodedUnpackLevel"] <= 5:
		list_levels(level_to_name)
	if options["encodedUnpackLevel"] <= 5:
		options["encodedUnpackLevel"] = input_level("ENCODED Unpack Level", 6, 7)
	if options["encryptedUnpackLevel"] <= 4:
		options["encodedUnpackLevel"] = input_level("ENCRYPTED Unpack Level", 5, 6)
	if options["rsgUnpackLevel"] <= 2:
		options["rsgUnpackLevel"] = input_level("RSG/RSB/SMF Unpack Level", 3, 7)
	if options["rsbUnpackLevel"] <= 1:
		options["rsbUnpackLevel"] = input_level("RSB/SMF Unpack Level", 2, 3)
	if options["smfUnpackLevel"] <= 0:
		options["smfUnpackLevel"] = input_level("SMF Unpack Level", 1, 2)
	
	if options["rsgStartsWithIgnore"]:
		rsgStartsWith = ""
	else:
		rsgStartsWith = options["rsgStartsWith"]	
	if options["rsgEndsWithIgnore"]:
		rsgEndsWith = ""
	else:
		rsgEndsWith = options["rsgEndsWith"]
	
	rijndael_cbc = RijndaelCBC(str.encode(options["encryptionKey"]), 24)
	if options["overrideDataCompression"] <= 0 or options["overrideImageDataCompression"] <= 0 or options["overrideEncryption"] <= 0:
		list_levels(["DEFAULT", "DISABLE", "ENABLE"])
	if options["overrideDataCompression"] <= 0:
		options["overrideDataCompression"] = input_level("Compress Data Override", 1, 3)
	overrideDataCompression = 2 * (options["overrideDataCompression"] - 2)
	if options["overrideImageDataCompression"] <= 0:
		options["overrideImageDataCompression"] = input_level("Compress Image Data Override", 1, 3)
	overrideImageDataCompression = options["overrideImageDataCompression"] - 2
	if options["overrideEncryption"] <= 0:
		options["overrideEncryption"] = input_level("Encrypt Override", 1, 3)
	overrideEncryption = options["overrideEncryption"] - 2
	if options["pathEndsWithIgnore"]:
		pathEndsWith = ""
	else:
		pathEndsWith = options["pathEndsWith"]
	if options["pathStartsWithIgnore"]:
		pathStartsWith = ""
	else:
		pathStartsWith = options["pathStartsWith"]
	RTONNoExtensions = options["RTONNoExtensions"]
	parse_json = JSONDecoder().parse_json

	blue_print("Working directory: " + getcwd())
	if 7 >= options["encodedUnpackLevel"] > 6:
		encoded_input = path_input("ENCODED " + level_to_name[options["encodedUnpackLevel"]] + " Input file or directory", options["encodedUnpacked"])
		if isfile(encoded_input):
			encoded_output = path_input("ENCODED Output file", options["encodedPacked"])
			if encoded_output.lower()[:-5] == ".json":
				encoded_output = encoded_output[:-5]
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
		smf_input = path_input("SMF " + level_to_name[options["smfUnpackLevel"]] + " Input file or directory")
		if isfile(smf_input):
			smf_output = path_input("SMF Output file", options["smfUnpacked"])
		else:
			smf_output = path_input("SMF Output directory", options["smfPacked"])

	# Start file_to_folder
	start_time = datetime.datetime.now()
	if 7 >= options["encodedUnpackLevel"] > 6:
		conversion(encoded_input, encoded_output, dirname(encoded_output), options["encodedUnpackLevel"], ".json")
	if 6 >= options["encryptedUnpackLevel"] > 5:
		conversion(encrypted_input, encrypted_output, dirname(encrypted_output), options["encryptedUnpackLevel"], ".rton")
	if 7 >= options["rsgUnpackLevel"] > 3:
		file_to_folder(rsg_input, rsg_output, rsg_patch, options["rsgUnpackLevel"], options["rsgExtensions"], dirname(rsg_output), rsg_patch)
	if 3 >= options["rsbUnpackLevel"] > 2:
		file_to_folder(rsb_input, rsb_output, rsb_patch, options["rsbUnpackLevel"], options["rsbExtensions"], dirname(rsb_output), rsb_patch)
	if 2 >= options["smfUnpackLevel"] > 1:
		file_to_folder(smf_input, smf_output, smf_output, options["smfUnpackLevel"], options["rsbExtensions"], dirname(smf_output), dirname(smf_output))

	green_print("finished patching in " + str(datetime.datetime.now() - start_time))
	if fail.tell() > 0:
		print("\33[93m" + "Errors occured, check: " + fail.name + "\33[0m")
	bold_input("\033[95mPRESS [ENTER]")
except Exception as e:
	error_message(type(e).__name__ + " : " + str(e))
except BaseException as e:
	warning_message(type(e).__name__ + " : " + str(e))
fail.close() # Close log