# Import libraries
import sys, datetime
from traceback import format_exc
from json import load
from struct import pack, unpack
from zlib import compress, decompress
from os import makedirs, listdir, system, getcwd, sep
from os.path import isdir, isfile, realpath, join as osjoin, dirname, relpath, splitext

# Default options
options = {
	"confirmPath": True, 
	"DEBUG_MODE": True,
	"endswith": (
		".rton",
	),
	"endswithIgnore": False,
	"enteredPath": False,
	"rsbExtensions": (
		".1bsr",
		".rsb1",
		".bsr",
		".rsb",
		".rsb.smf",
		".obb"
	),
	"rsbUnpackLevel": 4,
	"rsgpExtensions": (
		".pgsr",
		".rsgp"
	),
	"rsgpEndswith": (),
	"rsgpEndswithIgnore": True,
	"rsgpStartswith": (
		"packages",
		"worldpackages_"
	),
	"rsgpStartswithIgnore": False,
	"rsgpUnpackLevel": 2,
	"startswith": (
		"packages/",
	),
	"startswithIgnore": False
}

# Print & log error
def error_message(string):
	if DEBUG_MODE:
		string += "\n" + format_exc()
	
	fail.write(string + "\n")
	fail.flush()
	print("\033[91m%s\033[0m" % string)

# Print & log warning
def warning_message(string):
	fail.write("\t" + string + "\n")
	fail.flush()
	print("\33[93m%s\33[0m" % string)

# Print in blue text
def blue_print(text):
	print("\033[94m%s\033[0m" % text)

# Print in green text
def green_print(text):
	print("\033[32m%s\033[0m" % text)

# Input in bold text
def bold_input(text):
	return input("\033[1m%s\033[0m: " % text)

# Input hybrid path
def path_input(text):
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

# Set input level for conversion
def input_level(text, minimum, maximum):
	try:
		return max(minimum, min(maximum, int(bold_input(text + "(%s-%s)" % (minimum, maximum)))))
	except Exception as e:
		error_message("%s: %s" % (type(e).__name__, e))
		warning_message("Defaulting to %s" % minimum)
		return minimum

# Get cached file name
def GET_NAME(file, OFFSET, NAME_DICT):
	NAME = b""
	temp = file.tell()
	for key in list(NAME_DICT.keys()):
		if NAME_DICT[key] + OFFSET < temp:
			NAME_DICT.pop(key)
		else:
			NAME = key
	
	BYTE = b""
	while BYTE != b"\x00":
		NAME += BYTE
		BYTE = file.read(1)
		LENGTH = 4 * unpack("<I", file.read(3) + b"\x00")[0]
		if LENGTH != 0:
			NAME_DICT[NAME] = LENGTH
	
	return (NAME, NAME_DICT)

