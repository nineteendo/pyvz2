import zlib, os
options = {
	"DEBUG_MODE": False,
	"enteredPath": False
}

def error_message(string):
	if options["DEBUG_MODE"]:
		string = traceback.format_exc()
	
	fail.write(string + "\n")
	print("\33[91m%s\33[0m" % string)

def path_input(text):
	newstring = input(text)
	if options["enteredPath"]:
		return newstring
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
		
		return string

try:
	fail = open(os.path.join(sys.path[0], "fail.txt"), "w")
	if sys.version_info[0] < 3:
		raise RuntimeError("Must be using Python 3")
    
	print("\033[95m\033[1mOBBextracter v1.1.0\n(C) 2021 by Nineteendo\033[0m\n")
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
	filename = path_input("OBB/RSB=")
	for line in open(os.path.join(sys.path[0], "versions.cfg"), 'r').readlines():
		if not "#" in line and not ";" in line: 
			line = line.split(":")
			name = line[0]
			line = line[1].split(",")
			file_size = int(line[0])
			offset = int(line[1])
			packed_size = int(line[2])
			if os.path.getsize(filename) == file_size:
				compressed_file = open(filename, 'rb')
				compressed_file.read(offset)
				open(name + ".section", 'wb').write(zlib.decompress(compressed_file.read()))
				print("written " + name + ".section")
except BaseException as e:
	error_message('%s: %s' % (type(e).__name__, e))

fail.close()