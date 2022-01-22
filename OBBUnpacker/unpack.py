# OBBUnpacker
# written by Luigi Auriemma & Nineteendo
import os, struct, zlib, sys, traceback, json, datetime
options = {
	"confirmPath": True,
	"DEBUG_MODE": False,
	"dumpRsgp": False,
	"endswith": (
		".rton",
	),
	"endswithIgnore": False,
	"enteredPath": False,
	"extractRsgp": True,
	"extensions": (
		".1bsr",
		".rsb1",
		".bsr",
		".rsb",
		".obb",
		".pgsr",
		".rsgp"
	),
	"pgsrEndswith": (),
	"pgsrEndswithIgnore": True,
	"pgsrStartswith": (
		"packages",
		"__manifestgroup__",
		"worldpackages_"
	),
	"pgsrStartswithIgnore": False,
	"startswith": (
		"packages/",
		"properties/"
	),
	"startswithIgnore": False
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

def pgsr_extract(file, out, PGSR_OFFSET, PGSR_SIZE):
	BACKUP_OFFSET = file.tell()
	file.seek(PGSR_OFFSET)
	if file.read(4) == b"pgsr":
		VER = struct.unpack('<L', file.read(4))[0]
		
		file.seek(8, 1)
		TYPE = struct.unpack('<L', file.read(4))[0]
		PGSR_BASE = struct.unpack('<L', file.read(4))[0]
		
		data = ""
		OFFSET = struct.unpack('<L', file.read(4))[0]
		ZSIZE = struct.unpack('<L', file.read(4))[0]
		SIZE = struct.unpack('<L', file.read(4))[0]
		if SIZE != 0:
			file.seek(PGSR_OFFSET + OFFSET)
			if TYPE == 1:
				data = file.read(ZSIZE)
			else:
				print("\033[94mDecompressing ...\033[0m")
				data = zlib.decompress(file.read(ZSIZE))
		else:
			file.seek(4, 1)
			OFFSET = struct.unpack('<L', file.read(4))[0]
			ZSIZE = struct.unpack('<L', file.read(4))[0]
			SIZE = struct.unpack('<L', file.read(4))[0]
			if SIZE != 0:
				file.seek(PGSR_OFFSET + OFFSET)
				print("\033[94mDecompressing ...\033[0m")
				data = zlib.decompress(file.read(ZSIZE))
		
		file.seek(PGSR_OFFSET + 72)
		INFO_SIZE = struct.unpack('<L', file.read(4))[0]
		INFO_OFFSET = PGSR_OFFSET + struct.unpack('<L', file.read(4))[0]
		INFO_LIMIT = INFO_OFFSET + INFO_SIZE
		
		file.seek(INFO_OFFSET)
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
			
			if DECODED_NAME != "" and (DECODED_NAME.replace("\\", "/").lower().startswith(options["startswith"]) or options["startswithIgnore"]) and (DECODED_NAME.replace("\\", "/").lower().endswith(options["endswith"]) or options["endswithIgnore"]):
				os.makedirs(os.path.dirname(os.path.join(out, DECODED_NAME)), exist_ok=True)
				open(os.path.join(out, DECODED_NAME), "wb").write(data[FILE_OFFSET: FILE_OFFSET + SIZE])
				print("wrote " + os.path.relpath(os.path.join(out, DECODED_NAME), pathout))
			
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
	elif os.path.isfile(inp) and inp.lower().endswith(options["extensions"]):
		try:
			file = open(inp,"rb")
			if file.read(4) == b"1bsr":
				file.seek(40)
				FILES = struct.unpack('<L', file.read(4))[0]
				OFFSET = struct.unpack('<L', file.read(4))[0]
				file.seek(OFFSET)
				for i in range(0, FILES):
					NAME = file.read(128).strip(b"\x00").decode()
					OFFSET = struct.unpack('<L', file.read(4))[0]
					SIZE = struct.unpack('<L', file.read(4))[0]
					
					file.seek(68, 1)
					if (NAME.lower().startswith(options["pgsrStartswith"]) or options["pgsrStartswithIgnore"]) and (NAME.lower().endswith(options["pgsrEndswith"]) or options["pgsrEndswithIgnore"]):
						if options["dumpRsgp"]:
							temp = file.tell()
							file.seek(OFFSET)
							os.makedirs(out, exist_ok=True)
							open(os.path.join(out, NAME + ".rsgp"), "wb").write(file.read(SIZE))
							print("wrote " + os.path.relpath(os.path.join(out, NAME + ".rsgp"), pathout))
							file.seek(temp)
						
						if options["extractRsgp"]:
							pgsr_extract(file, out, OFFSET, SIZE)
			else:
				file.seek(0, 2)
				SIZE = file.tell()
				pgsr_extract(file, out, 0, SIZE)
		except Exception as e:
			error_message("Failed OBBUnpack: %s in %s pos %s: %s" % (type(e).__name__, inp, file.tell() - 1, e))
try:
	os.system('')
	if getattr(sys, 'frozen', False):
		application_path = os.path.dirname(sys.executable)
	else:
		application_path = sys.path[0]

	fail = open(os.path.join(application_path, "fail.txt"), "w")
	if sys.version_info[0] < 3:
		raise RuntimeError("Must be using Python 3")
	
	print("\033[95m\033[1mOBBUnpacker v1.1.0\n(C) 2021 by Nineteendo\033[0m\n")
	try:
		newoptions = json.load(open(os.path.join(application_path, "options.json"), "rb"))
		for key in options:
			if key in newoptions and newoptions[key] != options[key]:
				if type(options[key]) == type(newoptions[key]):
					options[key] = newoptions[key]
				elif isinstance(options[key], tuple) and isinstance(newoptions[key], list):
					options[key] = tuple([str(i).lower() for i in newoptions[key]])
	except Exception as e:
		error_message('%s in options.json: %s' % (type(e).__name__, e))
	
	print("Working directory: " + os.getcwd())
	pathin = path_input("Input file or directory")
	pathout = path_input("Output directory")
	
	# Start conversion
	start_time = datetime.datetime.now()
	conversion(pathin, pathout)
	print("\033[32mfinished unpacking %s in %s\033[0m" % (pathin, datetime.datetime.now() - start_time))
	input("\033[95m\033[1mPRESS [ENTER]\033[0m")
except BaseException as e:
	error_message('%s: %s' % (type(e).__name__, e))

fail.close()