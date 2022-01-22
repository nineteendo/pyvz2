# JSON parser
# written by Nineteendo
# usage: put json files in jsons & run

import os, json, struct, sys, traceback, datetime

# Default Options
options = {
	"allowNan": True,
	"allowAllJSON": True,
	"binObjClasses": (
		"drapersavedata",
		"globalsavedata",
		"playerinfolocalsavedata",
		"lootsavedata",
		"savegameheader"
	),
	"cachKeyLimit": 1048575,
	"cachValueLimit": 1048575,
	"commaSeparator": "",
	"confirmPath": True,
	"datObjClasses": (
		"playerinfo",
	),
	"DEBUG_MODE": False,
	"doublePointSeparator": " ",
	"ensureAscii": False,
	"enteredPath": False,
	"indent": "\t",
	"RTONExtensions": (
		".bin",
		".dat",
		".rton",
		".section"
	),
	"RTONNoExtensions": (
		"draper_",
		"local_profiles",
		"loot",
		"_saveheader_rton"
	),
	"repairFiles": False,
	"shortNames": False,
	"sortKeys": False
}
def error_message(string):
	if options["DEBUG_MODE"]:
		string = traceback.format_exc()
	
	fail.write(string + "\n")
	print("\033[91m%s\033[0m" % string)

def path_input(text):
	string = ""
	newstring = input("\033[1m%s\033[0m: " % text)
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
			newstring = input("\033[1m\033[91mEnter a path\033[0m: ")
		else:
			newstring = ""
			string = os.path.realpath(string)
			if options["confirmPath"]:
				newstring = input("\033[1mConfirm \033[100m%s\033[0m: " % string)

	return string

# Extra list class
class list2:
	def __init__(self, data):
		self.data = data

# Data Types
false = b'\x00'
true = b'\x01'
rtid_id_string = b'\x02'
rtid_string = b'\x03'
int8 = b'\x08'
int8_zero = b'\x09'
uint8 = b'\x0a'
uint8_zero = b'\x0b'
int16 = b'\x10'
int16_zero = b'\x11'
uint16 = b'\x12'
uint16_zero = b'\x13'
int32 = b'\x20'
int32_zero = b'\x21'
floating_point = b'\x22'
floating_point_zero = b'\x23'
positive_int32_varint = b'\x24'
negative_int32_varint= b'\x25'
uint32 = b'\x26'
uint32_zero = b'\x27'
positive_uint32_varint = b'\x28'
negative_uint32_varint = b'\x29'
int64 = b'\x40'
int64_zero = b'\x41'
double = b'\x42'
double_zero = b'\x43'
positive_int64_varint = b'\x44'
negative_int64_varint = b'\x45'
uint64 = b'\x46'
uint64_zero = b'\x47'
positive_uint64_varint = b'\x48'
negative_uint64_varint = b'\x49'
latin_string = b'\x81'
utf8_string = b'\x82'
RTID = b'\x83'
RTID_empty = b'\x84'
object_start = b'\x85'
array = b'\x86'
cached_latin_string = b'\x90'
cached_latin_string_recall = b'\x91'
cached_utf8_string = b'\x92'
cached_utf8_string_recall = b'\x93'
array_start = b'\xfd'
array_end = b'\xfe'
object_end = b'\xff'

def encode_bool(boolean):
	if boolean == False:
		return false
	else:
		return true

def encode_number(integ):
	integ, i = divmod(integ, 128)
	if (integ):
		i += 128
	
	string = bytes([i])
	while integ:
		integ, i = divmod(integ, 128)
		if (integ):
			i += 128
		
		string += bytes([i])
	
	return string

def encode_unicode(string):
	encoded_string = string.encode()
	return encode_number(len(string)) + encode_number(len(encoded_string)) + encoded_string

def encode_rtid(string):
	if '@' in string:
		name, type = string[5:-1].split('@')
		if name.count(".") == 2:
			i2, i1, i3 = name.split(".")
			name = encode_number(int(i1)) + encode_number(int(i2)) + bytes.fromhex(i3)[::-1]
			encode = rtid_id_string
		else:
			name = encode_unicode(name)
			encode = rtid_string
		
		return RTID + encode + encode_unicode(type) + name
	else:
		return RTID + false

