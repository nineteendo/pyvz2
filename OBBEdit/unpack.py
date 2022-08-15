# Standard libraries
from io import BytesIO
from os import listdir, getcwd, makedirs, sep
from os.path import exists, isdir, isfile, join as osjoin, dirname, splitext
#from PIL import Image
from struct import unpack
from zipfile import ZipFile
from zlib import decompress

# 3th party libraries
from libraries.pyvz2nineteendo import LogError, blue_print, path_input, list_levels
from libraries.pyvz2rijndael import RijndaelCBC
from libraries.pyvz2rton import RTONDecoder

options = {
# Default options
	# ZIP options
	"archiveExtensions": (
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
	"encodedExtensions": (
		".rton",
	),
	"zipExtensions": (
		".apk",
		".zip"
	),
	"zipPacked": "",
	"zipUnpacked": "",
	"zipUnpackLevel": 1,
	# SMF options
	"smfExtensions": (
		".apk",
		".zip",

		".rsb.smf",
	),
	"smfPacked": "",
	"smfUnpacked": "",
	"smfUnpackLevel": 2,
	# RSB options
	"rsbExtensions": (
		".apk",
		".zip",

		".rsb.smf",
		
		".1bsr",
		".rsb1",
		".rsb",
		".obb"
	),
	"rsbPacked": "",
	"rsbPatched": "",
	"rsbUnpacked": "",
	"rsbUnpackLevel": 3,
	"rsgEndsWith": (),
	"rsgEndsWithIgnore": True,
	"rsgStartsWith": (
		"packages",
		"worldpackages_"
	),
	"rsgStartsWithIgnore": False,
	# RSG options
	"overrideDataCompression": 1,
	"overrideEncryption": 2,
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
		".apk",
		".zip",
		
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
	"rsgUnpackLevel": 8,
	# Encryption options
	"encryptedExtensions": (
		".rton",
	),
	"encryptedPacked": "",
	"encryptedUnpacked": "",
	"encryptedUnpackLevel": 6,
	"encryptionKey": "00000000000000000000000000000000",
	# RTON options
	"comma": 0,
	"doublePoint": 1,
	"encodedPacked": "",
	"encodedUnpacked": "",
	"encodedUnpackLevel": 7,
	"ensureAscii": False,
	"indent": 4,
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
		"global_save_data",
		"local_profiles",
		"loot",
		"_saveheader_rton"
	),
	"sortKeys": False,
	"sortValues": False
}
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
#def rsg_extract(RSG_NAME, RSG_OFFSET, IMAGE_FORMATS, image_decoders, file, out, pathout, unpack_level):
def rsg_extract(RSG_NAME, file, pathout_data, out, unpack_level):
	try:
		HEADER = file.read(4)
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
		INFO_OFFSET = unpack("<I", file.read(4))[0]
		INFO_LIMIT = INFO_OFFSET + INFO_SIZE
		
		if COMPRESSION_FLAGS & 2 == 0: # Decompressed files
			data = bytearray(pathout_data[DATA_OFFSET: DATA_OFFSET + COMPRESSED_DATA_SIZE])
		elif COMPRESSED_DATA_SIZE != 0: # Compressed files
			data = bytearray(decompress(pathout_data[DATA_OFFSET: DATA_OFFSET + COMPRESSED_DATA_SIZE]))
			
		if DECOMPRESSED_IMAGE_DATA_SIZE != 0:
			file.seek(IMAGE_DATA_OFFSET)
			if COMPRESSION_FLAGS & 1 == 0: # Decompressed files
				image_data = bytearray(pathout_data[IMAGE_DATA_OFFSET: IMAGE_DATA_OFFSET + COMPRESSED_IMAGE_DATA_SIZE])
			else: # Compressed files
				image_data = bytearray(decompress(pathout_data[IMAGE_DATA_OFFSET: IMAGE_DATA_OFFSET + COMPRESSED_IMAGE_DATA_SIZE]))
		
		if unpack_level < 6:
			if COMPRESSION_FLAGS & 2 == 0 or COMPRESSED_DATA_SIZE != 0:
				file_path = osjoin(out, RSG_NAME + ".section")
				open(file_path, "wb").write(data)
			if DECOMPRESSED_IMAGE_DATA_SIZE != 0:
				image_path = osjoin(out, RSG_NAME + ".section2")
				open(image_path, "wb").write(image_data)
		else:
			DATA_DICT = {}
			IMAGE_DATA_DICT = {}
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
				IS_IMAGE = unpack("<I", file.read(4))[0] == 1
				FILE_OFFSET = unpack("<I", file.read(4))[0]
				FILE_SIZE = unpack("<I", file.read(4))[0]
				if IS_IMAGE:
					file.seek(20, 1)
					#IMAGE_ENTRY = unpack("<I", file.read(4))[0]
					#file.seek(8, 1)
					#WIDHT = unpack("<I", file.read(4))[0]
					#HEIGHT = unpack("<I", file.read(4))[0]
					temp = file.tell()
					IMAGE_DATA_DICT[DECODED_NAME] = {
						"FILE_OFFSET": FILE_OFFSET,
						"FILE_SIZE": FILE_SIZE
					}
				else:
					temp = file.tell()
					DATA_DICT[DECODED_NAME] = {
						"FILE_OFFSET": FILE_OFFSET,
						"FILE_SIZE": FILE_SIZE
					}
				temp = file.tell()

			split_task(len(DATA_DICT) + len(IMAGE_DATA_DICT))
			for DECODED_NAME in DATA_DICT:
				NAME_CHECK = DECODED_NAME.replace("\\", "/").lower()
				if NAME_CHECK.startswith(pathStartsWith) and NAME_CHECK.endswith(pathEndsWith):
					FILE_OFFSET = DATA_DICT[DECODED_NAME]["FILE_OFFSET"]
					FILE_SIZE = DATA_DICT[DECODED_NAME]["FILE_SIZE"]
					file_data = data[FILE_OFFSET: FILE_OFFSET + FILE_SIZE]
					
					if NAME_CHECK[-5:] == ".rton" and file_data[:2] == b"\x10\0" and 6 < unpack_level:
						file_data = rijndael_cbc.decrypt(file_data[2:])

					if NAME_CHECK[-5:] == ".rton" and 7 <= unpack_level and file_data[:4] != b"RTON":
						warning_message("No RTON " + file.name + ":" + DECODED_NAME)
					else:
						file_path = osjoin(out, DECODED_NAME)
						makedirs(dirname(file_path), exist_ok = True)
						if unpack_level > 7:
							if NAME_CHECK[-5:] == ".rton":
								try:
									file_path = osjoin(out, DECODED_NAME[:-5] + ".JSON")
									source = BytesIO(file_data)
									source.name = file.name + ":" + DECODED_NAME
									RTON_HEADER = source.read(4)
									file_data = parse_root_object(source)
									open(file_path, "wb").write(file_data)
								except Exception as e:
									error_message(e, " in " + file.name + ": " + RSG_NAME + ":" + DECODED_NAME + " pos: " + repr(source.tell()))
							else:
								open(file_path, "wb").write(file_data)
						else:
							open(file_path, "wb").write(file_data)
				finish_sub_task()
			for DECODED_NAME in IMAGE_DATA_DICT:
				NAME_CHECK = DECODED_NAME.replace("\\", "/").lower()
				if NAME_CHECK.startswith(pathStartsWith) and NAME_CHECK.endswith(pathEndsWith):
					FILE_OFFSET = IMAGE_DATA_DICT[DECODED_NAME]["FILE_OFFSET"]
					FILE_SIZE = IMAGE_DATA_DICT[DECODED_NAME]["FILE_SIZE"]
					file_data = image_data[FILE_OFFSET: FILE_OFFSET + FILE_SIZE]

					file_path = osjoin(out, DECODED_NAME)
					makedirs(dirname(file_path), exist_ok = True)
					# try:
					# 	file_path = osjoin(out, splitext(DECODED_NAME)[0] + ".PNG")
					# 	IMAGE_FORMAT = IMAGE_FORMATS[IMAGE_ENTRY]
					# 	if IMAGE_FORMAT in [0, 1, 2, 3]: # Single Image
					# 		image_decoders[IMAGE_FORMAT](file_data, WIDHT, HEIGHT).save(file_path)
					# 		print("wrote " + relpath(file_path, pathout))
					# 	elif IMAGE_FORMAT in [21, 23]: # 32x32 RGBABlock
					# 		RGBABlock32x32(image_decoders[21], file_data, WIDHT, HEIGHT).save(file_path)
					# 		print("wrote " + relpath(file_path, pathout))
					# 	elif IMAGE_FORMAT == 22: # 32x32 RGBBlock
					# 		RGBBlock32x32(image_decoders[IMAGE_FORMAT], file_data, WIDHT, HEIGHT).save(file_path)
					# 		print("wrote " + relpath(file_path, pathout)
					# 	except Exception as e:
					# 		error_message(type(e).__name__ + " in " + file.name + ": " + RSG_NAME + ":" + DECODED_NAME + ": " + str(e))
					open(file_path, "wb").write(file_data)
				finish_sub_task()
			merge_task()
	except Exception as e:
		error_message(e, " while extracting " + file.name)

