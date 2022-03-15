# Import libraries
from io import BytesIO
import sys, datetime
from traceback import format_exc
from json import load, dumps
from struct import unpack, error
from zlib import decompress
from os import makedirs, listdir, system, getcwd, sep
from os.path import isdir, isfile, realpath, join as osjoin, dirname, relpath, basename, splitext
#from PIL import Image
#COLORS = "RGBA"
#Alt for iPad: COLORS = "BGRA"

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
# RSGP Unpack functions
def GET_NAME(file, OFFSET, NAME_DICT):
# Get cached file name
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
def rsgp_extract(rsgp_NAME, rsgp_OFFSET, file, out, pathout, level):
# Extract data from RGSP file
	if file.read(4) == b"pgsr":
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
				if TYPE == 0: # Encypted files
					# Insert encyption here
					data = file.read(ZSIZE)
				elif TYPE == 1: # Uncompressed files
					data = file.read(ZSIZE)
				elif TYPE == 3: # Compressed files
					blue_print("Decompressing ...")
					data = decompress(file.read(ZSIZE))
				else: # Unknown files
					raise TypeError(TYPE)
			else:
				file.seek(4, 1)
				OFFSET = unpack("<I", file.read(4))[0]
				ZSIZE = unpack("<I", file.read(4))[0]
				SIZE = unpack("<I", file.read(4))[0]
				if SIZE != 0:
					file.seek(rsgp_OFFSET + OFFSET)
					if TYPE == 0: # Encypted files
						# Insert encyption here
						data = file.read(ZSIZE)
					elif TYPE == 1: # Compressed files
						blue_print("Decompressing ...")
						data = decompress(file.read(ZSIZE))
					elif TYPE == 3: # Compressed files
						blue_print("Decompressing ...")
						data = decompress(file.read(ZSIZE))
					else: # Unknown files
						raise TypeError(TYPE)
			if level < 4:
				file_path = osjoin(out, rsgp_NAME + ".section")
				makedirs(out, exist_ok = True)
				open(file_path, "wb").write(data)
				print("wrote " + relpath(file_path, pathout))
			else:
				file.seek(rsgp_OFFSET + 72)
				INFO_SIZE = unpack("<I", file.read(4))[0]
				INFO_OFFSET = rsgp_OFFSET + unpack("<I", file.read(4))[0]
				INFO_LIMIT = INFO_OFFSET + INFO_SIZE
				
				file.seek(INFO_OFFSET)
				TMP = file.tell()
				DECODED_NAME = None
				NAME_DICT = {}
				while DECODED_NAME != "":
					NAME, NAME_DICT = GET_NAME(file, TMP, NAME_DICT)
					DECODED_NAME = NAME.decode().replace("\\", sep)
					NAME_CHECK = DECODED_NAME.replace("\\", "/").lower()
					PTX = unpack("<I", file.read(4))[0]
					FILE_OFFSET = unpack("<I", file.read(4))[0]
					FILE_SIZE = unpack("<I", file.read(4))[0]
					if PTX:
						file.seek(20, 1)
						#A = unpack("<I", file.read(4))[0]
						#B = unpack("<I", file.read(4))[0]
						#C = unpack("<I", file.read(4))[0]
						#WIDHT = unpack("<I", file.read(4))[0]
						#HEIGHT = unpack("<I", file.read(4))[0]
					if DECODED_NAME and NAME_CHECK.startswith(startswith) and NAME_CHECK.endswith(endswith):
						if level < 5:
							file_path = osjoin(out, DECODED_NAME)
							makedirs(dirname(file_path), exist_ok = True)
							open(file_path, "wb").write(data[FILE_OFFSET: FILE_OFFSET + FILE_SIZE])
							print("wrote " + relpath(file_path, pathout))
						elif NAME_CHECK[-5:] == ".rton":
							try:
								jfn = osjoin(out, DECODED_NAME[:-5] + ".json")
								makedirs(dirname(jfn), exist_ok = True)
								source = BytesIO(data[FILE_OFFSET: FILE_OFFSET + FILE_SIZE])
								source.name = file.name + ": " + DECODED_NAME
								if source.read(4) == b"RTON":
									json_data = root_object(source, current_indent)
									open(jfn, "w", encoding = "utf-8").write(json_data)
									print("wrote " + relpath(jfn, pathout))
								else:
									warning_message("No RTON " + source.name)
							except Exception as e:
								error_message(type(e).__name__ + " in " + file.name + ": " + DECODED_NAME + " pos " + str(source.tell() - 1) + ": " + str(e))
						#elif PTX:
						#	if FILE_SIZE == 4 * WIDHT * HEIGHT:
						#		file_path = osjoin(out, splitext(DECODED_NAME)[0] + ".PNG")
						#		makedirs(dirname(file_path), exist_ok = True)
						#		blue_print("Decoding ...")
						#		Image.frombuffer("RGBA", (WIDHT, HEIGHT), data[FILE_OFFSET: FILE_OFFSET + FILE_SIZE], "raw", COLORS, 0, 1).save("/Users/wannes/Documents/GitHub/PVZ2tools/PTXTests/ALWAYSLOADED_384_00.PNG")
						#		print("wrote " + relpath(file_path, pathout))
		except Exception as e:
			error_message(type(e).__name__ + " while extracting " + rsgp_NAME + ".rsgp: " + str(e))
