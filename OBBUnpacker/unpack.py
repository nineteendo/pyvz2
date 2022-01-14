# OBBUnpacker
# written by Luigi Auriemma & Nineteendo
import os, struct, zlib, sys, traceback, json, datetime
options = {
	"DEBUG_MODE": False,
	"dumpRsgp": False,
	"endswith": (
		".RTON"
	),
	"endswithIgnore": False,
	"enteredPath": False,
	"extractRsgp": True,
	"extensions": (
		".1rsb",
		".obb",
		".rsb",
		".rsgp "
	),
	"startswith": (
		"PACKAGES/",
		"PROPERTIES/"
	),
	"startswithIgnore": True
}

def error_message(string):
	if options["DEBUG_MODE"]:
		string = traceback.format_exc()
	
	fail.write(string + "\n")
	print("\33[91m%s\33[0m" % string)

def path_input(text):
	newstring = input(text)
	if options["enteredPath"]:
		string = newstring
	else:
		string = ""
		quoted = False
		escaped = False
		tempstring = ""
		for char in newstring:
			if escaped:
				if char == '"' or not quoted and char in "\\ ":
					string += tempstring + char
				else:
					string += tempstring + "\\" + char
				
				tempstring = ""
				escaped = False
			elif char == "\\":
				escaped = True
			elif char == '"':
				quoted = not quoted
			elif quoted or char != " ":
				string += tempstring + char
				tempstring = ""
			else:
				tempstring += " "
		
		return os.path.realpath(string)

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

def pgsr_extract(file, out, PGSR_NAME, PGSR_OFFSET, PGSR_SIZE):
	BACKUP_OFFSET = file.tell()
	file.seek(PGSR_OFFSET)
	if file.read(4) == b"pgsr":
		VER = struct.unpack('<L', file.read(4))[0]
		file.seek(8, 1)
		TYPE = struct.unpack('<L', file.read(4))[0]
		PGSR_BASE = struct.unpack('<L', file.read(4))[0]
		OFFSET = 0
		ZSIZE = 0
		SIZE = 0
		for x in range(0, 2):
			TMP_OFFSET = struct.unpack('<L', file.read(4))[0]
			TMP_ZSIZE = struct.unpack('<L', file.read(4))[0]
			TMP_SIZE = struct.unpack('<L', file.read(4))[0]
			file.seek(4, 1)
			if TMP_SIZE != 0:
				OFFSET = TMP_OFFSET
				ZSIZE = TMP_ZSIZE
				SIZE = TMP_SIZE
		
		file.seek(16, 1)
		INFO_SIZE = struct.unpack('<L', file.read(4))[0]
		INFO_OFFSET = struct.unpack('<L', file.read(4))[0]
		INFO_OFFSET += PGSR_OFFSET
		INFO_LIMIT = INFO_OFFSET + INFO_SIZE
		file.seek(INFO_OFFSET)
		
		DECOMPRESSED = b""
		X_ZSIZE = ZSIZE
		X_SIZE = SIZE
		TMP = file.tell()
		DECODED_NAME = None
		NAME_DICT = {}
		while DECODED_NAME != "":			
			NAME, NAME_DICT = GET_NAME(file, TMP, NAME_DICT)
			DECODED_NAME = NAME.decode().replace("\\", os.sep)
			ENCODED = struct.unpack('<L', file.read(4))[0]
			FILE_OFFSET = struct.unpack('<L', file.read(4))[0]
			SIZE = struct.unpack('<L', file.read(4))[0]
			if ENCODED != 0:
				file.seek(20, 1)
			
			temp = file.tell()	
			if DECODED_NAME != "" and (DECODED_NAME.startswith(options["startswith"]) or options["startswithIgnore"]) and (DECODED_NAME.endswith(options["endswith"]) or options["endswithIgnore"]):
				os.makedirs(os.path.dirname(os.path.join(out, DECODED_NAME)), exist_ok=True)
				if ENCODED == 0 and TYPE == 1:
					file.seek(PGSR_OFFSET + PGSR_BASE + FILE_OFFSET)
					open(os.path.join(out, DECODED_NAME), "wb").write(file.read(SIZE))
				else:
					if TYPE == 1:
						file.seek(PGSR_OFFSET + PGSR_BASE)
						DECOMPRESSED = zlib.decompress(file.read(X_ZSIZE))
					elif DECOMPRESSED == b"":
						file.seek(PGSR_OFFSET + OFFSET)
						print("\033[94mDecompressing files ...\033[0m")
						DECOMPRESSED = zlib.decompress(file.read(X_ZSIZE))
			
					open(os.path.join(out, DECODED_NAME), "wb").write(DECOMPRESSED[FILE_OFFSET:FILE_OFFSET+SIZE])
				
				print("wrote " + os.path.relpath(os.path.join(out, DECODED_NAME), pathout))
			
			file.seek(temp)
			
	file.seek(BACKUP_OFFSET)
		