#def rsb_extract(file, out, unpack_level, image_decoders, pathout):
def rsb_extract(file, pathout_data, out, unpack_level):
	VERSION = unpack('<L', file.read(4))[0]

	file.seek(4, 1)
	HEADER_SIZE = unpack('<L', file.read(4))[0]

	FILE_LIST_SIZE = unpack('<L', file.read(4))[0]
	FILE_LIST_OFFSET = unpack('<L', file.read(4))[0]

	file.seek(8, 1)
	SUBGROUP_LIST_SIZE = unpack('<L', file.read(4))[0]
	SUBGROUP_LIST_OFFSET = unpack('<L', file.read(4))[0]
	SUBGROUP_INFO_ENTRIES = unpack("<I", file.read(4))[0]
	SUBGROUP_INFO_OFFSET = unpack("<I", file.read(4))[0]
	SUBGROUP_INFO_ENTRY_SIZE = unpack('<L', file.read(4))[0]

	GROUP_INFO_ENTRIES = unpack('<L', file.read(4))[0]
	GROUP_INFO_OFFSET = unpack('<L', file.read(4))[0]
	GROUP_INFO_ENTRY_SIZE = unpack('<L', file.read(4))[0]

	GROUP_LIST_SIZE = unpack('<L', file.read(4))[0]
	GROUP_LIST_OFFSET = unpack('<L', file.read(4))[0]

	AUTOPOOL_INFO_ENTRIES = unpack('<L', file.read(4))[0]
	AUTOPOOL_INFO_OFFSET = unpack('<L', file.read(4))[0]
	AUTOPOOL_INFO_ENTRY_SIZE = unpack('<L', file.read(4))[0]

	PTX_INFO_ENTRIES = unpack('<L', file.read(4))[0]
	PTX_INFO_OFFSET = unpack('<L', file.read(4))[0]
	PTX_INFO_ENTRY_SIZE = unpack('<L', file.read(4))[0]

	DIRECTORY_7_OFFSET = unpack('<L', file.read(4))[0]
	DIRECTORY_8_OFFSET = unpack('<L', file.read(4))[0]
	DIRECTORY_9_OFFSET = unpack('<L', file.read(4))[0]

	if VERSION == 4:
		HEADER_SIZE_2 = unpack('<L', file.read(4))[0]

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

	file.seek(SUBGROUP_INFO_OFFSET)
	split_task(SUBGROUP_INFO_ENTRIES)
	for i in range(0, SUBGROUP_INFO_ENTRIES):
		info_start = file.tell()
		RSG_NAME = file.read(128).strip(b"\0").decode()
		RSG_OFFSET = unpack("<I", file.read(4))[0]
		RSG_SIZE = unpack("<I", file.read(4))[0]
		SUBGROUP_ID = unpack("<I", file.read(4))[0]

		RSG_COMPRESSION_FLAGS = unpack("<I", file.read(4))[0]
		RSG_HEADER_LENGTH = unpack("<I", file.read(4))[0]

		RSG_DATA_OFFSET = unpack("<I", file.read(4))[0]
		RSG_COMPRESSED_DATA_SIZE = unpack("<I", file.read(4))[0]
		RSG_DECOMPRESSED_DATA_SIZE = unpack("<I", file.read(4))[0]
		RSG_DECOMPRESSED_DATA_SIZE_B = unpack("<I", file.read(4))[0]
		
		RSG_IMAGE_DATA_OFFSET = unpack("<I", file.read(4))[0]
		RSG_COMPRESSED_IMAGE_DATA_SIZE = unpack("<I", file.read(4))[0]
		RSG_DECOMPRESSED_IMAGE_DATA_SIZE = unpack("<I", file.read(4))[0]

		file.seek(20, 1)
		IMAGE_ENTRIES = unpack("<I", file.read(4))[0]
		IMAGE_ID = unpack("<I", file.read(4))[0]
		
		RSG_CHECK = RSG_NAME.lower()
		RSG_SIZE = max(RSG_DATA_OFFSET + RSG_COMPRESSED_DATA_SIZE, RSG_IMAGE_DATA_OFFSET + RSG_COMPRESSED_IMAGE_DATA_SIZE)
		if RSG_CHECK.startswith(rsgStartsWith) and RSG_CHECK.endswith(rsgEndsWith):
			subdata = pathout_data[RSG_OFFSET: RSG_OFFSET + RSG_SIZE]
			subdata[:4] = b"pgsr"
			subdata[16:36] = pathout_data[info_start + 140:info_start + 160]
			subdata[40:52] = pathout_data[info_start + 164:info_start + 176]
			if unpack_level < 5:
				open(osjoin(out, RSG_NAME + ".rsg"), "wb").write(subdata)
			else:
				subfile = BytesIO(subdata)
				subfile.name = file.name + ":" + RSG_NAME
				rsg_extract(RSG_NAME, subfile, subdata, out, unpack_level)
				#rsg_extract(RSG_NAME, RSG_OFFSET, TEXTURE_FORMATS[IMAGE_ID:IMAGE_ID + IMAGE_ENTRIES], image_decoders, file, out, pathout, unpack_level)
		finish_sub_task()
	merge_task()
