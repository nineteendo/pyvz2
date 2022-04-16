# Import libraries
import datetime
from hashlib import md5
from io import BytesIO
from json import load
from libraries.pyvz2rijndael import RijndaelCBC
from libraries.pyvz2rton import JSONDecoder
from os import makedirs, listdir, system, getcwd, sep
from os.path import isdir, isfile, realpath, join as osjoin, dirname, relpath, basename, splitext
from PIL import Image
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
	"smfUnpackLevel": 1,
	# RSB options
	"endsWith": (
		".rton",
	),
	"endsWithIgnore": False,
	"rsbExtensions": (
		".1bsr",
		".rsb1",
		".bsr",
		".rsb",
		".rsb.smf",
		".obb"
	),
	"rsbUnpackLevel": 7,
	"rsgpEndsWith": (),
	"rsgpEndsWithIgnore": True,
	"rsgpStartsWith": (
		"packages",
		"worldpackages_"
	),
	"rsgpStartsWithIgnore": False,
	"startsWith": (
		"packages/",
	),
	"startsWithIgnore": False,
	# Encryption
	"encryptedExtensions": (
		".rton",
	),
	"encryptedUnpackLevel": 5,
	"encryptionKey": "00000000000000000000000000000000",
	# RTON options
	"comma": 0,
	"doublePoint": 1,
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
def path_input(text):
# Input hybrid path
	string = ""
	newstring = bold_input(text)
	while newstring or string == "":
		string = ""
		quoted = 0
		escaped = False
		tempstring = ""
		confirm = False
		for char in newstring:
			if escaped:
				if quoted != 1 and char == "'" or quoted != 2 and char == '"' or quoted == 0 and char in "\\ ":
					string += tempstring + char
					confirm = True
				else:
					string += tempstring + "\\" + char
				
				tempstring = ""
				escaped = False
			elif char == "\\":
				escaped = True
			elif quoted != 2 and char == "'":
				quoted = 1 - quoted
			elif quoted != 1 and char == '"':
				quoted = 2 - quoted
			elif quoted != 0 or char != " ":
				string += tempstring + char
				tempstring = ""
			else:
				tempstring += " "
		
		if string == "":
			newstring = bold_input("\033[91mEnter a path")
		else:
			newstring = ""
			string = realpath(string)
			if confirm:
				newstring = bold_input("Confirm \033[100m" + string)
	return string
def input_level(text, minimum, maximum):
# Set input level for conversion
	try:
		return max(minimum, min(maximum, int(bold_input(text + "(" + str(minimum) + "-" + str(maximum) + ")"))))
	except Exception as e:
		error_message(type(e).__name__ + " : " + str(e))
		warning_message("Defaulting to " + str(minimum))
		return minimum
