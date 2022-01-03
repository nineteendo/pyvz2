import os, struct, zlib

obb = open("main.rsb","rb")

if obb.read(4) == b"1bsr":
	obb.seek(40)
	os.makedirs("pgsr", exist_ok=True)
	FILES = struct.unpack('<L', obb.read(4))[0]
	OFFSET = struct.unpack('<L', obb.read(4))[0]

	print(FILES, OFFSET)
	obb.seek(OFFSET)
	for i in range(0, FILES):
		NAME = obb.read(128).strip(b"\x00").decode()
		OFFSET = struct.unpack('<L', obb.read(4))[0]
		SIZE = struct.unpack('<L', obb.read(4))[0]
		obb.seek(68, 1)
	
		temp = obb.tell()
		obb.seek(OFFSET)
		open(os.path.join("pgsr", NAME), "wb").write(obb.read(SIZE))
		print("wrote " + NAME)
		obb.seek(temp)