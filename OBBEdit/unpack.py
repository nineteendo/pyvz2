# Import libraries
import datetime

from io import BytesIO
from json import load
from libraries.pyvz2rijndael import RijndaelCBC
from libraries.pyvz2rton import RTONDecoder
from os import makedirs, listdir, system, getcwd, sep
from os.path import isdir, isfile, realpath, join as osjoin, dirname, relpath, basename, splitext
#from PIL import Image
from struct import unpack
import sys
from traceback import format_exc
from zlib import decompress

options = {
# Default options
	# SMF options
	"smfExtensions": (
		".rsb.smf",
	),
	"smfPacked": "",
	"smfUnpacked": "",
	"smfUnpackLevel": 1,
	# RSB options
	"rsbExtensions": (
		".rsb.smf",
		
		".1bsr",
		".rsb1",
		".rsb",
		".obb"
	),
	"rsbPacked": "",
	"rsbPatched": "",
	"rsbUnpacked": "",
	"rsbUnpackLevel": 2,
	"rsgEndsWith": (),
	"rsgEndsWithIgnore": True,
	"rsgStartsWith": (
		"packages",
		"worldpackages_"
	),
	"rsgStartsWithIgnore": False,
	# RSG options
	"overrideDataCompression": 1,
	"overrideEncryption": 1,
	"overrideImageDataCompression": 1,
	"pathEndsWith": (
		".rton",
	),
	"pathEndsWithIgnore": False,
	"pathStartsWith": (
		"packages/",
	),
	"pathStartsWithIgnore": False,
	"rsgExtensions": (
		".rsb.smf",
		
		".1bsr",
		".rsb1",
		".rsb",
		".obb",
		
		".pgsr",
		".rsgp",
		".rsg",
		".rsg.smf"
	),
	"rsgPacked": "",
	"rsgPatched": "",
	"rsgUnpacked": "",
	"rsgUnpackLevel": 7,
	# Encryption options
	"encryptedExtensions": (
		".rton",
	),
	"encryptedPacked": "",
	"encryptedUnpacked": "",
	"encryptedUnpackLevel": 5,
	"encryptionKey": "00000000000000000000000000000000",
	# RTON options
	"comma": 0,
	"doublePoint": 1,
	"encodedPacked": "",
	"encodedUnpacked": "",
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
def path_input(text, preset):
# Input hybrid path
	if preset != "":
		print("\033[1m"+ text + "\033[0m: " + preset)
		return preset
	else:
		string = ""
		newstring = bold_input(text)
		while newstring or string == "":
			string = ""
			quoted = 0
			escaped = False
			temp_string = ""
			confirm = False
			for char in newstring:
				if escaped:
					if quoted != 1 and char == "'" or quoted != 2 and char == '"' or quoted == 0 and char in "\\ ":
						string += temp_string + char
						confirm = True
					else:
						string += temp_string + "\\" + char
					temp_string = ""
					escaped = False
				elif char == "\\":
					escaped = True
				elif quoted != 2 and char == "'":
					quoted = 1 - quoted
				elif quoted != 1 and char == '"':
					quoted = 2 - quoted
				elif quoted != 0 or char != " ":
					string += temp_string + char
					temp_string = ""
				else:
					temp_string += " "
			if string == "":
				newstring = bold_input("\033[91mEnter a path")
			else:
				newstring = ""
				string = realpath(string)
				if confirm:
					newstring = bold_input("Confirm \033[100m" + string)
		return string
# RSG Unpack functions
# def ARGB8888(file_data, WIDHT, HEIGHT):
# 	return Image.frombuffer("RGBA", (WIDHT, HEIGHT), file_data, "raw", "BGRA", 0, 1)
# def ABGR8888(file_data, WIDHT, HEIGHT):
# 	return Image.frombuffer("RGBA", (WIDHT, HEIGHT), file_data, "raw", "RGBA", 0, 1)
# def RGBA4444(file_data, WIDHT, HEIGHT):
# 	return Image.merge('RGBA', Image.frombuffer("RGBA", (WIDHT, HEIGHT), file_data, "raw", "RGBA;4B", 0, 1).split()[::-1])
# def RGB565(file_data, WIDHT, HEIGHT):
# 	return Image.frombuffer("RGB", (WIDHT, HEIGHT), file_data, "raw", "BGR;16", 0, 1)
# def RGBA5551(file_data, WIDHT, HEIGHT):
# 	img = Image.new('RGBA', (WIDHT, HEIGHT))
# 	index = 0
# 	for y in range(0, HEIGHT):
# 		for x in range(0, WIDHT):
# 			a = file_data[index]
# 			b = file_data[index + 1]
# 			img.putpixel((x,y), (b & 248, 36 * (b & 7) + (a & 192) // 8, 4 * (a & 62), 255 * (a & 1)))
# 			index += 2
# 	return img
# def RGBABlock32x32(image_decoder, file_data, WIDHT, HEIGHT):
# 	BLOCK_OFFSET = 0
# 	img = Image.new('RGBA', (WIDHT, HEIGHT))
# 	for y in range(0, HEIGHT, 32):
# 		for x in range(0, WIDHT, 32):
# 			img.paste(image_decoder(file_data[BLOCK_OFFSET: BLOCK_OFFSET + 2048], 32, 32), (x, y))
# 			BLOCK_OFFSET += 2048
# 	return img
# def RGBBlock32x32(image_decoder, file_data, WIDHT, HEIGHT):
# 	BLOCK_OFFSET = 0
# 	img = Image.new('RGB', (WIDHT, HEIGHT))
# 	for y in range(0, HEIGHT, 32):
# 		for x in range(0, WIDHT, 32):
# 			img.paste(image_decoder(file_data[BLOCK_OFFSET: BLOCK_OFFSET + 2048], 32, 32), (x, y))
# 			BLOCK_OFFSET += 2048
# 	return img
# rsb_image_decoders = {
# 	0: ARGB8888,
# 	1: RGBA4444,
# 	2: RGB565,
# 	3: RGBA5551,
	
# 	#5: DXT5,

# 	21: RGBA4444, # 32x32 block
# 	22: RGB565, # 32x32 block
# 	23: RGBA5551 # 32x32 block

# 	#30: PVRTC_4BPP_RGBA,
# 	#31: PVRTC_2BPP_RGBA,
# 	#32: ETC1_RGB,
# 	#33: ETC2_RGB,
# 	#34: ETC2_RGBA,
# 	#35: DXT1_RGB,
# 	#36: DXT3_RGBA,
# 	#37: DXT5_RGBA,
# 	#38: ATITC_RGB,
# 	#39: ATITC_RGBA,

# 	#147: ETC1_RGB_A8,
# 	#148: PVRTC_4BPP_RGB_A8,
# 	#149: XRGB8888_A8,
# 	#150: ETC1_RGB_A_Palette
# }
# obb_image_decoders = {
# 	0: ABGR8888,
# 	1: RGBA4444,
# 	2: RGB565,
# 	3: RGBA5551,
	
# 	#5: DXT5,

# 	21: RGBA4444, # 32x32 block
# 	22: RGB565, # 32x32 block
# 	23: RGBA5551 # 32x32 block

# 	#30: PVRTC_4BPP_RGBA,
# 	#31: PVRTC_2BPP_RGBA,
# 	#32: ETC1_RGB,
# 	#33: ETC2_RGB,
# 	#34: ETC2_RGBA,
# 	#35: DXT1_RGB,
# 	#36: DXT3_RGBA,
# 	#37: DXT5_RGBA,
# 	#38: ATITC_RGB,
# 	#39: ATITC_RGBA,

# 	#147: ETC1_RGB_A8,
# 	#148: PVRTC_4BPP_RGB_A8,
# 	#149: XRGB8888_A8,
# 	#150: ETC1_RGB_A_Palette
# }
#def rsgp_extract(RSG_NAME, RSG_OFFSET, IMAGE_FORMATS, image_decoders, file, out, pathout, level):
def rsgp_extract(RSG_NAME, RSG_OFFSET, file, out, pathout, level):
	if file.read(4) == b"pgsr":
		try:
			VERSION = unpack("<I", file.read(4))[0]
			
			file.seek(8, 1)
			COMPRESSION_FLAGS = unpack("<I", file.read(4))[0]
			HEADER_LENGTH = unpack("<I", file.read(4))[0]

			DATA_OFFSET = unpack("<I", file.read(4))[0]
			COMPRESSED_DATA_SIZE = unpack("<I", file.read(4))[0]
			DECOMPRESSED_DATA_SIZE = unpack("<I", file.read(4))[0]
			
			file.seek(4, 1)
			IMAGE_DATA_OFFSET = unpack("<I", file.read(4))[0]
			COMPRESSED_IMAGE_DATA_SIZE = unpack("<I", file.read(4))[0]
			DECOMPRESSED_IMAGE_DATA_SIZE = unpack("<I", file.read(4))[0]
			
			file.seek(20, 1)
			INFO_SIZE = unpack("<I", file.read(4))[0]
			INFO_OFFSET = RSG_OFFSET + unpack("<I", file.read(4))[0]
			INFO_LIMIT = INFO_OFFSET + INFO_SIZE
			
			file.seek(RSG_OFFSET + DATA_OFFSET)
			if COMPRESSION_FLAGS & 2 == 0: # Decompressed files
				data = file.read(COMPRESSED_DATA_SIZE)
			elif COMPRESSED_DATA_SIZE != 0: # Compressed files
				blue_print("Decompressing...")
				data = decompress(file.read(COMPRESSED_DATA_SIZE))
				
			if DECOMPRESSED_IMAGE_DATA_SIZE != 0:
				file.seek(RSG_OFFSET + IMAGE_DATA_OFFSET)
				if COMPRESSION_FLAGS & 1 == 0: # Decompressed files
					image_data = file.read(COMPRESSED_IMAGE_DATA_SIZE)
				else: # Compressed files
					blue_print("Decompressing...")
					image_data = decompress(file.read(COMPRESSED_IMAGE_DATA_SIZE))
			
			if level < 5:
				if COMPRESSION_FLAGS & 2 == 0 or COMPRESSED_DATA_SIZE != 0:
					file_path = osjoin(out, RSG_NAME + ".section")
					open(file_path, "wb").write(data)
					print("wrote " + relpath(file_path, pathout))
				if DECOMPRESSED_IMAGE_DATA_SIZE != 0:
					image_path = osjoin(out, RSG_NAME + ".section2")
					open(image_path, "wb").write(image_data)
					print("wrote " + relpath(image_path, pathout))
			else:
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
					while BYTE != b"\0":
						FILE_NAME += BYTE
						BYTE = file.read(1)
						LENGTH = 4 * unpack("<I", file.read(3) + b"\0")[0]
						if LENGTH != 0:
							NAME_DICT[FILE_NAME] = LENGTH
					
					DECODED_NAME = FILE_NAME.decode().replace("\\", sep)
					NAME_CHECK = DECODED_NAME.replace("\\", "/").lower()
					IS_IMAGE = unpack("<I", file.read(4))[0] == 1
					FILE_OFFSET = unpack("<I", file.read(4))[0]
					FILE_SIZE = unpack("<I", file.read(4))[0]
					if IS_IMAGE:
						file.seek(20, 1)
						#IMAGE_ENTRY = unpack("<I", file.read(4))[0]
						#file.seek(8, 1)
						#WIDHT = unpack("<I", file.read(4))[0]
						#HEIGHT = unpack("<I", file.read(4))[0]
					if DECODED_NAME and NAME_CHECK.startswith(pathStartsWith) and NAME_CHECK.endswith(pathEndsWith):
						if IS_IMAGE:
							file_data = image_data[FILE_OFFSET: FILE_OFFSET + FILE_SIZE]
						else:
							file_data = data[FILE_OFFSET: FILE_OFFSET + FILE_SIZE]
						
						if NAME_CHECK[-5:] == ".rton" and file_data[:2] == b"\x10\0" and 5 < level:
							file_data = rijndael_cbc.decrypt(file_data[2:])

						if level < 7:
							if NAME_CHECK[-5:] == ".rton" and 6 == level and file_data[:4] != b"RTON":
								warning_message("No RTON " + file.name + ":" + RSG_NAME + ":" + DECODED_NAME)
							else:
								file_path = osjoin(out, DECODED_NAME)
								makedirs(dirname(file_path), exist_ok = True)
								open(file_path, "wb").write(file_data)
								print("wrote " + relpath(file_path, pathout))
						elif NAME_CHECK[-5:] == ".rton":
							try:
								jfn = osjoin(out, DECODED_NAME[:-5] + ".JSON")
								makedirs(dirname(jfn), exist_ok = True)
								source = BytesIO(file_data)
								source.name = file.name + ":" + RSG_NAME + ":" + DECODED_NAME
								if source.read(4) == b"RTON":
									json_data = root_object(source, current_indent)
									open(jfn, "wb").write(json_data)
									print("wrote " + relpath(jfn, pathout))
								else:
									warning_message("No RTON " + source.name)
							except Exception as e:
								error_message(type(e).__name__ + " in " + file.name + ": " + RSG_NAME + ":" + DECODED_NAME + " pos " + str(source.tell() - 1) + ": " + str(e))
						# elif IS_IMAGE:
						# 	try:
						# 		file_path = osjoin(out, splitext(DECODED_NAME)[0] + ".PNG")
						# 		makedirs(dirname(file_path), exist_ok = True)
						# 		IMAGE_FORMAT = IMAGE_FORMATS[IMAGE_ENTRY]
						# 		if IMAGE_FORMAT in [0, 1, 2, 3]: # Single Image
						# 			image_decoders[IMAGE_FORMAT](file_data, WIDHT, HEIGHT).save(file_path)
						# 			print("wrote " + relpath(file_path, pathout))
						# 		elif IMAGE_FORMAT in [21, 23]: # 32x32 RGBABlock
						# 			RGBABlock32x32(image_decoders[21], file_data, WIDHT, HEIGHT).save(file_path)
						# 			print("wrote " + relpath(file_path, pathout))
						# 		elif IMAGE_FORMAT == 22: # 32x32 RGBBlock
						# 			RGBBlock32x32(image_decoders[IMAGE_FORMAT], file_data, WIDHT, HEIGHT).save(file_path)
						# 			print("wrote " + relpath(file_path, pathout))
						# 	except Exception as e:
						# 		error_message(type(e).__name__ + " in " + file.name + RSG_NAME + ": " + DECODED_NAME + ": " + str(e))
					temp = file.tell()
		except Exception as e:
			error_message(type(e).__name__ + " while extracting " + file.name + ":" + RSG_NAME + str(e))

#def rsb_extract(file, out, level, image_decoders, pathout):
def rsb_extract(file, out, level, pathout):
	VERSION = unpack('<L', file.read(4))[0]

	file.seek(4, 1)
	DIRECTORY_10_OFFSET = unpack('<L', file.read(4))[0]

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

	# TEXTURE_FORMATS = []
	# file.seek(DIRECTORY_6_OFFSET)
	# for IMAGE_ID in range(0, DIRECTORY_6_ENTRIES):
	# 	WIDHT = unpack("<I", file.read(4))[0]
	# 	HEIGHT = unpack("<I", file.read(4))[0]
	# 	WIDHT_BYTES = unpack("<I", file.read(4))[0]
	# 	TEXTURE_FORMAT = unpack("<I", file.read(4))[0]
	# 	if DIRECTORY_6_ENTRY_SIZE == 24:
	# 		COMPRESSED_IMAGE_SIZE = unpack("<I", file.read(4))[0]
	# 		HUNDRED = unpack("<I", file.read(4))[0]

	# 	TEXTURE_FORMATS.append(TEXTURE_FORMAT)

	file.seek(DIRECTORY_4_OFFSET)
	for i in range(0, DIRECTORY_4_ENTRIES):
		RSG_NAME = file.read(128).strip(b"\0").decode()
		RSG_CHECK = RSG_NAME.lower()
		RSG_OFFSET = unpack("<I", file.read(4))[0]
		RSG_LENGTH = unpack("<I", file.read(4))[0]
		
		RSG_ID = unpack("<I", file.read(4))[0]

		COMPRESSION_FLAGS = unpack("<I", file.read(4))[0]
		HEADER_LENGTH = unpack("<I", file.read(4))[0]

		DATA_OFFSET = unpack("<I", file.read(4))[0]
		COMPRESSED_DATA_SIZE = unpack("<I", file.read(4))[0]
		DECOMPRESSED_DATA_SIZE = unpack("<I", file.read(4))[0]
		DECOMPRESSED_DATA_SIZE_B = unpack("<I", file.read(4))[0]
		
		IMAGE_DATA_OFFSET = unpack("<I", file.read(4))[0]
		COMPRESSED_IMAGE_DATA_SIZE = unpack("<I", file.read(4))[0]
		DECOMPRESSED_IMAGE_DATA_SIZE = unpack("<I", file.read(4))[0]

		file.seek(20, 1)
		IMAGE_ENTRIES = unpack("<I", file.read(4))[0]
		IMAGE_ID = unpack("<I", file.read(4))[0]
		if RSG_CHECK.startswith(rsgStartsWith) and RSG_CHECK.endswith(rsgEndsWith):
			temp = file.tell()
			file.seek(RSG_OFFSET)
			if level < 4:
				open(osjoin(out, RSG_NAME + ".rsg"), "wb").write(file.read(RSG_LENGTH))
				print("wrote " + relpath(osjoin(out, RSG_NAME + ".rsg"), pathout))
			else:
				rsgp_extract(RSG_NAME, RSG_OFFSET, file, out, pathout, level)
				#rsgp_extract(RSG_NAME, RSG_OFFSET, TEXTURE_FORMATS[IMAGE_ID:IMAGE_ID + IMAGE_ENTRIES], image_decoders, file, out, pathout, level)
			file.seek(temp)
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
			HEADER = file.read(4)
			if HEADER == b"\xD4\xFE\xAD\xDE":
				DECOMPRESSED_SIZE = unpack("<I", file.read(4))[0]
				data = decompress(file.read())
				if level < 3:
					open(out, "wb").write(data)
					print("wrote " + relpath(out, pathout))
				else:
					file = BytesIO(data)
					file.name = inp
					HEADER = file.read(4)
			if HEADER == b"1bsr":
				# if file.[-4:] == ".obb":
				# 	image_decoders = obb_image_decoders
				# else:
				# 	image_decoders = rsb_image_decoders

				makedirs(out, exist_ok = True)
				rsb_extract(file, out, level, pathout)
				#rsb_extract(file, out, level, image_decoders, pathout)
			elif HEADER == b"pgsr":
				makedirs(out, exist_ok = True)
				file.seek(0)
				rsgp_extract("data", 0, file, out, pathout, level)
				#rsgp_extract("data", 0, [], {} file, out, pathout, level)
		except Exception as e:
			error_message("Failed OBBUnpack: " + type(e).__name__ + " in " + inp + " pos " + str(file.tell()) + ": " + str(e))
def conversion(inp, out, pathout, extensions, noextensions):
# Recursive file convert function
	check = inp.lower()
	if isfile(inp) and (check.endswith(extensions) or basename(check).startswith(noextensions)):
		try:
			file = open(inp, "rb")
			HEADER = file.read(2)
			if HEADER == b"\x10\0":
				open(out,"wb").write(rijndael_cbc.decrypt(file.read()))
				print("wrote " + relpath(out, pathout))
			elif HEADER == b"RT" and file.read(2) == b"ON":
				if out.lower()[-5:] == ".rton":
					out = out[:-5]
				out += ".json"
				data = root_object(file, current_indent)
				open(out, "wb").write(data)
				print("wrote " + relpath(out, pathout))
			elif check[-5:] != ".json":
				warning_message("No RTON " + inp)
		except Exception as e:
			error_message(type(e).__name__ + " in " + inp + " pos " + str(file.tell() -1) + ": " + str(e))
	elif isdir(inp):
		makedirs(out, exist_ok = True)
		for entry in listdir(inp):
			input_file = osjoin(inp, entry)
			if isfile(input_file) or input_file != pathout:
				conversion(input_file, osjoin(out, entry), pathout, extensions, noextensions)
def list_levels(levels):
	blue_print(" ".join([repr(i) + "-" + levels[i] for i in range(len(levels))]))
def input_level(text, minimum, maximum):
# Set input level for conversion
	try:
		return max(minimum, min(maximum, int(bold_input(text + " (" + str(minimum) + "-" + str(maximum) + ")"))))
	except Exception as e:
		error_message(type(e).__name__ + " : " + str(e))
		warning_message("Defaulting to " + str(minimum))
		return minimum
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
	
	print("\033[95m\033[1mOBBUnpacker v1.1.6b (C) 2022 by Nineteendo\nCode based on: Luigi Auriemma, Small Pea & 1Zulu\nDocumentation: Watto Studios, YingFengTingYu & h3x4n1um\033[0m\n")
	try:
		folder = osjoin(application_path, "options")
		templates = {}
		blue_print("\033[1mTEMPLATES:\033[0m")
		for entry in sorted(listdir(folder)):
			if isfile(osjoin(folder, entry)):
				file, extension = splitext(entry)
				if extension == ".json" and entry.count("--") == 2:
					key, unpack_name, patch_name = file.split("--")
					if not key in templates:
						blue_print("\033[1m" + key + "\033[0m: " + unpack_name)
						templates[key] = unpack_name + "--" + patch_name + ".json"
				elif entry.count("--") > 0:
					print("--".join(file.split("--")[1:]))
		length = len(templates)
		if length == 0:
			green_print("Loaded default template")
		else:
			if length > 1:
				key = bold_input("Choose template")
			
			name = key + "--" + templates[key]
			newoptions = load(open(osjoin(folder, name), "rb"))
			for key in options:
				if key in newoptions and newoptions[key] != options[key]:
					if type(options[key]) == type(newoptions[key]):
						options[key] = newoptions[key]
					elif isinstance(options[key], tuple) and isinstance(newoptions[key], list):
						options[key] = tuple([str(i).lower() for i in newoptions[key]])
					elif key == "indent" and newoptions[key] == None:
						options[key] = newoptions[key]
			green_print("Loaded template " + name)
	except Exception as e:
		error_message(type(e).__name__ + " while loading options: " + str(e))
		warning_message("Falling back to default options.")
	
	level_to_name = ["SPECIFY", "SMF", "RSB", "RSG", "SECTION", "ENCRYPTED", "ENCODED", "DECODED"]
	if options["smfUnpackLevel"] <= 0 or options["rsbUnpackLevel"] <= 1 or options["rsgUnpackLevel"] <= 2 or options["encryptedUnpackLevel"] <= 4 or options["encodedUnpackLevel"] <= 5:
		list_levels(level_to_name)
	if options["smfUnpackLevel"] <= 0:
		options["smfUnpackLevel"] = input_level("SMF Unpack Level", 1, 2)
	if options["rsbUnpackLevel"] <= 1:
		options["rsbUnpackLevel"] = input_level("RSB/SMF Unpack Level", 2, 3)
	if options["rsgUnpackLevel"] <= 2:
		options["rsgUnpackLevel"] = input_level("RSG/RSB/SMF Unpack Level", 3, 7)
	if options["encryptedUnpackLevel"] <= 4:
		options["encryptedUnpackLevel"] = input_level("ENCRYPTED Unpack Level", 5, 6)
	if options["encodedUnpackLevel"] <= 5:
		options["encodedUnpackLevel"] = input_level("ENCODED Unpack Level", 6, 7)

	if options["rsgStartsWithIgnore"]:
		rsgStartsWith = ""
	else:
		rsgStartsWith = options["rsgStartsWith"]
	if options["rsgEndsWithIgnore"]:
		rsgEndsWith = ""
	else:
		rsgEndsWith = options["rsgEndsWith"]

	rijndael_cbc = RijndaelCBC(str.encode(options["encryptionKey"]), 24)
	if options["pathEndsWithIgnore"]:
		pathEndsWith = ""
	else:
		pathEndsWith = options["pathEndsWith"]
	if options["pathStartsWithIgnore"]:
		pathStartsWith = ""
	else:
		pathStartsWith = options["pathStartsWith"]

	if options["comma"] > 0:
		comma = b"," + b" " * options["comma"]
	else:
		comma = b","
	if options["doublePoint"] > 0:
		doublePoint = b":" + b" " * options["doublePoint"]
	else:
		doublePoint = b":"
	if options["indent"] == None:
		indent = current_indent = b""
	elif options["indent"] < 0:
		current_indent = b"\r\n"
		indent = b"\t"
	else:
		current_indent = b"\r\n"
		indent = b" " * options["indent"]
	ensureAscii = options["ensureAscii"]
	repairFiles = options["repairFiles"]
	sortKeys = options["sortKeys"]
	sortValues = options["sortValues"]
	root_object = RTONDecoder(comma, doublePoint, ensureAscii, fail, indent, repairFiles, sortKeys, sortValues).root_object
	
	blue_print("Working directory: " + getcwd())
	if 2 >= options["smfUnpackLevel"] > 1:
		smf_input = path_input("SMF Input file or directory", options["smfPacked"])
		if isfile(smf_input):
			smf_output = path_input("SMF " + level_to_name[options["smfUnpackLevel"]] + " Output file", options["smfUnpacked"])
		else:
			smf_output = path_input("SMF " + level_to_name[options["smfUnpackLevel"]] + " Output directory", options["smfUnpacked"])
	if 3 >= options["rsbUnpackLevel"] > 2:
		rsb_input = path_input("RSB/SMF Input file or directory", options["rsbPacked"])
		rsb_output = path_input("RSB/SMF " + level_to_name[options["rsbUnpackLevel"]] + " Output directory", options["rsbUnpacked"])
	if 7 >= options["rsgUnpackLevel"] > 3:
		rsg_input = path_input("RSG/RSB/SMF Input file or directory", options["rsgPacked"])
		rsg_output = path_input("RSG/RSB/SMF " + level_to_name[options["rsgUnpackLevel"]] + " Output directory", options["rsgUnpacked"])
	if 6 >= options["encryptedUnpackLevel"] > 5:
		encrypted_input = path_input("ENCRYPTED Input file or directory", options["encryptedPacked"])
		if isfile(encrypted_input):
			encrypted_output = path_input("ENCRYPTED " + level_to_name[options["encryptedUnpackLevel"]] + " Output file", options["encryptedUnpacked"])
		else:
			encrypted_output = path_input("ENCRYPTED " + level_to_name[options["encryptedUnpackLevel"]] + " Output directory", options["encryptedUnpacked"])
	if 7 >= options["encodedUnpackLevel"] > 6:
		encoded_input = path_input("ENCODED Input file or directory", options["encodedPacked"])
		if isfile(encoded_input):
			encoded_output = path_input("ENCODED " + level_to_name[options["encodedUnpackLevel"]] + " Output file", options["encodedUnpacked"])
			if encoded_output.lower()[:-5] == ".json":
				encoded_output = encoded_output[:-5]
		else:
			encoded_output = path_input("ENCODED " + level_to_name[options["encodedUnpackLevel"]] + " Output directory", options["encodedUnpacked"])

	# Start file_to_folder
	start_time = datetime.datetime.now()
	if 2 >= options["smfUnpackLevel"] > 1:
		file_to_folder(smf_input, smf_output, options["smfUnpackLevel"], options["smfExtensions"], dirname(smf_output))
	if 3 >= options["rsbUnpackLevel"] > 2:
		file_to_folder(rsb_input, rsb_output, options["rsbUnpackLevel"], options["rsbExtensions"], rsb_output)
	if 7 >= options["rsgUnpackLevel"] > 3:
		file_to_folder(rsg_input, rsg_output, options["rsgUnpackLevel"], options["rsgExtensions"], rsg_output)
	if 6 >= options["encryptedUnpackLevel"] > 5:
		conversion(encrypted_input, encrypted_output, dirname(encrypted_output), options["encryptedExtensions"], ())
	if 7 >= options["encodedUnpackLevel"] > 6:
		conversion(encoded_input, encoded_output, dirname(encoded_output), options["RTONExtensions"], options["RTONNoExtensions"])

	green_print("finished unpacking in " + str(datetime.datetime.now() - start_time))
	if fail.tell() > 0:
		print("\33[93mErrors occured, check: " + fail.name + "\33[0m")
	bold_input("\033[95mPRESS [ENTER]")
except Exception as e:
	error_message(type(e).__name__ + " : " + str(e))
except BaseException as e:
	warning_message(type(e).__name__ + " : " + str(e))
fail.close() # Close log