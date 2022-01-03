import os, struct, zlib

DUMP_PGSR_AS_IS = False
file = "obbs/main.6.com.ea.game.pvz2_na.obb"
folder = os.path.splitext(file)[0]
obb = open(file,"rb")

options = {
	"dumpAll": False,
	"startswith": (
		"PACKAGES/"
	)
}

def GET_NAME(NAME, NAME_DICT):
	TMP_BYTE = b""
	while TMP_BYTE != b"\x00":
		NAME += TMP_BYTE
		TMP_BYTE = obb.read(1)
		TMP_LENGTH = 4 * struct.unpack('<L', obb.read(3) + b"\x00")[0]
		if TMP_LENGTH != 0:
			NAME_DICT[NAME] = TMP_LENGTH
	return (NAME, NAME_DICT)

def pgsr_extract(PGSR_NAME, PGSR_OFFSET, PGSR_SIZE):
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
			
			NAME, NAME_DICT = GET_NAME(NAME, NAME_DICT)
			DECODED_NAME = NAME.decode().replace("\\", "/")
			ENCODED = struct.unpack('<L', obb.read(4))[0]
			FILE_OFFSET = struct.unpack('<L', obb.read(4))[0]
			SIZE = struct.unpack('<L', obb.read(4))[0]
			if ENCODED != 0:
				obb.seek(20, 1)
				if TYPE == 1:
					temp = obb.tell()
					obb.seek(PGSR_OFFSET + OFFSET)
					DECOMPRESSED = zlib.decompress(obb.read(X_ZSIZE))
					obb.seek(temp)
				
			temp = obb.tell()
			if NAME != b"" and TYPE == 3 and DECOMPRESSED == b"":
				obb.seek(PGSR_OFFSET + OFFSET)
				DECOMPRESSED = zlib.decompress(obb.read(X_ZSIZE))
			
			if DECODED_NAME != "" and (DECODED_NAME.startswith(options["startswith"]) or options["dumpAll"]):
				os.makedirs(os.path.dirname(os.path.join(folder, DECODED_NAME)), exist_ok=True)
				if ENCODED == 0 and TYPE == 1:
					obb.seek(PGSR_OFFSET + PGSR_BASE + FILE_OFFSET)
					open(os.path.join(folder, DECODED_NAME), "wb").write(obb.read(SIZE))
				else:
					open(os.path.join(folder, DECODED_NAME), "wb").write(DECOMPRESSED[FILE_OFFSET:FILE_OFFSET+SIZE])
				
				print("wrote " + DECODED_NAME)
			
			obb.seek(temp)
			
	obb.seek(BACKUP_OFFSET)

SIGN = obb.read(4)
if SIGN == b"pgsr":
	obb.seek(0,)
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
	
		if DUMP_PGSR_AS_IS:
			temp = obb.tell()
			obb.seek(OFFSET)
			os.makedirs(folder, exist_ok=True)
			open(os.path.join(folder, NAME + ".pgsr"), "wb").write(obb.read(SIZE))
			print("wrote " + NAME + ".pgsr")
			obb.seek(temp)
		else:
			pgsr_extract(NAME, OFFSET, SIZE)