def archive_extract(file, out, unpack_level, allow_copy):
	HEADER = file.read(4)
	COMPRESSED = HEADER == b"\xD4\xFE\xAD\xDE"
	if COMPRESSED:
		if unpack_level > 2:
			DECOMPRESSED_SIZE = unpack("<I", file.read(4))[0]
			pathout_data = decompress(file.read())
			if unpack_level > 3:
				name = file.name
				file = BytesIO(pathout_data)
				file.name = name
				HEADER = file.read(4)
			else:
				open(out, "wb").write(pathout_data)
		elif allow_copy:
			open(out, "wb").write(HEADER + file.read())
	if HEADER == b"1bsr":
		if unpack_level > 3:
			if not COMPRESSED:
				pathout_data = HEADER + file.read()
				file.seek(4)
			
			# if file.[-4:] == ".obb":
			# 	image_decoders = obb_image_decoders
			# else:
			# 	image_decoders = rsb_image_decoders
			makedirs(out, exist_ok = True)
			rsb_extract(file, bytearray(pathout_data), out, unpack_level)
			#rsb_extract(file, out, unpack_level, image_decoders, pathout)
		elif allow_copy:
			open(out, "wb").write(HEADER + file.read())
	elif HEADER == b"pgsr":
		if unpack_level > 4:
			pathout_data = HEADER + file.read()
			file.seek(0)
			makedirs(out, exist_ok = True)
			rsg_extract("data", file, pathout_data, out, unpack_level)
			#rsg_extract("data", 0, [], {} file, out, pathout, unpack_level)
		elif allow_copy:
			open(out, "wb").write(HEADER + file.read())
	elif not COMPRESSED:
		warning_message("UNKNOWN HEADER (" + HEADER.hex() + ") in " + file.name)