def file_to_folder(inp, out, level, extensions, pathout):
# Recursive file convert function
	if isdir(inp):
		makedirs(out, exist_ok = True)
		for entry in sorted(listdir(inp)):
			input_file = osjoin(inp, entry)
			output_file = osjoin(out, entry)
			if isfile(input_file):
				file_to_folder(input_file, splitext(output_file)[0], level, extensions, pathout)
			elif input_file != pathout:
				file_to_folder(input_file, output_file, level, extensions, pathout)
	elif isfile(inp) and inp.lower().endswith(extensions):
		try:
			file = open(inp, "rb")
			SIGN = file.read(4)
			if SIGN == b"1bsr":
				file.seek(40)
				FILES = unpack("<I", file.read(4))[0]
				OFFSET = unpack("<I", file.read(4))[0]
				file.seek(OFFSET)
				for i in range(0, FILES):
					FILE_NAME = file.read(128).strip(b"\x00").decode()
					FILE_CHECK = FILE_NAME.lower()
					FILE_OFFSET = unpack("<I", file.read(4))[0]
					FILE_SIZE = unpack("<I", file.read(4))[0]
					
					file.seek(68, 1)
					if FILE_CHECK.startswith(rsgpStartswith) and FILE_CHECK.endswith(rsgpEndswith):
						temp = file.tell()
						file.seek(FILE_OFFSET)
						if level < 3:
							makedirs(out, exist_ok = True)
							open(osjoin(out, FILE_NAME + ".rsgp"), "wb").write(file.read(FILE_SIZE))
							print("wrote " + relpath(osjoin(out, FILE_NAME + ".rsgp"), pathout))
						else:
							rsgp_extract(FILE_NAME, FILE_OFFSET, file, out, pathout, level)
						file.seek(temp)
			elif SIGN == b"pgsr":
				file.seek(0)
				rsgp_extract("data", 0, file, out, pathout, level)
		except Exception as e:
			error_message("Failed OBBUnpack: " + type(e).__name__ + " in " + inp + " pos " + str(file.tell()) + ": " + str(e))
# RTON Decode functions
def parse_int8(fp):
# type 08
	return repr(unpack("b", fp.read(1))[0])
def parse_uint8(fp):
# type 0a
	return repr(fp.read(1)[0])
def parse_int16(fp):
# type 10
	return repr(unpack("<h", fp.read(2))[0])
def parse_uint16(fp):
# type 12
	return repr(unpack("<H", fp.read(2))[0])
def parse_int32(fp):
# type 20
	return repr(unpack("<i", fp.read(4))[0])
def parse_float(fp):
# type 22
	return repr(unpack("<f", fp.read(4))[0]).replace("inf", "Infinity").replace("nan", "NaN")
def parse_uvarint(fp):
# type 24, 28, 44 and 48
	return repr(parse_number(fp))