# Patch RGSP file
def rsgp_patch_data(rsgp_NAME, rsgp_OFFSET, file, pathout_data, patch, patchout, level):
	if file.read(4) == b"pgsr":
		data = None
		if level < 4:
			file_name = osjoin(patch, rsgp_NAME + ".section")
			try:
				data = open(file_name, "rb").read()
			except Exception:
				pass
		else:
			try:
				VER = unpack("<I", file.read(4))[0]
				
				file.seek(8, 1)
				TYPE = unpack("<I", file.read(4))[0]
				rsgp_BASE = unpack("<I", file.read(4))[0]
				
				data = None
				OFFSET = unpack("<I", file.read(4))[0]
				ZSIZE = unpack("<I", file.read(4))[0]
				SIZE = unpack("<I", file.read(4))[0]
				if SIZE != 0:
					file.seek(rsgp_OFFSET + OFFSET)
					if TYPE == 0: # Encrypted files
						# Insert decryption here
						data = bytearray(file.read(ZSIZE))
					elif TYPE == 1: # Uncompressed files
						data = bytearray(file.read(ZSIZE))
					elif TYPE == 3: # Compressed files
						blue_print("Decompressing ...")
						data = bytearray(decompress(file.read(ZSIZE)))
					else: # Unknown files
						raise TypeError(TYPE)
				else:
					file.seek(4, 1)
					OFFSET = unpack("<I", file.read(4))[0]
					ZSIZE = unpack("<I", file.read(4))[0]
					SIZE = unpack("<I", file.read(4))[0]
					if SIZE != 0:
						if TYPE == 0: # Encrypted files
							# Insert decryption here
							data = bytearray(file.read(ZSIZE))
						elif TYPE == 1: # Compressed files
							file.seek(rsgp_OFFSET + OFFSET)
							blue_print("Decompressing ...")
							data = bytearray(decompress(file.read(ZSIZE)))
						elif TYPE == 3: # Compressed files
							file.seek(rsgp_OFFSET + OFFSET)
							blue_print("Decompressing ...")
							data = bytearray(decompress(file.read(ZSIZE)))
						else: # Unknown files
							raise TypeError(TYPE)

				file.seek(rsgp_OFFSET + 72)
				INFO_SIZE = unpack("<I", file.read(4))[0]
				INFO_OFFSET = rsgp_OFFSET + unpack("<I", file.read(4))[0]
				INFO_LIMIT = INFO_OFFSET + INFO_SIZE
				
				file.seek(INFO_OFFSET)
				TMP = file.tell()
				DECODED_NAME = None
				NAME_DICT = {}
				FILE_DICT = {}
				while DECODED_NAME != "":
					FILE_NAME, NAME_DICT = GET_NAME(file, TMP, NAME_DICT)
					DECODED_NAME = FILE_NAME.decode().replace("\\", sep)
					if DECODED_NAME:
						ENCODED = unpack("<I", file.read(4))[0]
						FILE_OFFSET = unpack("<I", file.read(4))[0]
						FILE_SIZE = unpack("<I", file.read(4))[0]
						FILE_DICT[DECODED_NAME] = {
							"FILE_INFO": file.tell(),
							"FILE_OFFSET": FILE_OFFSET
						}
						if ENCODED != 0:
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
						file_name = osjoin(patch, DECODED_NAME)
						try:
							patch_data = open(file_name, "rb").read()
						except Exception:
							pass
						else:
							try:
								FILE_INFO = FILE_DICT[DECODED_NAME]["FILE_INFO"]
								FILE_SIZE = len(patch_data)
								MAX_FILE_SIZE = FILE_OFFSET_NEW - FILE_OFFSET
								data[FILE_OFFSET: FILE_OFFSET + MAX_FILE_SIZE] = patch_data + bytes(MAX_FILE_SIZE - FILE_SIZE)
								pathout_data[FILE_INFO - 4: FILE_INFO] = pack("<I", FILE_SIZE)
								print("patched " + relpath(file_name, patchout))
							except Exception as e:
								error_message("%s while patching %s: %s" % (type(e).__name__, file_name, e))
					
					FILE_OFFSET = FILE_OFFSET_NEW
					DECODED_NAME = DECODED_NAME_NEW
			except Exception as e:
				error_message("%s while patching %s.rsgrp: %s" % (type(e).__name__, rsgp_NAME, e))
		
		if data != None:
			try:
				file.seek(rsgp_OFFSET + 16)
				TYPE = unpack("<I", file.read(4))[0]
				rsgp_BASE = unpack("<I", file.read(4))[0]
				
				OFFSET = unpack("<I", file.read(4))[0]
				ZSIZE = unpack("<I", file.read(4))[0]
				SIZE = unpack("<I", file.read(4))[0]
				if SIZE != 0:
					data += bytes(SIZE - len(data))
					if TYPE == 0: # Encypted files
						# Insert encyption here
						pathout_data[rsgp_OFFSET + OFFSET: rsgp_OFFSET + OFFSET + ZSIZE] = data
					elif TYPE == 1: # Uncompressed files
						pathout_data[rsgp_OFFSET + OFFSET: rsgp_OFFSET + OFFSET + ZSIZE] = data
					elif TYPE == 3: # Compressed files
						blue_print("Compressing ...")
						compressed_data = compress(data, 9)
						pathout_data[rsgp_OFFSET + OFFSET: rsgp_OFFSET + OFFSET + ZSIZE] = compressed_data + bytes(ZSIZE - len(compressed_data))
					else: # Unknown files
						raise TypeError(TYPE)
				else:
					file.seek(4, 1)
					OFFSET = unpack("<I", file.read(4))[0]
					ZSIZE = unpack("<I", file.read(4))[0]
					SIZE = unpack("<I", file.read(4))[0]
					if SIZE != 0:
						if TYPE == 0: # Encypted files
							# Insert encyption here
							pathout_data[rsgp_OFFSET + OFFSET: rsgp_OFFSET + OFFSET + ZSIZE] = data
						elif TYPE == 1: # Compressed files
							data += bytes(SIZE - len(data))
							blue_print("Compressing ...")
							compressed_data = compress(data, 9)
							pathout_data[rsgp_OFFSET + OFFSET: rsgp_OFFSET + OFFSET + ZSIZE] = compressed_data + bytes(ZSIZE - len(compressed_data))
						elif TYPE == 3: # Compressed files
							data += bytes(SIZE - len(data))
							blue_print("Compressing ...")
							compressed_data = compress(data, 9)
							pathout_data[rsgp_OFFSET + OFFSET: rsgp_OFFSET + OFFSET + ZSIZE] = compressed_data + bytes(ZSIZE - len(compressed_data))
						else: # Unknown files
							raise TypeError(TYPE)

				if level < 3:
					print("patched " + relpath(osjoin(patch, rsgp_NAME + ".section"), patchout))
			except Exception as e:
				error_message("%s while patching %s.rsgp: %s" % (type(e).__name__, rsgp_NAME, e))
			
	return pathout_data