def file_decode(file, out, unpack_level, allow_copy):
	HEADER = file.read(2)
	ENCRYPTED = HEADER == b"\x10\0"
	if ENCRYPTED:
		if unpack_level > 6:
			file_data = rijndael_cbc.decrypt(file.read())
			if file_data[:4] != b"RTON":
				warning_message("No RTON " + file.name)
			elif unpack_level > 7:
				name = file.name
				file = BytesIO(file_data)
				file.name = name
				HEADER = file.read(4)
			else:
				open(out,"wb").write(file_data)
		elif allow_copy:
			open(out, "wb").write(HEADER + file.read())
	else:
		HEADER += file.read(2)

	if HEADER == b"RTON":
		if unpack_level > 7:
			data = parse_root_object(file)
			open(out, "wb").write(data)
		elif allow_copy:
			open(out, "wb").write(HEADER + file.read())
	elif file.name.lower()[-5:] in (".json", ".hash") and not ENCRYPTED:
		warning_message("UNKNOWN RTON HEADER (" + HEADER.hex() + ") in " + file.name)
def file_to_folder(inp, out, unpack_level, extensions, pathout):
	entries = get_archives(inp, out, unpack_level, extensions, pathout)
	split_task(len(entries))
	for inp, out in entries:
		try:
			if inp.lower().endswith((".apk", ".zip")):
				with ZipFile(inp, 'r') as zipObj:
					sub_entries = zipObj.namelist()
					split_task(len(sub_entries))
					for name in sub_entries:
						if name.lower().endswith(options["archiveExtensions"]):
							file_name = osjoin(out, name)
							if not exists(dirname(file_name)):
								makedirs(dirname(file_name), exist_ok = True)
							with zipObj.open(name, "r") as file:
								file.name = inp + ":" + name
								archive_extract(file, file_name, unpack_level, True)
						elif name.lower().endswith(options["encodedExtensions"]) and unpack_level > 5:
							file_name = osjoin(out, name)
							if not exists(dirname(file_name)):
								makedirs(dirname(file_name), exist_ok = True)
							with zipObj.open(name, "r") as file:
								file.name = inp + ":" + name
								file_decode(file, file_name, unpack_level, True)
						finish_sub_task()
					merge_task()
			else:
				with open(inp, "rb") as file:
					archive_extract(file, out, unpack_level, False)
		except Exception as e:
			error_message(e, " in " + inp, "Failed OBBUnpack: ")
		finish_sub_task()
	merge_task()
	finish_sub_task()