def parse_varint(fp):
# type 25, 29, 45 and 49
	num = parse_number(fp)
	if num % 2:
		num = -num -1
	return repr(num // 2)
def parse_number(fp):
	num = fp.read(1)[0]
	result = num & 0x7f
	i = 128
	while num > 127:
		num = fp.read(1)[0]
		result += i * (num & 0x7f)
		i *= 128
	return result
def parse_uint32(fp):
# type 26
	return repr(unpack("<I", fp.read(4))[0])
def parse_int64(fp):
# type 40
	return repr(unpack("<q", fp.read(8))[0])
def parse_double(fp):
# type 42
	return repr(unpack("<d", fp.read(8))[0]).replace("inf", "Infinity").replace("nan", "NaN")
def parse_uint64(fp):
# type 46
	return repr(unpack("<Q", fp.read(8))[0])
def parse_str(fp):
# types 81, 90
	byte = fp.read(parse_number(fp))
	try:
		return dumps(byte.decode('utf-8'), ensure_ascii = ensureAscii)
	except Exception:
		return dumps(byte.decode('latin-1'), ensure_ascii = ensureAscii)
def parse_printable_str(fp):
# type 82, 92
	return dumps(parse_utf8_str(fp), ensure_ascii = ensureAscii)
def parse_utf8_str(fp):
	i1 = parse_number(fp) # Character length
	string = fp.read(parse_number(fp)).decode()
	i2 = len(string)
	if i1 != i2:
		warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": Unicode string of character length " + str(i2) + " found, expected " + str(i1))
	return string
def parse_cached_str(fp, code, chached_strings, chached_printable_strings):
# types 90, 91, 92, 93
	if code == b"\x90":
		result = parse_str(fp)
		chached_strings.append(result)
	elif code in b"\x91":
		result = chached_strings[parse_number(fp)]
	elif code in b"\x92":
		result = parse_printable_str(fp)
		chached_printable_strings.append(result)
	elif code in b"\x93":
		result = chached_printable_strings[parse_number(fp)]
	return (result, chached_strings, chached_printable_strings)
def parse_ref(fp):
# type 83
	ch = fp.read(1)
	if ch == b"\x00":
		return '"RTID()"'
	elif ch == b"\x02":
		p1 = parse_utf8_str(fp)
		i2 = parse_uvarint(fp)
		i1 = parse_uvarint(fp)
		return dumps("RTID(" + i1 + "." + i2 + "." + fp.read(4)[::-1].hex() + "@" + p1 + ")", ensure_ascii = ensureAscii)
	elif ch == b"\x03":
		p1 = parse_utf8_str(fp)
		return dumps("RTID(" + parse_utf8_str(fp) + "@" + p1 + ")", ensure_ascii = ensureAscii)
	else:
		raise TypeError("unexpected subtype for type 83, found: " + ch.hex())
def root_object(fp, currrent_indent):
# root object
	VER = unpack("<I", fp.read(4))[0]
	string = "{"
	new_indent = currrent_indent + indent
	items = []
	end = "}"
	try:
		key, chached_strings, chached_printable_strings = parse(fp, new_indent, [], [])
		value, chached_strings, chached_printable_strings = parse(fp, new_indent, chached_strings, chached_printable_strings)
		string += new_indent 
		items = [key + doublepoint + value]
		end = currrent_indent + end
		while True:
			key, chached_strings, chached_printable_strings = parse(fp, new_indent, chached_strings, chached_printable_strings)
			value, chached_strings, chached_printable_strings = parse(fp, new_indent, chached_strings, chached_printable_strings)
			items.append(key + doublepoint + value)
	except KeyError as k:
		if str(k) == 'b""':
			if repairFiles:
				warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": end of file")
			else:
				raise EOFError
		elif k.args[0] != b'\xff':
			raise TypeError("unknown tag " + k.args[0].hex())
	except (error, IndexError):
		if repairFiles:
			warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": end of file")
		else:
			raise EOFError
	if sortKeys:
		items = sorted(items)
	return string + (comma + new_indent).join(items) + end
def parse_object(fp, currrent_indent, chached_strings, chached_printable_strings):
# type 85
	string = "{"
	new_indent = currrent_indent + indent
	items = []
	end = "}"
	try:
		key, chached_strings, chached_printable_strings = parse(fp, new_indent, chached_strings, chached_printable_strings)
		value, chached_strings, chached_printable_strings = parse(fp, new_indent, chached_strings, chached_printable_strings)
		string += new_indent 
		items = [key + doublepoint + value]
		end = currrent_indent + end
		while True:
			key, chached_strings, chached_printable_strings = parse(fp, new_indent, chached_strings, chached_printable_strings)
			value, chached_strings, chached_printable_strings = parse(fp, new_indent, chached_strings, chached_printable_strings)
			items.append(key + doublepoint + value)
	except KeyError as k:
		if str(k) == 'b""':
			if repairFiles:
				warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": end of file")
			else:
				raise EOFError
		elif k.args[0] != b'\xff':
			raise TypeError("unknown tag " + k.args[0].hex())
	except (error, IndexError):
		if repairFiles:
			warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": end of file")
		else:
			raise EOFError
	if sortKeys:
		items = sorted(items)
	return (string + (comma + new_indent).join(items) + end, chached_strings, chached_printable_strings)