def encode_int(integ):
	if integ == 0:
		return int32_zero
	elif -128 <= integ <= 127:
		return int8 + struct.pack('<b', integ)
	elif 0 <= integ <= 255:
		return uint8 + struct.pack('<B', integ)
	elif -32768 <= integ <= 32767:
		return int16 + struct.pack('<h', integ)
	elif 0 <= integ < 65535:
		return uint16 + struct.pack('<H', integ)
	elif 0 <= integ <= 2097151:
		return positive_int32_varint + encode_number(integ)
	elif -2097151 <= integ <= 0:
		return negative_int32_varint + encode_number(-integ)
	elif -2147483648 <= integ <= 2147483647:
		return int32 + struct.pack('<i', integ)
	elif 0 <= integ < 4294967295:
		return uint32 + struct.pack('<I', integ)
	elif 0 <= integ <= 562949953421311:
		return positive_int64_varint + encode_number(integ)
	elif -562949953421311 <= integ <= 0:
		return negative_int64_varint + encode_number(-integ)
	elif -9223372036854775808 <= integ <= 9223372036854775807:
		return int64 + struct.pack('<q', integ)
	elif 0 <= integ <= 18446744073709551615:
		return uint64 + struct.pack('<Q', integ)
	elif 0 <= integ:
		return positive_int64_varint + encode_number(integ)
	else:
		return negative_int64_varint + encode_number(-integ)

def encode_floating_point(dec):
	if dec == 0:
		return floating_point_zero
	elif dec != dec or dec == struct.unpack('<f', struct.pack("<f", dec))[0]:
		return floating_point + struct.pack("<f", dec)
	else:
		return double + struct.pack("<d", dec)

def encode_key(string, cached_latin_strings, cached_utf8_strings):
	if len(string) == len(string.encode('latin-1', 'ignore')):
		if string in cached_latin_strings:
			data = cached_latin_string_recall + encode_number(cached_latin_strings[string])
		elif len(cached_latin_strings) < options["cachKeyLimit"]:
			cached_latin_strings[string] = len(cached_latin_strings)
			data = cached_latin_string + encode_number(len(string)) + string.encode('latin-1')
		else:
			data = latin_string + encode_number(len(string)) + string.encode('latin-1')
	else:
		if string in cached_utf8_strings:
			data = cached_utf8_string_recall + encode_number(cached_utf8_strings[string])
		elif len(cached_utf8_strings) < options["cachKeyLimit"]:
			cached_utf8_strings[string] = len(cached_utf8_strings)
			data = cached_utf8_string + encode_unicode(string)
		else:
			data = utf8_string + encode_unicode(string)
	
	return (data, cached_latin_strings, cached_utf8_strings)


def encode_string(string, cached_latin_strings, cached_utf8_strings):
	if len(string) == len(string.encode('latin-1', 'ignore')):
		if string in cached_latin_strings:
			data = cached_latin_string_recall + encode_number(cached_latin_strings[string])
		elif len(cached_latin_strings) < options["cachValueLimit"]:
			cached_latin_strings[string] = len(cached_latin_strings)
			data = cached_latin_string + encode_number(len(string)) + string.encode('latin-1')
		else:
			data = latin_string + encode_number(len(string)) + string.encode('latin-1')
	else:
		if string in cached_utf8_strings:
			data = cached_utf8_string_recall + encode_number(cached_utf8_strings[string])
		elif len(cached_utf8_strings) < options["cachValueLimit"]:
			cached_utf8_strings[string] = len(cached_utf8_strings)
			data = cached_utf8_string + encode_unicode(string)
		else:
			data = utf8_string + encode_unicode(string)
	
	return (data, cached_latin_strings, cached_utf8_strings)

def parse_array(data, cached_latin_strings, cached_utf8_strings):
	string = array + array_start + encode_number(len(data))
	for v in data:
		v, cached_latin_strings, cached_utf8_strings = parse_json(v, cached_latin_strings, cached_utf8_strings)
		string += v
	
	return (string + array_end, cached_latin_strings, cached_utf8_strings)

def parse_object(data, cached_latin_strings, cached_utf8_strings):
	string = object_start
	for v in data:
		key, value = v
		key, cached_latin_strings, cached_utf8_strings = encode_key(key, cached_latin_strings, cached_utf8_strings)
		value, cached_latin_strings, cached_utf8_strings = parse_json(value, cached_latin_strings, cached_utf8_strings)
		string += key + value
	
	return (string + object_end, cached_latin_strings, cached_utf8_strings)