def get_archives(inp, out, unpack_level, extensions, pathout):
# Recursive file convert function
	if isdir(inp):
		makedirs(out, exist_ok = True)
		entries = []
		for entry in listdir(inp):
			input_file = osjoin(inp, entry)
			output_file = osjoin(out, entry)
			if isfile(input_file):
				if entry.lower().endswith(extensions):
					entries.append((input_file, splitext(output_file)[0]))
			elif input_file != pathout:
				entries.extend(get_archives(input_file, output_file, unpack_level, extensions, pathout))
		return entries
	elif isfile(inp):
		return [(inp, out)]
	else:
		return []
def conversion(inp, out, unpack_level, extensions, noextensions, pathout):
	entries = get_encoded(inp, out, unpack_level, extensions, noextensions, pathout)
	split_task(len(entries))
	for inp, out in entries:
		try:
			file = BytesIO()
			file = open(inp, "rb")
			file_decode(file, out, unpack_level, False)
			file.close()
		except Exception as e:
			error_message(e, " in " + inp + " pos " + repr(file.tell()))
			file.close()
		finish_sub_task()
	merge_task()
	finish_sub_task()
def get_encoded(inp, out, unpack_level, extensions, noextensions, pathout):
# Recursive file convert function
	if isdir(inp):
		makedirs(out, exist_ok = True)
		entries = []
		for entry in listdir(inp):
			input_file = osjoin(inp, entry)
			output_file = osjoin(out, entry)
			if isfile(input_file):
				check = entry.lower()
				if unpack_level > 7:
					if check[-5:] == ".rton":
						output_file = output_file[:-5]
					output_file += ".json"
				if check.endswith(extensions) or check.startswith(noextensions):
					entries.append((input_file, output_file))
			elif input_file != pathout:
				entries.extend(get_encoded(input_file, output_file, unpack_level, extensions, noextensions, pathout))
		return entries
	elif isfile(inp):
		return [(inp, out)]
	else:
		return []