def parse_list(fp, currrent_indent, chached_strings, chached_printable_strings):
# type 86
	code = fp.read(1)
	if code == b"":
		if repairFiles:
			warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": end of file")
		else:
			raise EOFError
	elif code != b"\xfd":
		raise TypeError("List starts with " + code.hex())
	string = "["
	new_indent = currrent_indent + indent
	items = []
	end = "]"
	i1 = parse_number(fp)
	try:
		value, chached_strings, chached_printable_strings = parse(fp, new_indent, chached_strings, chached_printable_strings)
		string += new_indent
		items = [value]
		end = currrent_indent + end
		while True:
			value, chached_strings, chached_printable_strings = parse(fp, new_indent, chached_strings, chached_printable_strings)
			items.append(value)
	except KeyError as k:
		if str(k) == 'b""':
			if repairFiles:
				warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": end of file")
			else:
				raise EOFError
		elif k.args[0] != b'\xfe':
			raise TypeError("unknown tag " + k.args[0].hex())
	except (error, IndexError):
		if repairFiles:
			warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": end of file")
		else:
			raise EOFError
	i2 = len(items)
	if i1 != i2:
		warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() -1) + ": Array of length " + str(i1) + " found, expected " + str(i2))
	if sortValues:
		items = sorted(sorted(items), key = lambda key : len(key))
	
	return (string + (comma + new_indent).join(items) + end, chached_strings, chached_printable_strings)
def parse(fp, current_indent, chached_strings, chached_printable_strings):
	code = fp.read(1)
	if code == b"\x85":
		return parse_object(fp, current_indent, chached_strings, chached_printable_strings)
	elif code == b"\x86":
		return parse_list(fp, current_indent, chached_strings, chached_printable_strings)
	elif code in cached_codes:
		return parse_cached_str(fp, code, chached_strings, chached_printable_strings)
	return (mappings[code](fp), chached_strings, chached_printable_strings)
