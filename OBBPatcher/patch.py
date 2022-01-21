import zlib, os, sys, traceback, json, struct, datetime
options = {
	"confirmPath": True,
	"DEBUG_MODE": False,
	"enteredPath": False,
	"singleFile": False,
	"pgsrEndswith": (),
	"pgsrEndswithIgnore": True,
	"pgsrStartswith": (
		"packages",
		"__manifestgroup__",
		"worldpackages_"
	),
	"pgsrStartswithIgnore": False
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

def pgsr_patch_data(NAME, file, pathout_data, PGSR_OFFSET):
	BACKUP_OFFSET = file.tell()
	file.seek(PGSR_OFFSET)
	if file.read(4) == b"pgsr":
		try:
			patch_data = open(os.path.join(patch, NAME + ".section"), "rb").read()
		except:
			pass
		else:
			try:
				VER = struct.unpack('<L', file.read(4))[0]
				
				file.seek(8, 1)
				TYPE = struct.unpack('<L', file.read(4))[0]
				PGSR_BASE = struct.unpack('<L', file.read(4))[0]
				
				OFFSET = struct.unpack('<L', file.read(4))[0]
				ZSIZE = struct.unpack('<L', file.read(4))[0]
				SIZE = struct.unpack('<L', file.read(4))[0]
				if SIZE != 0:
					data = patch_data + bytes(SIZE - len(patch_data))
					if TYPE == 1:
						pathout_data = pathout_data[:PGSR_OFFSET + OFFSET] + data + pathout_data[PGSR_OFFSET + OFFSET + ZSIZE:]
					else:
						print("\033[94mCompressing ...\033[0m")
						compressed_data = zlib.compress(data, 9)
						compressed_data += bytes(ZSIZE - len(compressed_data))
						pathout_data = pathout_data[:PGSR_OFFSET + OFFSET] + compressed_data + pathout_data[PGSR_OFFSET + OFFSET + ZSIZE:]
				else:
					file.seek(4, 1)
					OFFSET = struct.unpack('<L', file.read(4))[0]
					ZSIZE = struct.unpack('<L', file.read(4))[0]
					SIZE = struct.unpack('<L', file.read(4))[0]
					if SIZE != 0:
						print("\033[94mCompressing ...\033[0m")
						compressed_data = zlib.compress(patch_data + bytes(SIZE - len(patch_data)), 9)
						compressed_data += bytes(ZSIZE - len(compressed_data))
						pathout_data = pathout_data[:PGSR_OFFSET + OFFSET] + compressed_data + pathout_data[PGSR_OFFSET + OFFSET + ZSIZE:]
			
				print("applied %s.section" % NAME)
			except Exception as e:
				error_message('%s while patching %s.section: %s' % (type(e).__name__, NAME, e))
	
	file.seek(BACKUP_OFFSET)
	return pathout_data

try:
	os.system('')
	if getattr(sys, 'frozen', False):
		application_path = os.path.dirname(sys.executable)
	else:
		application_path = sys.path[0]

	fail = open(os.path.join(application_path, "fail.txt"), "w")
	if sys.version_info[0] < 3:
		raise RuntimeError("Must be using Python 3")
	
	print("\033[95m\033[1mOBB SectionPatch_dataer v1.1.0\n(C) 2021 by Nineteendo\033[0m\n")
	try:
		newoptions = json.load(open(os.path.join(application_path, "options.json"), "rb"))
		for key in options:
			if key in newoptions:
				if type(options[key]) == type(newoptions[key]):
					options[key] = newoptions[key]
				elif isinstance(options[key], tuple) and isinstance(newoptions[key], list):
					options[key] = tuple([str(i) for i in newoptions[key]])
	except Exception as e:
		error_message('%s in options.json: %s' % (type(e).__name__, e))
	
	print("Working directory: " + os.getcwd())
	file = open(path_input("Input file"), "rb")
	pathout = path_input("Output file")
	patch = path_input("Patch directory")
	pathout_data = file.read()
	file.seek(0)
	if file.read(4) == b"1bsr":
		if options["singleFile"]:
			PGSR_NAME = input("PGSR/RSGP name=").lower()
		
		start_time = datetime.datetime.now()
		file.seek(40)
		FILES = struct.unpack('<L', file.read(4))[0]
		OFFSET = struct.unpack('<L', file.read(4))[0]
		file.seek(OFFSET)
		for i in range(0, FILES):
			NAME = file.read(128).strip(b"\x00").decode()
			OFFSET = struct.unpack('<L', file.read(4))[0]
			SIZE = struct.unpack('<L', file.read(4))[0]
			file.seek(68, 1)
			if options["singleFile"] and NAME.lower() == PGSR_NAME or not options["singleFile"] and (NAME.lower().startswith(options["pgsrStartswith"]) or options["pgsrStartswithIgnore"]) and (NAME.lower().endswith(options["pgsrEndswith"]) or options["pgsrEndswithIgnore"]):
				pathout_data = pgsr_patch_data(NAME, file, pathout_data, OFFSET)
	else:
		start_time = datetime.datetime.now()
		pathout_data = pgsr_patch_data(file, pathout, 0)
		
	open(pathout, "wb").write(pathout_data)
	print("\033[32mpatched %s in %s\033[0m" % (pathout, datetime.datetime.now() - start_time))
	input("\033[95m\033[1mPRESS [ENTER]\033[0m")
except BaseException as e:
	error_message('%s: %s' % (type(e).__name__, e))

fail.close()