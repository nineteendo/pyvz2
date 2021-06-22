import zlib, os

filename = input("OBB/RSB=")
patch = input("Section=")
for line in open('versions.cfg', 'r').readlines():
    if not "#" in line and not ";" in line: 
        line = line.split(":")
        name = line[0]
        line = line[1].split(",")
        file_size = int(line[0])
        offset = int(line[1])
        packed_size = int(line[2])
        if packed_size < 0:
        	packed_size -= offset
        if os.path.getsize(filename) == file_size:
            data = zlib.compress(open(patch, 'rb').read(), 9)
            compressed = open(filename, 'rb')
            compressed.read(offset)
            open(name + "_backup.section", 'wb').write(zlib.decompress(compressed.read()))
            print("\nmade backup " + name + "_backup.section")
            if len(data) <= packed_size:
                compressed = open(filename, 'rb')
                write = compressed.read(offset) + data + (packed_size-len(data)) * b"\x00"
                compressed.read(packed_size)
                write += compressed.read()
                open(filename, 'wb').write(write)
            else:
                print("section doesn't fit in the obb, try a smaller section")
