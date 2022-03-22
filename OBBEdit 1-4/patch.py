# Import libraries
import sys, datetime
from traceback import format_exc
from json import load
from struct import pack, unpack
from zlib import compress, decompress
from os import makedirs, listdir, system, getcwd, sep
from os.path import isdir, isfile, realpath, join as osjoin, dirname, relpath, basename, splitext

options = {
# Default options
	# Universal options
	"confirmPath": True,
	"DEBUG_MODE": True,
	"enteredPath": False,
	# RSB options
	"rsbExtensions": (
		".1bsr",
		".rsb1",
		".bsr",
		".rsb",
		".rsb.smf",
		".obb"
	),
	"rsbUnpackLevel": 4,
	"rsgpEndswith": (),
	"rsgpEndswithIgnore": True,
	"rsgpStartswith": (
		"packages",
		"worldpackages_"
	),
	"rsgpStartswithIgnore": False,
	# RSGP options
	"endswith": (
		".rton",
	),
	"endswithIgnore": False,
	"rsgpExtensions": (
		".pgsr",
		".rsgp"
	),
	"rsgpUnpackLevel": 2,
	"startswith": (
		"packages/",
	),
	"startswithIgnore": False,
	# RTON options
	"comma": 0,
	"doublepoint": 1,
	"encodedUnpackLevel": 4,
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
	if options["DEBUG_MODE"]:
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
		if options["enteredPath"]:
			string = newstring
		else:
			string = ""
			quoted = 0
			escaped = False
			tempstring = ""
			for char in newstring:
				if escaped:
					if quoted != 1 and char == "'" or quoted != 2 and char == '"' or quoted == 0 and char in "\\ ":
						string += tempstring + char
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
			if options["confirmPath"]:
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
		data = None
		if level < 4:
			try:
				data = open(osjoin(patch, rsgp_NAME + ".section"), "rb").read()
			except FileNotFoundError:
				pass
		else:
			rsgp_VERSION = unpack("<I", file.read(4))[0]
			
			file.seek(8, 1)
			rsgp_TYPE = unpack("<I", file.read(4))[0]
			rsgp_BASE = unpack("<I", file.read(4))[0]
			
			data = None
			DATA_OFFSET = unpack("<I", file.read(4))[0]
			COMPRESSED_SIZE = unpack("<I", file.read(4))[0]
			UNCOMPRESSED_SIZE = unpack("<I", file.read(4))[0]
			if UNCOMPRESSED_SIZE != 0:
				file.seek(rsgp_OFFSET + DATA_OFFSET)
				if rsgp_TYPE == 0: # Encrypted files
					# Insert decryption here
					data = bytearray(file.read(COMPRESSED_SIZE))
				elif rsgp_TYPE == 1: # Uncompressed files
					data = bytearray(file.read(COMPRESSED_SIZE))
				elif rsgp_TYPE == 3: # Compressed files
					blue_print("Decompressing ...")
					data = bytearray(decompress(file.read(COMPRESSED_SIZE)))
				else: # Unknown files
					raise TypeError(TYPE)
			else:
				file.seek(4, 1)
				DATA_OFFSET = unpack("<I", file.read(4))[0]
				COMPRESSED_SIZE = unpack("<I", file.read(4))[0]
				UNCOMPRESSED_SIZE = unpack("<I", file.read(4))[0]
				if UNCOMPRESSED_SIZE != 0:
					if rsgp_TYPE == 0: # Encrypted files
						# Insert decryption here
						data = bytearray(file.read(COMPRESSED_SIZE))
					elif rsgp_TYPE == 1: # Compressed files
						file.seek(rsgp_OFFSET + DATA_OFFSET)
						blue_print("Decompressing ...")
						data = bytearray(decompress(file.read(COMPRESSED_SIZE)))
					elif rsgp_TYPE == 3: # Compressed files
						file.seek(rsgp_OFFSET + DATA_OFFSET)
						blue_print("Decompressing ...")
						data = bytearray(decompress(file.read(COMPRESSED_SIZE)))
					else: # Unknown files
						raise TypeError(TYPE)
			file.seek(rsgp_OFFSET + 72)
			INFO_SIZE = unpack("<I", file.read(4))[0]
			INFO_OFFSET = rsgp_OFFSET + unpack("<I", file.read(4))[0]
			INFO_LIMIT = INFO_OFFSET + INFO_SIZE
			
			file.seek(INFO_OFFSET)
			DECODED_NAME = None
			NAME_DICT = {}
			FILE_DICT = {}
			while DECODED_NAME != "":
				FILE_NAME = b""
				temp = file.tell()
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
				if DECODED_NAME:
					PTX = unpack("<I", file.read(4))[0] != 0
					FILE_OFFSET = unpack("<I", file.read(4))[0]
					FILE_SIZE = unpack("<I", file.read(4))[0]
					FILE_DICT[DECODED_NAME] = {
						"FILE_INFO": file.tell(),
						"FILE_OFFSET": FILE_OFFSET
					}
					if PTX != 0:
						file.seek(20, 1)
				else:
					FILE_DICT[""] = {
						"FILE_OFFSET": SIZE
					}
			DECODED_NAME = ""
			for DECODED_NAME_NEW in sorted(FILE_DICT, key = lambda key: FILE_DICT[key]["FILE_OFFSET"]):
				FILE_OFFSET_NEW = FILE_DICT[DECODED_NAME_NEW]["FILE_OFFSET"]
				NAME_CHECK = DECODED_NAME.replace("\\", "/").lower()
				if DECODED_NAME and NAME_CHECK.startswith(startswith) and NAME_CHECK.endswith(endswith):
					if level < 5:
						try:
							file_name = osjoin(patch, DECODED_NAME)
							patch_data = open(file_name, "rb").read()
							FILE_INFO = FILE_DICT[DECODED_NAME]["FILE_INFO"]
							FILE_SIZE = len(patch_data)
							MAX_FILE_SIZE = FILE_OFFSET_NEW - FILE_OFFSET
							data[FILE_OFFSET: FILE_OFFSET + MAX_FILE_SIZE] = patch_data + bytes(MAX_FILE_SIZE - FILE_SIZE)
							pathout_data[FILE_INFO - 4: FILE_INFO] = pack("<I", FILE_SIZE)
							print("patched " + relpath(file_name, patchout))
						except FileNotFoundError:
							pass
						except Exception as e:
							error_message(type(e).__name__ + " while patching " + file_name + ": " + str(e))
					elif NAME_CHECK[-5:] == ".rton":
						try:
							file_name = osjoin(patch, DECODED_NAME[:-5] + ".JSON")
							source = load(open(file_name, "rb"), object_pairs_hook = encode_object_pairs).data
							patch_data = parse_json(source)
							FILE_INFO = FILE_DICT[DECODED_NAME]["FILE_INFO"]
							FILE_SIZE = len(patch_data)
							MAX_FILE_SIZE = FILE_OFFSET_NEW - FILE_OFFSET
							data[FILE_OFFSET: FILE_OFFSET + MAX_FILE_SIZE] = patch_data + bytes(MAX_FILE_SIZE - FILE_SIZE)
							pathout_data[FILE_INFO - 4: FILE_INFO] = pack("<I", FILE_SIZE)
							print("patched " + relpath(file_name, patchout))
						except FileNotFoundError as e:
							pass
						except Exception as e:
							error_message(type(e).__name__ + " while patching " + file_name + ": " + str(e))
				FILE_OFFSET = FILE_OFFSET_NEW
				DECODED_NAME = DECODED_NAME_NEW
		if data != None:
			file.seek(rsgp_OFFSET + 16)
			TYPE = unpack("<I", file.read(4))[0]
			rsgp_BASE = unpack("<I", file.read(4))[0]
			
			DATA_OFFSET = unpack("<I", file.read(4))[0]
			COMPRESSED_SIZE = unpack("<I", file.read(4))[0]
			UNCOMPRESSED_SIZE = unpack("<I", file.read(4))[0]
			if UNCOMPRESSED_SIZE != 0:
				data += bytes(UNCOMPRESSED_SIZE - len(data))
				if TYPE == 0: # Encypted files
					# Insert encyption here
					pathout_data[rsgp_OFFSET + DATA_OFFSET: rsgp_OFFSET + DATA_OFFSET + COMPRESSED_SIZE] = data
				elif TYPE == 1: # Uncompressed files
					pathout_data[rsgp_OFFSET + DATA_OFFSET: rsgp_OFFSET + DATA_OFFSET + COMPRESSED_SIZE] = data
				elif TYPE == 3: # Compressed files
					blue_print("Compressing ...")
					compressed_data = compress(data, 9)
					pathout_data[rsgp_OFFSET + DATA_OFFSET: rsgp_OFFSET + DATA_OFFSET + COMPRESSED_SIZE] = compressed_data + bytes(COMPRESSED_SIZE - len(compressed_data))
				else: # Unknown files
					raise TypeError(TYPE)
			else:
				file.seek(4, 1)
				DATA_OFFSET = unpack("<I", file.read(4))[0]
				COMPRESSED_SIZE = unpack("<I", file.read(4))[0]
				UNCOMPRESSED_SIZE = unpack("<I", file.read(4))[0]
				if UNCOMPRESSED_SIZE != 0:
					if TYPE == 0: # Encypted files
						# Insert encyption here
						pathout_data[rsgp_OFFSET + DATA_OFFSET: rsgp_OFFSET + DATA_OFFSET + COMPRESSED_SIZE] = data
					elif TYPE == 1: # Compressed files
						data += bytes(UNCOMPRESSED_SIZE - len(data))
						blue_print("Compressing ...")
						compressed_data = compress(data, 9)
						pathout_data[rsgp_OFFSET + DATA_OFFSET: rsgp_OFFSET + DATA_OFFSET + COMPRESSED_SIZE] = compressed_data + bytes(COMPRESSED_SIZE - len(compressed_data))
					elif TYPE == 3: # Compressed files
						data += bytes(UNCOMPRESSED_SIZE - len(data))
						blue_print("Compressing ...")
						compressed_data = compress(data, 9)
						pathout_data[rsgp_OFFSET + DATA_OFFSET: rsgp_OFFSET + DATA_OFFSET + COMPRESSED_SIZE] = compressed_data + bytes(COMPRESSED_SIZE - len(compressed_data))
					else: # Unknown files
						raise TypeError(TYPE)
			if level < 3:
				print("patched " + relpath(osjoin(patch, rsgp_NAME + ".section"), patchout))
	return pathout_data
def file_to_folder(inp, out, patch, level, extensions, pathout, patchout):
# Recursive file convert function
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
	elif isfile(inp) and inp.lower().endswith(extensions):
		try:
			file = open(inp, "rb")
			blue_print("Preparing ...")
			pathout_data = bytearray(file.read())
			file.seek(0)
			HEADER = file.read(4)
			if HEADER == b"1bsr":
				file.seek(40)
				FILES = unpack("<I", file.read(4))[0]
				OFFSET = unpack("<I", file.read(4))[0]
				file.seek(OFFSET)
				for i in range(0, FILES):
					FILE_NAME = file.read(128).strip(b"\x00").decode()
					FILE_NAME_TESTS = FILE_NAME.lower()
					FILE_OFFSET = unpack("<I", file.read(4))[0]
					FILE_SIZE = unpack("<I", file.read(4))[0]
					
					file.seek(68, 1)
					if FILE_NAME_TESTS.startswith(rsgpStartswith) and FILE_NAME_TESTS.endswith(rsgpEndswith):
						temp = file.tell()
						file.seek(FILE_OFFSET)
						try:
							if level < 3:
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
				open(out, "wb").write(pathout_data)
				print("patched " + relpath(out, pathout))
			elif HEADER == b"pgsr":
				file.seek(0)
				try:
					pathout_data = rsgp_patch_data("data", 0, file, pathout_data, patch, patchout, level)
					open(out, "wb").write(pathout_data)
					print("patched " + relpath(out, pathout))
				except Exception as e:
					error_message(type(e).__name__ + " while patching " + relpath(file_path, patchout) + ".rsgp: " + str(e))
		except Exception as e:
			error_message("Failed OBBPatch " + type(e).__name__ + " in " + inp + " pos " + str(file.tell()) + ": " + str(e))
# JSON Encode functions
class list2:
# Extra list class
	def __init__(self, data):
		self.data = data
Infinity = [float("Infinity"), float("-Infinity")] # Inf and -inf values
def encode_bool(boolean):
# Boolian
	if boolean:
		return b"\x01"
	else:
		return b"\x00"
def encode_number(integ):
# Number with variable length
	integ, i = divmod(integ, 128)
	if (integ):
		i += 128
	string = pack("B", i)
	while integ:
		integ, i = divmod(integ, 128)
		if (integ):
			i += 128
		string += pack("B", i)
	return string
def encode_unicode(string):
# Unicode string
	encoded_string = string.encode()
	return encode_number(len(string)) + encode_number(len(encoded_string)) + encoded_string
def encode_rtid(string):
# RTID
	if "@" in string:
		name, type = string[5:-1].split("@")
		if name.count(".") == 2:
			i2, i1, i3 = name.split(".")
			return b"\x83\x02" + encode_unicode(type) + encode_number(int(i1)) + encode_number(int(i2)) + bytes.fromhex(i3)[::-1]
		else:
			return b"\x83\x03" + encode_unicode(type) + encode_unicode(name)
	else:
		return b"\x84"
def encode_int(integ):
# Number
	if integ == 0:
		return b"\x21"
	elif 0 <= integ <= 2097151:
		return b"\x24" + encode_number(integ)
	elif -1048576 <= integ <= 0:
		return b"\x25" + encode_number(-1 - 2 * integ)
	elif -2147483648 <= integ <= 2147483647:
		return b"\x20" + pack("<i", integ)
	elif 0 <= integ < 4294967295:
		return b"\x26" + pack("<I", integ)
	elif 0 <= integ <= 562949953421311:
		return b"\x44" + encode_number(integ)
	elif -281474976710656 <= integ <= 0:
		return b"\x45" + encode_number(-1 - 2 * integ)
	elif -9223372036854775808 <= integ <= 9223372036854775807:
		return b"\x40" + pack("<q", integ)
	elif 0 <= integ <= 18446744073709551615:
		return b"\x46" + pack("<Q", integ)
	elif 0 <= integ:
		return b"\x44" + encode_number(integ)
	else:
		return b"\x45" + encode_number(-1 - 2 * integ)
def encode_float(dec):
# Float
	if dec == 0:
		return b"\x23"
	elif dec != dec or dec in Infinity or -340282346638528859811704183484516925440 <= dec <= 340282346638528859811704183484516925440 and dec == unpack("<f", pack("<f", dec))[0]:
		return b"\x22" + pack("<f", dec)
	else:
		return b"\x42" + pack("<d", dec)
def encode_string(string, cached_strings):
# String
	if string in cached_strings:
		data = b"\x91" + encode_number(cached_strings[string])
	else:
		cached_strings[string] = len(cached_strings)
		encoded_string = string.encode()
		data = b"\x90" + encode_number(len(encoded_string)) + encoded_string
	return (data, cached_strings)
def parse_array(data, cached_strings):
# Array
	string = encode_number(len(data))
	for v in data:
		v, cached_strings = parse_data(v, cached_strings)
		string += v
	return (b"\x86\xfd" + string + b"\xfe", cached_strings)
def parse_object(data, cached_strings):
# Object
	string = b"\x85"
	for key, value in data:
		key, cached_strings = encode_string(key, cached_strings)
		value, cached_strings = parse_data(value, cached_strings)
		string += key + value
	return (string + b"\xff", cached_strings)
def parse_json(data):
# JSON -> RTON
	cached_strings = {}
	string = b"RTON\x01\x00\x00\x00"
	for key, value in data:
		key, cached_strings = encode_string(key, cached_strings)
		value, cached_strings = parse_data(value, cached_strings)
		string += key + value
	return string + b"\xffDONE"
def parse_data(data, cached_strings):
# Data
	if isinstance(data, str):
		if "RTID()" == data[:5] + data[-1:]:
			return (encode_rtid(data), cached_strings)
		else:
			return encode_string(data, cached_strings)
	elif isinstance(data, bool):
		return (encode_bool(data), cached_strings)
	elif isinstance(data, int):
		return (encode_int(data), cached_strings)
	elif isinstance(data, float):
		return (encode_float(data), cached_strings)
	elif isinstance(data, list):
		return parse_array(data, cached_strings)
	elif isinstance(data, list2):
		return parse_object(data.data, cached_strings)
	elif data == None:
		return (b"\x84", cached_strings)
	else:
		raise TypeError(type(data))
def conversion(inp, out, pathout):
# Convert file
	if isfile(inp) and inp.lower()[-5:] == ".json":
		write = out.removesuffix(".json")
		try:
			file = open(inp, "rb")
			if file.read(4) != b"RTON": # Ignore CDN files
				file.seek(0)
				data = load(file, object_pairs_hook = encode_object_pairs).data
				encoded_data = parse_json(data)
				# No extension
				if "" == splitext(write)[1] and not basename(write).lower().startswith(RTONNoExtensions):
					write += ".rton"
				open(write, "wb").write(encoded_data)
				print("wrote " + relpath(write, pathout))
		except Exception as e:
			error_message(type(e).__name__ + " in " + inp + ": " + str(e))
	elif isdir(inp):
		makedirs(out, exist_ok = True)
		for entry in listdir(inp):
			input_file = osjoin(inp, entry)
			if isfile(input_file) or input_file != pathout:
				conversion(input_file, osjoin(out, entry), pathout)
def encode_object_pairs(pairs):
# Object to list of tuples
	return list2(pairs)
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
	
	print("\033[95m\033[1mOBBUnpatcher v1.1.2\n(C) 2022 by Luigi Auriemma & Nineteendo\033[0m\n")
	try:
		newoptions = load(open(osjoin(application_path, "options.json"), "rb"))
		for key in options:
			if key in newoptions and newoptions[key] != options[key]:
				if type(options[key]) == type(newoptions[key]):
					options[key] = newoptions[key]
				elif isinstance(options[key], tuple) and isinstance(newoptions[key], list):
					options[key] = tuple([str(i).lower() for i in newoptions[key]])
				elif key == "indent" and newoptions[key] == None:
					options[key] = newoptions[key]
	except Exception as e:
		error_message(type(e).__name__ + " in options.json: " + str(e))
	
	if options["encodedUnpackLevel"] < 1:
		options["encodedUnpackLevel"] = input_level("ENCODED Unpack Level", 4, 5)
	if options["rsgpUnpackLevel"] < 1:
		options["rsgpUnpackLevel"] = input_level("PGSR/RSGP Unpack Level", 2, 4)
	if options["rsbUnpackLevel"] < 1:
		options["rsbUnpackLevel"] = input_level("OBB/RSB Unpack Level", 1, 4)
	
	if options["rsgpStartswithIgnore"]:
		rsgpStartswith = ""
	else:
		rsgpStartswith = options["rsgpStartswith"]	
	if options["rsgpEndswithIgnore"]:
		rsgpEndswith = ""
	else:
		rsgpEndswith = options["rsgpEndswith"]
	
	if options["endswithIgnore"]:
		endswith = ""
	else:
		endswith = options["endswith"]
	if options["startswithIgnore"]:
		startswith = ""
	else:
		startswith = options["startswith"]
	RTONNoExtensions = options["RTONNoExtensions"]

	level_to_name = ["SPECIFY", "OBB/RSB", "PGSR/RSGP", "SECTION", "ENCODED", "DECODED (beta)"]

	blue_print("Working directory: " + getcwd())
	if 6 > options["encodedUnpackLevel"] > 4:
		encoded_input = path_input("ENCODED " + level_to_name[options["encodedUnpackLevel"]] + "Input file or directory")
		if isfile(encoded_input):
			encoded_output = path_input("ENCODED Output file").removesuffix(".json")
		else:
			encoded_output = path_input("ENCODED Output directory")
	if 6 > options["rsgpUnpackLevel"] > 2:
		rsgp_input = path_input("PGSR/RSGP Input file or directory")
		if isfile(rsgp_input):
			rsgp_output = path_input("PGSR/RSGP Modded file")
		else:
			rsgp_output = path_input("PGSR/RSGP Modded directory")
		rsgp_patch = path_input("PGSR/RSGP " + level_to_name[options["rsgpUnpackLevel"]] + " Patch directory")
	if 6 > options["rsbUnpackLevel"] > 1:
		rsb_input = path_input("OBB/RSB Input file or directory")
		if isfile(rsb_input):
			rsb_output = path_input("OBB/RSB Modded file")
		else:
			rsb_output = path_input("OBB/RSB Modded directory")
		rsb_patch = path_input("OBB/RSB " + level_to_name[options["rsbUnpackLevel"]] + " Patch directory")

	# Start file_to_folder
	start_time = datetime.datetime.now()
	if 6 > options["encodedUnpackLevel"] > 4:
		conversion(encoded_input, encoded_output, dirname(encoded_output))
	if 6 > options["rsgpUnpackLevel"] > 2:
		file_to_folder(rsgp_input, rsgp_output, rsgp_patch, options["rsgpUnpackLevel"], options["rsgpExtensions"], dirname(rsgp_output), rsgp_patch)
	if 6 > options["rsbUnpackLevel"] > 1:
		file_to_folder(rsb_input, rsb_output, rsb_patch, options["rsbUnpackLevel"], options["rsbExtensions"], dirname(rsb_output), rsb_patch)

	green_print("finished patching in " + str(datetime.datetime.now() - start_time))
	if fail.tell() > 0:
		print("\33[93m" + "Errors occured, check: " + fail.name + "\33[0m")
	bold_input("\033[95mPRESS [ENTER]")
except Exception as e:
	error_message(type(e).__name__ + " : " + str(e))
except BaseException as e:
	warning_message(type(e).__name__ + " : " + str(e))
fail.close() # Close log