def parse_json(data, cached_latin_strings, cached_utf8_strings):
	if isinstance(data, list):
		return parse_array(data, cached_latin_strings, cached_utf8_strings)
	elif isinstance(data, list2):
		return parse_object(data.data, cached_latin_strings, cached_utf8_strings)
	elif isinstance(data, bool):
		return (encode_bool(data), cached_latin_strings, cached_utf8_strings)
	elif isinstance(data, int):
		return (encode_int(data), cached_latin_strings, cached_utf8_strings)
	elif isinstance(data, float):
		return (encode_floating_point(data), cached_latin_strings, cached_utf8_strings)
	elif isinstance(data, str):
		if data == 'RTID(' + data[5:-1] + ')':
			return (encode_rtid(data), cached_latin_strings, cached_utf8_strings)
		else:
			return encode_string(data, cached_latin_strings, cached_utf8_strings)
	else:
		raise TypeError(type(data))

# Convert file
def conversion(inp, out):
	if os.path.isdir(inp) and inp != pathout:
		os.makedirs(out, exist_ok=True)
		for entry in sorted(os.listdir(inp)):
			conversion(os.path.join(inp, entry), os.path.join(out, entry))
	elif os.path.isfile(inp) and inp.lower().endswith(".json") and (options["allowAllJSON"] or inp.lower().endswith(options["RTONExtensions"], 0, -5) or os.path.basename(inp).lower().startswith(options["RTONNoExtensions"])):
		write = out.removesuffix(".json")
		try:
			data = json.load(open(inp, 'rb'), object_pairs_hook = encode_object_pairs).data
		
		except Exception as e:
			error_message('%s in %s: %s' % (type(e).__name__, inp, e))
		else:
			try:
				encoded_data = b'RTON\x01\x00\x00\x00%sDONE' % parse_object(data, {}, {})[0][1:]
				# No RTON extension
				if "" == os.path.splitext(write)[1] and not os.path.basename(write).lower().startswith(options["RTONNoExtensions"]):
					vals = list(values_from_keys(data, ["objects","objclass"]))
					if any(value in vals for value in options["datObjClasses"]):
						write += ".dat"
					elif any(value in vals for value in options["binObjClasses"]):
						write += ".bin"
					else:
						write += ".rton"
				open(write, 'wb').write(encoded_data)
				print("wrote " + os.path.relpath(write, pathout))
			except Exception as e:
				error_message('%s in %s: %s' % (type(e).__name__, inp, e))

def encode_object_pairs(pairs):
	if options["sortKeys"]:
		pairs = sorted(pairs)
		
	return list2(pairs)

def values_from_keys(data, keyz):
	if keyz == []:
		yield str(data).lower()
	elif isinstance(data, list):
		for val in data:
			yield from values_from_keys(val, keyz)
	elif isinstance(data, list2):
		for val in data.data:
			yield from values_from_keys(val, keyz)
	elif isinstance(data, tuple):
		key, value = data
		if keyz[0] == key:
			yield from values_from_keys(value, keyz[1:])

try:
	os.system('')
	if getattr(sys, 'frozen', False):
		application_path = os.path.dirname(sys.executable)
	else:
		application_path = sys.path[0]

	fail = open(os.path.join(application_path, "fail.txt"), "w")
	if sys.version_info[0] < 3:
		raise RuntimeError("Must be using Python 3")
	
	print("\033[95m\033[1mJSON RTONEncoder v1.1.0\n(C) 2021 by Nineteendo\033[0m\n")
	try:
		newoptions = json.load(open(os.path.join(application_path, "options.json"), "rb"))
		for key in options:
			if key in newoptions:
				if type(options[key]) == type(newoptions[key]):
					options[key] = newoptions[key]
				elif isinstance(options[key], tuple) and isinstance(newoptions[key], list):
					options[key] = tuple([str(i).lower() for i in newoptions[key]])
				elif key == "Indent" and type(newoptions[key]) in [int, type(None)]:
					options[key] = newoptions[key]
	except Exception as e:
		error_message("%s in options.json: %s" % (type(e).__name__, e))
	
	print("Working directory: " + os.getcwd())
	pathin = path_input("Input file or directory")
	if os.path.isfile(pathin):
		pathout = path_input("Output file").removesuffix(".json")
	else:
		pathout = path_input("Output directory")
	
	# Start conversion
	start_time = datetime.datetime.now()
	conversion(pathin, pathout)
	print("\033[32mfinished converting %s in %s\033[0m" % (pathin, datetime.datetime.now() - start_time))
	input("\033[95m\033[1mPRESS [ENTER]\033[0m")
except BaseException as e:
	error_message("%s: %s" % (type(e).__name__, e))

fail.close()