# OBBUnpacker
# written by Luigi Auriemma & Nineteendo
import os, struct, zlib, sys, traceback, json, time
options = {
	"DEBUG_MODE": False,
	"extractAllFiles": False,
	"dumpRsgp": False,
	"enteredPath": False,
	"extractRsgp": True,
	"extensions": (
		".1rsb",
		".obb",
		".rsb",
		".rsgp "
	),
	"startswith": (
		"PACKAGES/"
	)
}

def error_message(string):
	if options["DEBUG_MODE"]:
		string = traceback.format_exc()
	
	fail.write(string + "\n")
	print("\33[91m%s\33[0m" % string)

def GET_NAME(obb, NAME, NAME_DICT):
	TMP_BYTE = b""
	while TMP_BYTE != b"\x00":
		NAME += TMP_BYTE
		TMP_BYTE = obb.read(1)
		TMP_LENGTH = 4 * struct.unpack('<L', obb.read(3) + b"\x00")[0]
		if TMP_LENGTH != 0:
			NAME_DICT[NAME] = TMP_LENGTH
	return (NAME, NAME_DICT)

def pgsr_extract(obb, out, PGSR_NAME, PGSR_OFFSET, PGSR_SIZE):
	BACKUP_OFFSET = obb.tell()
	obb.seek(PGSR_OFFSET)
	if obb.read(4) == b"pgsr":
		VER = struct.unpack('<L', obb.read(4))[0]
		obb.seek(8, 1)
		TYPE = struct.unpack('<L', obb.read(4))[0]
		PGSR_BASE = struct.unpack('<L', obb.read(4))[0]
		OFFSET = 0
		ZSIZE = 0
		SIZE = 0
		for x in range(0, 2):
			TMP_OFFSET = struct.unpack('<L', obb.read(4))[0]
			TMP_ZSIZE = struct.unpack('<L', obb.read(4))[0]
			TMP_SIZE = struct.unpack('<L', obb.read(4))[0]
			obb.seek(4, 1)
			if TMP_SIZE != 0:
				OFFSET = TMP_OFFSET
				ZSIZE = TMP_ZSIZE
				SIZE = TMP_SIZE
		
		obb.seek(16, 1)
		INFO_SIZE = struct.unpack('<L', obb.read(4))[0]
		INFO_OFFSET = struct.unpack('<L', obb.read(4))[0]
		INFO_OFFSET += PGSR_OFFSET
		INFO_LIMIT = INFO_OFFSET + INFO_SIZE
		obb.seek(INFO_OFFSET)
		
		DECOMPRESSED = b""
		X_ZSIZE = ZSIZE
		X_SIZE = SIZE
		TMP = obb.tell()
		DECODED_NAME = None
		NAME_DICT = {}
		while DECODED_NAME != "":
			NAME = b""
			temp = obb.tell()
			for key in list(NAME_DICT.keys()):
				if NAME_DICT[key] + TMP < temp:
					NAME_DICT.pop(key)
				else:
					NAME = key
			
			NAME, NAME_DICT = GET_NAME(obb, NAME, NAME_DICT)
			DECODED_NAME = NAME.decode().replace("\\", "/")
			ENCODED = struct.unpack('<L', obb.read(4))[0]
			FILE_OFFSET = struct.unpack('<L', obb.read(4))[0]
			SIZE = struct.unpack('<L', obb.read(4))[0]
			if ENCODED != 0:
				obb.seek(20, 1)
				if TYPE == 1:
					temp = obb.tell()
					obb.seek(PGSR_OFFSET + PGSR_BASE)
					DECOMPRESSED = zlib.decompress(obb.read(X_ZSIZE))
					obb.seek(temp)
				
			temp = obb.tell()
			if DECODED_NAME != "" and (DECODED_NAME.startswith(options["startswith"]) or options["extractAllFiles"]):
				os.makedirs(os.path.dirname(os.path.join(out, DECODED_NAME)), exist_ok=True)
				if ENCODED == 0 and TYPE == 1:
					obb.seek(PGSR_OFFSET + PGSR_BASE + FILE_OFFSET)
					open(os.path.join(out, DECODED_NAME), "wb").write(obb.read(SIZE))
				else:
					if DECOMPRESSED == b"":
						obb.seek(PGSR_OFFSET + OFFSET)
						print("\033[94mDecompressing files ...\033[0m")
						DECOMPRESSED = zlib.decompress(obb.read(X_ZSIZE))
			
					open(os.path.join(out, DECODED_NAME), "wb").write(DECOMPRESSED[FILE_OFFSET:FILE_OFFSET+SIZE])
				
				print("wrote " + os.path.join(os.path.relpath(out, pathout), DECODED_NAME))
			
			obb.seek(temp)
			
	obb.seek(BACKUP_OFFSET)
		
## Recursive file convert function
def conversion(inp, out):
	if os.path.isdir(inp) and os.path.realpath(inp) != os.path.realpath(pathout):
		os.makedirs(out, exist_ok=True)
		for entry in sorted(os.listdir(inp)):
			conversion(os.path.join(inp, entry), os.path.join(out, entry))
	elif os.path.isfile(inp) and inp.endswith(options["extensions"]):
		try:
			obb = open(inp,"rb")
			out = os.path.splitext(out)[0]
			SIGN = obb.read(4)
			if SIGN == b"pgsr":
				obb.seek(0, 2)
				SIZE = obb.tell()
				obb.seek(0)
				pgsr_extract("", 0, SIZE)
			elif SIGN == b"1bsr":
				obb.seek(40)
				FILES = struct.unpack('<L', obb.read(4))[0]
				OFFSET = struct.unpack('<L', obb.read(4))[0]
				obb.seek(OFFSET)
				for i in range(0, FILES):
					NAME = obb.read(128).strip(b"\x00").decode()
					OFFSET = struct.unpack('<L', obb.read(4))[0]
					SIZE = struct.unpack('<L', obb.read(4))[0]
					obb.seek(68, 1)
					if options["dumpRsgp"]:
						temp = obb.tell()
						obb.seek(OFFSET)
						os.makedirs(out, exist_ok=True)
						open(os.path.join(out, NAME + ".pgsr"), "wb").write(obb.read(SIZE))
						print("wrote " + os.path.join(os.path.relpath(out, pathout), NAME + ".pgsr"))
						obb.seek(temp)
					
					if options["extractRsgp"]:
						pgsr_extract(obb, out, NAME, OFFSET, SIZE)
		except Exception as e:
			error_message("Failed OBBUnpack: %s in %s pos %s: %s" % (type(e).__name__, inp, obb.tell() - 1, e))
try:
	fail = open(os.path.join(sys.path[0], "fail.txt"), "w")
	if sys.version_info[0] < 3:
		raise RuntimeError("Must be using Python 3")
    
	print("\033[95m\033[1mOBBUnpacker v1.1.0\n(C) 2021 by Nineteendo\033[0m\n")
	print("Working directory: " + os.getcwd())
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
	
	pathin = input("\033[1mInput file or directory\033[0m: ")
	pathout = input("\033[1mOutput directory\033[0m: ")
	if not options["enteredPath"]:
		pathin = pathin.replace("\\ ", " ")
		pathout = pathout.replace("\\ ", " ")

	# Start conversion
	start_time = time.time()
	conversion(pathin, pathout)
	print("--- %s seconds ---" % (time.time() - start_time))
except BaseException as e:
	error_message('%s: %s' % (type(e).__name__, e))
fail.close()