## Recursive file convert function
def conversion(inp, out):
	if os.path.isdir(inp) and inp != pathout:
		os.makedirs(out, exist_ok=True)
		for entry in sorted(os.listdir(inp)):
			input_file = os.path.join(inp, entry)
			output_file = os.path.join(out, entry)
			if os.path.isfile(input_file):
				output_file = os.path.splitext(output_file)[0]
			conversion(input_file, output_file)
	elif os.path.isfile(inp) and inp.endswith(options["extensions"]):
		try:
			file = open(inp,"rb")
			SIGN = file.read(4)
			if SIGN == b"pgsr":
				file.seek(0, 2)
				SIZE = file.tell()
				file.seek(0)
				pgsr_extract("", 0, SIZE)
			elif SIGN == b"1bsr":
				file.seek(40)
				FILES = struct.unpack('<L', file.read(4))[0]
				OFFSET = struct.unpack('<L', file.read(4))[0]
				file.seek(OFFSET)
				for i in range(0, FILES):
					NAME = file.read(128).strip(b"\x00").decode()
					OFFSET = struct.unpack('<L', file.read(4))[0]
					SIZE = struct.unpack('<L', file.read(4))[0]
					file.seek(68, 1)
					if options["dumpRsgp"]:
						temp = file.tell()
						file.seek(OFFSET)
						os.makedirs(out, exist_ok=True)
						open(os.path.join(out, NAME + ".rsgp"), "wb").write(file.read(SIZE))
						print("wrote " + os.path.relpath(os.path.join(out, NAME + ".pgsr"), pathout))
						file.seek(temp)
					
					if options["extractRsgp"]:
						pgsr_extract(file, out, NAME, OFFSET, SIZE)
		except Exception as e:
			error_message("Failed OBBUnpack: %s in %s pos %s: %s" % (type(e).__name__, inp, file.tell() - 1, e))
try:
	fail = open(os.path.join(sys.path[0], "fail.txt"), "w")
	if sys.version_info[0] < 3:
		raise RuntimeError("Must be using Python 3")
    
	print("\033[95m\033[1mOBBUnpacker v1.1.0\n(C) 2021 by Nineteendo\033[0m\n")
	try:
		newoptions = json.load(open(os.path.join(sys.path[0], "options.json"), "rb"))
		for key in options:
			if key in newoptions and newoptions[key] != options[key]:
				if type(options[key]) == type(newoptions[key]):
					options[key] = newoptions[key]
				elif isinstance(options[key], tuple) and isinstance(newoptions[key], list):
					options[key] = tuple([str(i) for i in newoptions[key]])
	except Exception as e:
		error_message('%s in options.json: %s' % (type(e).__name__, e))
	
	print("Working directory: " + os.getcwd())
	pathin = path_input("\033[1mInput file or directory\033[0m: ")
	pathout = path_input("\033[1mOutput directory\033[0m: ")
	
	# Start conversion
	start_time = datetime.datetime.now()
	conversion(pathin, pathout)
	print("Duration: %s" % (datetime.datetime.now() - start_time))
except BaseException as e:
	error_message('%s: %s' % (type(e).__name__, e))

fail.close()