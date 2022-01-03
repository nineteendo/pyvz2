import zlib, os

filename = input("OBB/RSB=")
for line in open('versions.cfg', 'r').readlines():
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