# Start of the code
try:
	logerror = LogError()
	error_message = logerror.error_message
	warning_message = logerror.warning_message
	input_level = logerror.input_level
	split_task = logerror.split_task
	merge_task = logerror.merge_task
	finish_sub_task = logerror.finish_sub_task

	logerror.check_version(3, 9, 0)
	branches = {
		"beta": "Beta 1.2.1d Fixed numerous issues",
		"master": "Merge branch 'beta'"
	}
	release_tag = "1.2"
	print("""\033[95m
\033[1mOBBUnpacker v1.2.1d (c) 2022 Nineteendo\033[22m
\033[1mCode based on:\033[22m Luigi Auriemma, Small Pea & 1Zulu
\033[1mDocumentation:\033[22m Watto Studios, YingFengTingYu, TwinKleS-C & h3x4n1um
\033[1mFollow PyVZ2 development:\033[22m \033[4mhttps://discord.gg/CVZdcGKVSw\033[24m
\033[0m""")
	getupdate = logerror.get_update("Nineteendo/PVZ2tools", branches, release_tag)
	options = logerror.load_template(options, 1)
	level_to_name = ["SPECIFY", "ZIP", "SMF", "RSB", "RSG", "SECTION", "ENCRYPTED", "ENCODED", "DECODED"]
	list_levels(level_to_name)
	options["zipUnpackLevel"] = input_level("ZIP Unpack Level", 1, 2, options["zipUnpackLevel"])
	options["smfUnpackLevel"] = input_level("SMF/ZIP Unpack Level", 2, 3, options["smfUnpackLevel"])
	options["rsbUnpackLevel"] = input_level("RSB/SMF/ZIP Unpack Level", 3, 4, options["rsbUnpackLevel"])
	options["rsgUnpackLevel"] = input_level("RSG/RSB/SMF/ZIP Unpack Level", 4, 8, options["rsgUnpackLevel"])
	options["encryptedUnpackLevel"] = input_level("ENCRYPTED Unpack Level", 6, 8, options["encryptedUnpackLevel"])
	options["encodedUnpackLevel"] = input_level("ENCODED/ENCRYPTED Unpack Level", 7, 8, options["encodedUnpackLevel"])

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
	parse_root_object = RTONDecoder(comma, current_indent, doublePoint, ensureAscii, indent, repairFiles, sortKeys, sortValues, warning_message).parse_root_object
	
	blue_print("\nWorking directory: " + getcwd())
	entries = 0
	if 2 >= options["zipUnpackLevel"] > 1:
		entries += 1
		zip_input = path_input("ZIP Input file or directory", options["zipPacked"])
		if isfile(zip_input):
			zip_output = path_input("ZIP " + level_to_name[options["zipUnpackLevel"]] + " Output file", options["zipUnpacked"])
		else:
			zip_output = path_input("ZIP " + level_to_name[options["zipUnpackLevel"]] + " Output directory", options["zipUnpacked"])
	if 3 >= options["smfUnpackLevel"] > 2:
		entries += 1
		smf_input = path_input("SMF/ZIP Input file or directory", options["smfPacked"])
		if isfile(smf_input):
			smf_output = path_input("SMF/ZIP " + level_to_name[options["smfUnpackLevel"]] + " Output file", options["smfUnpacked"])
		else:
			smf_output = path_input("SMF/ZIP " + level_to_name[options["smfUnpackLevel"]] + " Output directory", options["smfUnpacked"])
	if 4 >= options["rsbUnpackLevel"] > 3:
		entries += 1
		rsb_input = path_input("RSB/SMF/ZIP Input file or directory", options["rsbPacked"])
		rsb_output = path_input("RSB/SMF/ZIP " + level_to_name[options["rsbUnpackLevel"]] + " Output directory", options["rsbUnpacked"])
	if 8 >= options["rsgUnpackLevel"] > 4:
		entries += 1
		rsg_input = path_input("RSG/RSB/SMF/ZIP Input file or directory", options["rsgPacked"])
		rsg_output = path_input("RSG/RSB/SMF/ZIP " + level_to_name[options["rsgUnpackLevel"]] + " Output directory", options["rsgUnpacked"])
	if 8 >= options["encryptedUnpackLevel"] > 6:
		entries += 1
		encrypted_input = path_input("ENCRYPTED Input file or directory", options["encryptedPacked"])
		if isfile(encrypted_input):
			encrypted_output = path_input("ENCRYPTED " + level_to_name[options["encryptedUnpackLevel"]] + " Output file", options["encryptedUnpacked"])
		else:
			encrypted_output = path_input("ENCRYPTED " + level_to_name[options["encryptedUnpackLevel"]] + " Output directory", options["encryptedUnpacked"])
	if 8 >= options["encodedUnpackLevel"] > 7:
		entries += 1
		encoded_input = path_input("ENCODED/ENCRYPTED Input file or directory", options["encodedPacked"])
		if isfile(encoded_input):
			encoded_output = path_input("ENCODED/ENCRYPTED " + level_to_name[options["encodedUnpackLevel"]] + " Output file", options["encodedUnpacked"])
		else:
			encoded_output = path_input("ENCODED/ENCRYPTED " + level_to_name[options["encodedUnpackLevel"]] + " Output directory", options["encodedUnpacked"])

	# Start file_to_folder
	logerror.set_levels(5)
	split_task(entries)
	if 2 >= options["zipUnpackLevel"] > 1:
		file_to_folder(zip_input, zip_output, options["zipUnpackLevel"], options["zipExtensions"], dirname(zip_output))
	if 3 >= options["smfUnpackLevel"] > 2:
		file_to_folder(smf_input, smf_output, options["smfUnpackLevel"], options["smfExtensions"], dirname(smf_output))
	if 4 >= options["rsbUnpackLevel"] > 3:
		file_to_folder(rsb_input, rsb_output, options["rsbUnpackLevel"], options["rsbExtensions"], rsb_output)
	if 8 >= options["rsgUnpackLevel"] > 4:
		file_to_folder(rsg_input, rsg_output, options["rsgUnpackLevel"], options["rsgExtensions"], rsg_output)
	if 8 >= options["encryptedUnpackLevel"] > 6:
		conversion(encrypted_input, encrypted_output, options["encryptedUnpackLevel"], options["encryptedExtensions"], (), dirname(encrypted_output))
	if 8 >= options["encodedUnpackLevel"] > 7:
		conversion(encoded_input, encoded_output, options["encodedUnpackLevel"], options["RTONExtensions"], options["RTONNoExtensions"], dirname(encoded_output))

	logerror.finish_program()
except Exception as e:
	logerror.set_levels(0)
	error_message(e)
except BaseException as e:
	logerror.set_levels(0)
	warning_message(type(e).__name__ + " : " + str(e))
logerror.close() # Close log