cached_codes = [
	b"\x90",
	b"\x91",
	b"\x92",
	b"\x93"
]
mappings = {	
	b"\x00": lambda x: "false",
	b"\x01": lambda x: "true",
	b"\x08": parse_int8,  
	b"\x09": lambda x: "0", # int8_zero
	b"\x0a": parse_uint8,
	b"\x0b": lambda x: "0", # uint8_zero
	b"\x10": parse_int16,
	b"\x11": lambda x: "0",  # int16_zero
	b"\x12": parse_uint16,
	b"\x13": lambda x: "0", # uint16_zero
	b"\x20": parse_int32,
	b"\x21": lambda x: "0", # int32_zero
	b"\x22": parse_float,
	b"\x23": lambda x: "0.0", # float_zero
	b"\x24": parse_uvarint, # int32_uvarint
	b"\x25": parse_varint, # int32_varint
	b"\x26": parse_uint32,
	b"\x27": lambda x: "0", #uint_32_zero
	b"\x28": parse_uvarint, # uint32_uvarint
	b"\x29": parse_varint, # uint32_varint?
	b"\x40": parse_int64,
	b"\x41": lambda x: "0", #int64_zero
	b"\x42": parse_double,
	b"\x43": lambda x: "0.0", # double_zero
	b"\x44": parse_uvarint, # int64_uvarint
	b"\x45": parse_varint, # int64_varint
	b"\x46": parse_uint64,
	b"\x47": lambda x: "0", # uint64_zero
	b"\x48": parse_uvarint, # uint64_uvarint
	b"\x49": parse_varint, # uint64_varint
	b"\x81": parse_str, # uncached string
	b"\x82": parse_printable_str, # uncached printable string
	b"\x83": parse_ref,
	b"\x84": lambda x: "null" # null reference
}
def conversion(inp, out, pathout):
# Recursive file convert function
	check = inp.lower()
	if isfile(inp) and (check.endswith(RTONExtensions) or basename(check).startswith(RTONNoExtensions)):
		try:
			if check[-5:] == ".rton":
				out = out[:-5]
			jfn = out + ".json"
			file = open(inp, "rb")
			if file.read(4) == b"RTON":
				data = root_object(file, current_indent)
				open(jfn, "w", encoding = "utf-8").write(data)
				print("wrote " + relpath(jfn, pathout))
			elif check[-5:] != ".json":
				warning_message("No RTON " + inp)
		except Exception as e:
			error_message(type(e).__name__ + " in " + inp + " pos " + str(file.tell() -1) + ": " + str(e))
	elif isdir(inp):
		makedirs(out, exist_ok = True)
		for entry in listdir(inp):
			input_file = osjoin(inp, entry)
			if isfile(input_file) or input_file != pathout:
				conversion(input_file, osjoin(out, entry), pathout)
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
	
	print("\033[95m\033[1mOBBUnpacker v1.1.2\n(C) 2022 by 1Zulu, h3x4n1um, Luigi Auriemma & Nineteendo\033[0m\n")
	try:
		newoptions = load(open(osjoin(application_path, "options.json"), "rb"))
		for key in options:
			if key in newoptions and newoptions[key] != options[key]:
				if type(options[key]) == type(newoptions[key]):
					options[key] = newoptions[key]
				elif isinstance(options[key], tuple) and isinstance(newoptions[key], list):
					options[key] = tuple([str(i).lower() for i in newoptions[key]])
	except Exception as e:
		error_message(type(e).__name__ + " in options.json: " + str(e))
	
	if options["rsbUnpackLevel"] < 1:
		options["rsbUnpackLevel"] = input_level("OBB/RSB Unpack Level", 1, 5)
	if options["rsgpUnpackLevel"] < 1:
		options["rsgpUnpackLevel"] = input_level("PGSR/RSGP Unpack Level", 2, 5)
	if options["encodedUnpackLevel"] < 1:
		options["encodedUnpackLevel"] = input_level("ENCODED Unpack Level", 4, 5)

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

	if options["comma"] > 0:
		comma = "," + " " * options["comma"]
	else:
		comma = ","
	if options["doublepoint"] > 0:
		doublepoint = ":" + " " * options["doublepoint"]
	else:
		doublepoint = ":"
	if options["indent"] == None:
		indent = current_indent = ""
	elif options["indent"] < 0:
		current_indent = "\n"
		indent = "\t"
	else:
		current_indent = "\n"
		indent = " " * options["indent"]
	ensureAscii = options["ensureAscii"]
	repairFiles = options["repairFiles"]
	RTONExtensions = options["RTONExtensions"]
	RTONNoExtensions = options["RTONNoExtensions"]
	sortKeys = options["sortKeys"]
	sortValues = options["sortValues"]
	
	level_to_name = ["SPECIFY", "OBB/RSB", "PGSR/RSGP", "SECTION", "ENCODED", "DECODED (beta)"]

	blue_print("Working directory: " + getcwd())
	if 6 > options["rsbUnpackLevel"] > 1:
		rsb_input = path_input("OBB/RSB Input file or directory")
		rsb_output = path_input("OBB/RSB " + level_to_name[options["rsbUnpackLevel"]] + " Output directory")
	if 6 > options["rsgpUnpackLevel"] > 2:
		rsgp_input = path_input("PGSR/RSGP Input file or directory")
		rsgp_output = path_input("PGSR/RSGP " + level_to_name[options["rsgpUnpackLevel"]] + " Output directory")
	if 6 > options["encodedUnpackLevel"] > 4:
		encoded_input = path_input("ENCODED Input file or directory")
		if isfile(encoded_input):
			encoded_output = path_input("ENCODED " + level_to_name[options["encodedUnpackLevel"]] + " Output file").removesuffix(".json")
		else:
			encoded_output = path_input("ENCODED " + level_to_name[options["encodedUnpackLevel"]] + " Output directory")

	# Start file_to_folder
	start_time = datetime.datetime.now()
	if 6 > options["rsbUnpackLevel"] > 1:
		file_to_folder(rsb_input, rsb_output, options["rsbUnpackLevel"], options["rsbExtensions"], rsb_output)
	if 6 > options["rsgpUnpackLevel"] > 2:
		file_to_folder(rsgp_input, rsgp_output, options["rsgpUnpackLevel"], options["rsgpExtensions"], rsgp_output)
	if 6 > options["encodedUnpackLevel"] > 4:
		conversion(encoded_input, encoded_output, dirname(encoded_output))

	green_print("finished unpacking in " + str(datetime.datetime.now() - start_time))
	if fail.tell() > 0:
		print("\33[93m" + "Errors occured, check: " + fail.name + "\33[0m")
	bold_input("\033[95mPRESS [ENTER]")
except Exception as e:
	error_message(type(e).__name__ + " : " + str(e))
except BaseException as e:
	warning_message(type(e).__name__ + " : " + str(e))
fail.close() # Close log