# Recursive file convert function
def file_to_folder(inp, out, patch, level, extensions, pathout, patchout):
	if isdir(inp) and inp != pathout and inp != patchout:
		makedirs(out, exist_ok = True)
		makedirs(patch, exist_ok = True)
		for entry in sorted(listdir(inp)):
			input_file = osjoin(inp, entry)
			output_file = osjoin(out, entry)
			patch_file = osjoin(patch, entry)
			if isfile(input_file):
				patch_file = splitext(patch_file)[0]
			
			file_to_folder(input_file, output_file, patch_file, level, extensions, pathout, patchout)
	elif isfile(inp) and inp.lower().endswith(extensions):
		try:
			file = open(inp, "rb")
			blue_print("Preparing ...")
			pathout_data = bytearray(file.read())
			file.seek(0)
			SIGN = file.read(4)
			if SIGN == b"1bsr":
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
						if level < 3:
							file_path = osjoin(patch, FILE_NAME + ".rsgp")
							try:
								patch_data = open(file_path, "rb").read()
							except Exception:
								pass
							else:
								try:
									pathout_data[FILE_OFFSET: FILE_OFFSET + FILE_SIZE] = patch_data + bytes(FILE_SIZE - len(patch_data))
									print("applied " + relpath(file_path, patchout))
								except Exception as e:
									error_message("%s while patching %s: %s" % (type(e).__name__, relpath(file_path, patchout), e))
						else:
							pathout_data = rsgp_patch_data(FILE_NAME, FILE_OFFSET, file, pathout_data, patch, patchout, level)
						
						file.seek(temp)
				open(out, "wb").write(pathout_data)
				print("patched " + relpath(out, pathout))
			elif SIGN == b"pgsr":
				file.seek(0)
				pathout_data = rsgp_patch_data("data", 0, file, pathout_data, patch, patchout, level)
				open(out, "wb").write(pathout_data)
				print("patched " + relpath(out, pathout))

		except Exception as e:
			error_message("Failed OBBUnpatch: %s in %s pos %s: %s" % (type(e).__name__, inp, file.tell() - 1, e))

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
	
	print("\033[95m\033[1mOBBUnpatcher v1.1.0\n(C) 2022 by Luigi Auriemma & Nineteendo\033[0m\n")
	try:
		newoptions = load(open(osjoin(application_path, "options.json"), "rb"))
		for key in options:
			if key in newoptions and newoptions[key] != options[key]:
				if type(options[key]) == type(newoptions[key]):
					options[key] = newoptions[key]
				elif isinstance(options[key], tuple) and isinstance(newoptions[key], list):
					options[key] = tuple([str(i).lower() for i in newoptions[key]])
	except Exception as e:
		error_message("%s in options.json: %s" % (type(e).__name__, e))
	
	if options["rsgpUnpackLevel"] < 1:
		options["rsgpUnpackLevel"] = input_level("PGSR/RSGP Unpack Level", 2, 4)
	
	if options["rsbUnpackLevel"] < 1:
		options["rsbUnpackLevel"] = input_level("OBB/RSB Unpack Level", 1, 4)

	DEBUG_MODE = options["DEBUG_MODE"]
	if options["endswithIgnore"]:
		endswith = ""
	else:
		endswith = options["endswith"]
	
	if options["rsgpStartswithIgnore"]:
		rsgpStartswith = ""
	else:
		rsgpStartswith = options["rsgpStartswith"]
	
	if options["rsgpEndswithIgnore"]:
		rsgpEndswith = ""
	else:
		rsgpEndswith = options["rsgpEndswith"]

	if options["startswithIgnore"]:
		startswith = ""
	else:
		startswith = options["startswith"]

	blue_print("Working directory: " + getcwd())
	level_to_name = ["SPECIFY", "OBB/RSB", "PGSR/RSGP", "SECTION", "ENCODED"]
	if 5 > options["rsgpUnpackLevel"] > 2:
		rsgp_input = path_input("PGSR/RSGP Input file or directory")
		if isfile(rsgp_input):
			rsgp_output = path_input("PGSR/RSGP Modded file")
		else:
			rsgp_output = path_input("PGSR/RSGP Modded directory")
		
		rsgp_patch = path_input("PGSR/RSGP %s Patch directory" % level_to_name[options["rsgpUnpackLevel"]])

	if 5 > options["rsbUnpackLevel"] > 1:
		rsb_input = path_input("OBB/RSB Input file or directory")
		if isfile(rsb_input):
			rsb_output = path_input("OBB/RSB Modded file")
		else:
			rsb_output = path_input("OBB/RSB Modded directory")
		
		rsb_patch = path_input("OBB/RSB %s Patch directory" % level_to_name[options["rsbUnpackLevel"]])

	# Start file_to_folder
	start_time = datetime.datetime.now()
	if 5 > options["rsgpUnpackLevel"] > 2:
		file_to_folder(rsgp_input, rsgp_output, rsgp_patch, options["rsgpUnpackLevel"], options["rsgpExtensions"], dirname(rsgp_output), rsgp_patch)
	
	if 5 > options["rsbUnpackLevel"] > 1:
		file_to_folder(rsb_input, rsb_output, rsb_patch, options["rsbUnpackLevel"], options["rsbExtensions"], dirname(rsb_output), rsb_patch)

	green_print("finished patching in %s" % (datetime.datetime.now() - start_time))
	bold_input("\033[95mPRESS [ENTER]")
except BaseException as e:
	error_message("%s: %s" % (type(e).__name__, e))

# Close log
fail.close()