# RSGP Patch functions
def rsgp_patch_data(rsgp_NAME, rsgp_OFFSET, file, pathout_data, patch, patchout, level):
# Patch RGSP file
	if file.read(4) == b"pgsr":
		rsgp_VERSION = unpack("<I", file.read(4))[0]
			
		file.seek(8, 1)
		COMPRESSION_FLAGS = unpack("<I", file.read(4))[0]
		rsgp_BASE = unpack("<I", file.read(4))[0]

		DATA_OFFSET = unpack("<I", file.read(4))[0]
		COMPRESSED_DATA_SIZE = unpack("<I", file.read(4))[0]
		UNCOMPRESSED_DATA_SIZE = unpack("<I", file.read(4))[0]
		
		file.seek(4, 1)
		IMAGE_DATA_OFFSET = unpack("<I", file.read(4))[0]
		COMPRESSED_IMAGE_DATA_SIZE = unpack("<I", file.read(4))[0]
		UNCOMPRESSED_IMAGE_DATA_SIZE = unpack("<I", file.read(4))[0]
		
		file.seek(20, 1)
		INFO_SIZE = unpack("<I", file.read(4))[0]
		INFO_OFFSET = rsgp_OFFSET + unpack("<I", file.read(4))[0]
		INFO_LIMIT = INFO_OFFSET + INFO_SIZE

		data = None
		if UNCOMPRESSED_DATA_SIZE != 0:
			if level < 5:
				try:
					data = open(osjoin(patch, rsgp_NAME + ".section"), "rb").read()
				except FileNotFoundError:
					pass
			elif COMPRESSION_FLAGS & 2 != 0: # Compressed files
				blue_print("Decompressing...")
				file.seek(rsgp_OFFSET + DATA_OFFSET)
				data = decompress(file.read(COMPRESSED_DATA_SIZE))
			else: # Uncompressed files
				file.seek(rsgp_OFFSET + DATA_OFFSET)
				data = file.read(COMPRESSED_DATA_SIZE)
			
		image_data = None
		if UNCOMPRESSED_IMAGE_DATA_SIZE != 0:
			if level < 5:
				try:
					image_data = open(osjoin(patch, rsgp_NAME + ".section2"), "rb").read()
				except FileNotFoundError:
					pass
			elif COMPRESSION_FLAGS & 1 != 0:
				blue_print("Decompressing...")
				file.seek(rsgp_OFFSET + IMAGE_DATA_OFFSET)
				image_data = decompress(file.read(COMPRESSED_IMAGE_DATA_SIZE))
			else: # Uncompressed files
				file.seek(rsgp_OFFSET + IMAGE_DATA_OFFSET)
				image_data = file.read(COMPRESSED_IMAGE_DATA_SIZE)

		if 4 < level:
			DATA_DICT = {}
			IMAGE_DICT = {}
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
				while BYTE != b"\x00":
					FILE_NAME += BYTE
					BYTE = file.read(1)
					LENGTH = 4 * unpack("<I", file.read(3) + b"\x00")[0]
					if LENGTH != 0:
						NAME_DICT[FILE_NAME] = LENGTH

				DECODED_NAME = FILE_NAME.decode().replace("\\", sep)
				IS_IMAGE = unpack("<I", file.read(4))[0] == 1
				FILE_OFFSET = unpack("<I", file.read(4))[0]
				FILE_SIZE = unpack("<I", file.read(4))[0]
				if IS_IMAGE:
					IMAGE_ENTRY = unpack("<I", file.read(4))[0]
					file.seek(8, 1)
					WIDHT = unpack("<I", file.read(4))[0]
					HEIGHT = unpack("<I", file.read(4))[0]
					IMAGE_DICT[DECODED_NAME] = {
						"FILE_INFO": file.tell(),
						"FILE_OFFSET": FILE_OFFSET
					}
				else:
					DATA_DICT[DECODED_NAME] = {
						"FILE_INFO": file.tell(),
						"FILE_OFFSET": FILE_OFFSET
					}

			DATA_DICT[""] = {
				"FILE_OFFSET": UNCOMPRESSED_DATA_SIZE
			}
			IMAGE_DICT[""] = {
				"FILE_OFFSET": UNCOMPRESSED_IMAGE_DATA_SIZE
			}
			
			DECODED_NAME = ""
			for DECODED_NAME_NEW in sorted(DATA_DICT, key = lambda key: DATA_DICT[key]["FILE_OFFSET"]):
				FILE_OFFSET_NEW = DATA_DICT[DECODED_NAME_NEW]["FILE_OFFSET"]
				NAME_CHECK = DECODED_NAME.replace("\\", "/").lower()
				if DECODED_NAME and NAME_CHECK.startswith(startsWith) and NAME_CHECK.endswith(endsWith):
					try:
						if level < 7:
							file_name = osjoin(patch, DECODED_NAME)
							patch_data = open(file_name, "rb").read()
						elif NAME_CHECK[-5:] == ".rton":
							file_name = osjoin(patch, DECODED_NAME[:-5] + ".JSON")
							patch_data = parse_json(open(file_name, "rb"))
						else:
							raise FileNotFoundError

						if NAME_CHECK[-5:] == ".rton" and data[FILE_OFFSET: FILE_OFFSET + 2] == b"\x10\x00" and 5 < level:
							patch_data = b'\x10\x00' + rijndael_cbc.encrypt(patch_data)
						
						FILE_INFO = DATA_DICT[DECODED_NAME]["FILE_INFO"]
						FILE_SIZE = len(patch_data)
						MAX_FILE_SIZE = FILE_OFFSET_NEW - FILE_OFFSET
						data[FILE_OFFSET: FILE_OFFSET + MAX_FILE_SIZE] = patch_data + bytes(MAX_FILE_SIZE - FILE_SIZE)
						pathout_data[FILE_INFO - 4: FILE_INFO] = pack("<I", FILE_SIZE)
						print("patched " + relpath(file_name, patchout))
					except FileNotFoundError:
						pass
					except Exception as e:
						error_message(type(e).__name__ + " while patching " + file_name + ": " + str(e))
				FILE_OFFSET = FILE_OFFSET_NEW
				DECODED_NAME = DECODED_NAME_NEW
			
			for DECODED_NAME_NEW in sorted(IMAGE_DICT, key = lambda key: IMAGE_DICT[key]["FILE_OFFSET"]):
				FILE_OFFSET_NEW = IMAGE_DICT[DECODED_NAME_NEW]["FILE_OFFSET"]
				NAME_CHECK = DECODED_NAME.replace("\\", "/").lower()
				if DECODED_NAME and NAME_CHECK.startswith(startsWith) and NAME_CHECK.endswith(endsWith):
					try:
						if level < 7:
							file_name = osjoin(patch, DECODED_NAME)
							patch_data = open(file_name, "rb").read()
						else:
							raise FileNotFoundError

						FILE_INFO = IMAGE_DICT[DECODED_NAME]["FILE_INFO"]
						FILE_SIZE = len(patch_data)
						MAX_FILE_SIZE = FILE_OFFSET_NEW - FILE_OFFSET
						image_data[FILE_OFFSET: FILE_OFFSET + MAX_FILE_SIZE] = patch_data + bytes(MAX_FILE_SIZE - FILE_SIZE)
						pathout_data[FILE_INFO - 4: FILE_INFO] = pack("<I", FILE_SIZE)
						print("patched " + relpath(file_name, patchout))
					except FileNotFoundError:
						pass
					except Exception as e:
						error_message(type(e).__name__ + " while patching " + file_name + ": " + str(e))
				FILE_OFFSET = FILE_OFFSET_NEW
				DECODED_NAME = DECODED_NAME_NEW
		
		if data != None:
			data += bytes(UNCOMPRESSED_DATA_SIZE - len(data))
			if COMPRESSION_FLAGS & 2 != 0: # Compressed files
				blue_print("Compressing...")
				compressed_data = compress(data, 9)
				pathout_data[rsgp_OFFSET + DATA_OFFSET: rsgp_OFFSET + DATA_OFFSET + COMPRESSED_DATA_SIZE] = compressed_data + bytes(COMPRESSED_DATA_SIZE - len(compressed_data))
			else: # Uncompressed files
				pathout_data[rsgp_OFFSET + DATA_OFFSET: rsgp_OFFSET + DATA_OFFSET + COMPRESSED_DATA_SIZE] = data
			
			if level < 5:
				print("patched " + relpath(osjoin(patch, rsgp_NAME + ".section"), patchout))
			
		if image_data != None:
			data += bytes(UNCOMPRESSED_IMAGE_DATA_SIZE - len(data))
			if COMPRESSION_FLAGS & 1 != 0: # Compressed files
				blue_print("Compressing...")
				compressed_data = compress(data, 9)
				pathout_data[rsgp_OFFSET + DATA_OFFSET: rsgp_OFFSET + DATA_OFFSET + COMPRESSED_IMAGE_DATA_SIZE] = compressed_data + bytes(COMPRESSED_IMAGE_DATA_SIZE - len(compressed_data))
			else: # Uncompressed files
				pathout_data[rsgp_OFFSET + DATA_OFFSET: rsgp_OFFSET + DATA_OFFSET + COMPRESSED_IMAGE_DATA_SIZE] = data
			
			if level < 5:
				print("patched " + relpath(osjoin(patch, rsgp_NAME + ".section2"), patchout))
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
				UNCOMPRESSED_SIZE = unpack("<I", file.read(4))[0]
				blue_print("Decompressing...")
				pathout_data = decompress(file.read())
				file = BytesIO(pathout_data)
				file.name = inp
				HEADER = file.read(4)

			if HEADER == b"1bsr":
				if not COMPRESSED:
					pathout_data = HEADER + file.read()
				
				if level < 3:
					out += ".smf"
				else:
					blue_print("Preparing...")
					pathout_data = bytearray(pathout_data)
					
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

					blue_print("Indexing...")
					TEXTURE_FORMATS = []
					file.seek(DIRECTORY_6_OFFSET)
					for IMAGE_ID in range(0, DIRECTORY_6_ENTRIES):
						WIDHT = unpack("<I", file.read(4))[0]
						HEIGHT = unpack("<I", file.read(4))[0]
						WIDHT_BYTES = unpack("<I", file.read(4))[0]
						TEXTURE_FORMAT = unpack("<I", file.read(4))[0]
						if DIRECTORY_6_ENTRY_SIZE == 24:
							COMPRESSED_IMAGE_SIZE = unpack("<I", file.read(4))[0]
							HUNDRED = unpack("<I", file.read(4))[0]

						TEXTURE_FORMATS.append(TEXTURE_FORMAT)
					
					file.seek(DIRECTORY_4_OFFSET)
					for i in range(0, DIRECTORY_4_ENTRIES):
						FILE_NAME = file.read(128).strip(b"\x00").decode()
						FILE_NAME_TESTS = FILE_NAME.lower()
						FILE_OFFSET = unpack("<I", file.read(4))[0]
						FILE_SIZE = unpack("<I", file.read(4))[0]
						
						RSGP_ID = unpack("<I", file.read(4))[0]

						COMPRESSION_FLAGS = unpack("<I", file.read(4))[0]
						HEADER_PADDING = unpack("<I", file.read(4))[0]
						DATA_OFFSET = unpack("<I", file.read(4))[0]

						DATA_PADDING = unpack("<I", file.read(4))[0]
						COMPRESSED_DATA_SIZE = unpack("<I", file.read(4))[0]
						DECOMPRESSED_DATA_SIZE = unpack("<I", file.read(4))[0]
						
						IMAGE_PADDING = unpack("<I", file.read(4))[0]
						COMPRESSED_IMAGE_SIZE = unpack("<I", file.read(4))[0]
						DECOMPRESSED_IMAGE_SIZE = unpack("<I", file.read(4))[0]

						file.seek(20, 1)
						IMAGE_ENTRIES = unpack("<I", file.read(4))[0] # Image layer?
						IMAGE_ID = unpack("<I", file.read(4))[0]
						if FILE_NAME_TESTS.startswith(rsgpStartsWith) and FILE_NAME_TESTS.endswith(rsgpEndsWith):
							temp = file.tell()
							file.seek(FILE_OFFSET)
							try:
								if level < 4:
									file_path = osjoin(patch, FILE_NAME + ".rsgp")
									patch_data = open(file_path, "rb").read()
									pathout_data[FILE_OFFSET: FILE_OFFSET + FILE_SIZE] = patch_data + bytes(FILE_SIZE - len(patch_data))
									print("applied " + relpath(file_path, patchout))
								else:
									pathout_data = rsgp_patch_data(FILE_NAME, FILE_OFFSET, file, pathout_data, patch, patchout, level)
							except FileNotFoundError:
								pass
							except Exception as e:
								error_message(type(e).__name__ + " while patching " + relpath(file_path, patchout) + ".rsgp: " + str(e))
							file.seek(temp)
				if level < 3 or COMPRESSED:
					tag, extension = splitext(out)
					tag += ".tag" + extension
					open(tag, "wb").write(md5(pathout_data).hexdigest().upper().encode() + b"\r\n")
					green_print("wrote " + relpath(tag, pathout))
					blue_print("Compressing...")
					pathout_data = b"\xD4\xFE\xAD\xDE" + pack("<I", len(pathout_data)) + compress(pathout_data, level = 9)
				
				open(out, "wb").write(pathout_data)
				green_print("wrote " + relpath(out, pathout))
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
				open(out,"wb").write(b'\x10\x00' + rijndael_cbc.encrypt(b"RTON" + file.read()))
				print("wrote " + relpath(out, pathout))
		except Exception as e:
			error_message(type(e).__name__ + " in " + inp + ": " + str(e))
	elif isdir(inp):
		makedirs(out, exist_ok = True)
		for entry in listdir(inp):
			input_file = osjoin(inp, entry)
			if isfile(input_file) or input_file != pathout:
				conversion(input_file, osjoin(out, entry), pathout, level, extension)
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
	
	print("\033[95m\033[1mOBBUnpatcher v1.1.5\n(C) 2022 by Nineteendo, Luigi Auriemma, Small Pea, 1Zulu & h3x4n1um\033[0m\n")
	try:
		folder = osjoin(application_path, "options")
		templates = list(filter(lambda entry: isfile(osjoin(folder, entry)) and entry[-5:] == ".json", sorted(listdir(folder))))
		length = len(templates)
		if length == 0:
			green_print("Loaded default template")
		else:
			blue_print("\033[1mTEMPLATES:\033[0m")
			for index in range(length):
				blue_print("\033[1m" + repr(index) + "\033[0m: "  + templates[index][:-5].strip())
			
			if length == 1:
				newoptions = load(open(osjoin(folder, templates[0]), "rb"))
			else:
				newoptions = load(open(osjoin(folder, templates[int(bold_input("Choose template"))]), "rb"))
			
			for key in options:
				if key in newoptions and newoptions[key] != options[key]:
					if type(options[key]) == type(newoptions[key]):
						options[key] = newoptions[key]
					elif isinstance(options[key], tuple) and isinstance(newoptions[key], list):
						options[key] = tuple([str(i).lower() for i in newoptions[key]])
					elif key == "indent" and newoptions[key] == None:
						options[key] = newoptions[key]
			
			green_print("Loaded template")
	except Exception as e:
		error_message(type(e).__name__ + " while loading options: " + str(e))
		warning_message("Falling back to default options.")
	
	if options["encodedUnpackLevel"] < 1:
		options["encodedUnpackLevel"] = input_level("ENCODED Unpack Level", 6, 7)
	if options["rsbUnpackLevel"] < 1:
		options["rsbUnpackLevel"] = input_level("OBB/RSB/SMF Unpack Level", 2, 3)
	if options["smfUnpackLevel"] < 1:
		options["smfUnpackLevel"] = input_level("SMF Unpack Level", 1, 2)
	
	if options["rsgpStartsWithIgnore"]:
		rsgpStartsWith = ""
	else:
		rsgpStartsWith = options["rsgpStartsWith"]	
	if options["rsgpEndsWithIgnore"]:
		rsgpEndsWith = ""
	else:
		rsgpEndsWith = options["rsgpEndsWith"]
	
	rijndael_cbc = RijndaelCBC(str.encode(options["encryptionKey"]), 24)
	if options["endsWithIgnore"]:
		endsWith = ""
	else:
		endsWith = options["endsWith"]
	if options["startsWithIgnore"]:
		startsWith = ""
	else:
		startsWith = options["startsWith"]
	RTONNoExtensions = options["RTONNoExtensions"]
	parse_json = JSONDecoder().parse_json

	level_to_name = ["SPECIFY", "SMF", "RSB", "RSGP", "SECTION", "ENCRYPTED", "ENCODED", "DECODED (beta)"]

	blue_print("Working directory: " + getcwd())
	if 7 >= options["encodedUnpackLevel"] > 6:
		encoded_input = path_input("ENCODED " + level_to_name[options["encodedUnpackLevel"]] + " Input file or directory")
		if isfile(encoded_input):
			encoded_output = path_input("ENCODED Output file").removesuffix(".json")
		else:
			encoded_output = path_input("ENCODED Output directory")
	if 6 >= options["encryptedUnpackLevel"] > 5:
		encrypted_input = path_input("ENCRYPTED " + level_to_name[options["encryptedUnpackLevel"]] + " Input file or directory")
		if isfile(encrypted_input):
			encrypted_output = path_input("ENCRYPTED Output file").removesuffix(".json")
		else:
			encrypted_output = path_input("ENCRYPTED Output directory")
	if 7 >= options["rsbUnpackLevel"] > 2:
		rsb_input = path_input("OBB/RSB/SMF Input file or directory")
		if isfile(rsb_input):
			rsb_output = path_input("OBB/RSB/SMF Modded file")
		else:
			rsb_output = path_input("OBB/RSB/SMF Modded directory")
		rsb_patch = path_input("OBB/RSB/SMF " + level_to_name[options["rsbUnpackLevel"]] + " Patch directory")
	
	if 2 >= options["smfUnpackLevel"] > 1:
		smf_input = path_input("SMF " + level_to_name[options["smfUnpackLevel"]] + " Input file or directory")
		if isfile(smf_input):
			smf_output = path_input("SMF Output file")
		else:
			smf_output = path_input("SMF Output directory")

	# Start file_to_folder
	start_time = datetime.datetime.now()
	if 7 >= options["encodedUnpackLevel"] > 6:
		conversion(encoded_input, encoded_output, dirname(encoded_output), options["encodedUnpackLevel"], ".json")
	if 6 >= options["encryptedUnpackLevel"] > 5:
		conversion(encrypted_input, encrypted_output, dirname(encrypted_output), options["encryptedUnpackLevel"], ".rton")
	if 7 >= options["rsbUnpackLevel"] > 2:
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