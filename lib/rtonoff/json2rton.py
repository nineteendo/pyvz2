"""
RTON/OFF json2rton
"""

# Standard libraries
from json import load
from struct import pack, unpack

INFINITY = float('Infinity')
NEGATIVE_INFINITY = -INFINITY


class KeyValueList:
    """
    List of key value pairs
    """

    def __init__(self, data):
        self.data = data


class JSONDecoder():
    def encode_object_pairs(self, pairs):
        # Object to list of tuples
        return KeyValueList(pairs)

    def encode_number(self, integ):
        # Number with variable length
        i = integ % 128
        integ = integ // 128
        if integ:
            i += 128
        string = pack("B", i)
        while integ:
            i = integ % 128
            integ = integ // 128
            if integ:
                i += 128
            string += pack("B", i)
        return string

    def encode_utf8_text(self, string):
        # unicode text in rtid
        encoded_string = string.encode()
        return self.encode_number(len(string)) + self.encode_number(len(encoded_string)) + encoded_string

    def encode_bool(self, boolean):
        # type 00, 01
        return b"\x01" if boolean else b"\0"

    def encode_int(self, integ):
        # type 08, 0a, 10, 12, 20, 21, 25, 26, 29, 40, 45, 46, 49
        if integ == 0:
            return b"!"
        if 0 <= integ <= 2097151:
            return b"$" + self.encode_number(integ)
        if -1048576 <= integ <= 0:
            return b"%" + self.encode_number(-1 - 2 * integ)
        if -2147483648 <= integ <= 2147483647:
            return b" " + pack("<i", integ)
        if 0 <= integ < 4294967295:
            return b"&" + pack("<I", integ)
        if 0 <= integ <= 562949953421311:
            return b"D" + self.encode_number(integ)
        if -281474976710656 <= integ <= 0:
            return b"E" + self.encode_number(-1 - 2 * integ)
        if -9223372036854775808 <= integ <= 9223372036854775807:
            return b"@" + pack("<q", integ)
        if 0 <= integ <= 18446744073709551615:
            return b"F" + pack("<Q", integ)
        if integ >= 0:
            return b"D" + self.encode_number(integ)
        return b"E" + self.encode_number(-1 - 2 * integ)

    def encode_float(self, dec):
        # type 22, 42
        if dec == 0:
            return b"#"
        elif -340282346638528859811704183484516925440 <= dec <= 340282346638528859811704183484516925440 and dec == unpack("<f", pack("<f", dec))[0] or dec != dec or dec == INFINITY or dec == NEGATIVE_INFINITY:
            return b'"' + pack("<f", dec)
        else:
            return b"B" + pack("<d", dec)

    def encode_rtid(self, string):
        # type 83
        if "@" in string:
            name, type = string[5:-1].split("@")
            if name.count(".") == 2:
                i2, i1, i3 = name.split(".")
                return b"\x83\x02" + self.encode_utf8_text(type) + self.encode_number(int(i1)) + self.encode_number(int(i2)) + bytes.fromhex(i3)[::-1]
            else:
                return b"\x83\x03" + self.encode_utf8_text(type) + self.encode_utf8_text(name)
        else:
            return b"\x84"

    def encode_root_object(self, file):
        # type 85*
        cached_strings = {}
        items = []
        for key, value in load(file, object_pairs_hook=self.encode_object_pairs).data:
            key = self.encode_cached_string(key, cached_strings)
            if isinstance(value, str):
                if "RTID()" == value[:5] + value[-1:]:
                    value = self.encode_rtid(value)
                else:
                    value = self.encode_cached_string(value, cached_strings)
            elif isinstance(value, bool):
                value = self.encode_bool(value)
            elif isinstance(value, int):
                value = self.encode_int(value)
            elif isinstance(value, float):
                value = self.encode_float(value)
            elif isinstance(value, list):
                value = self.encode_array(value, cached_strings)
            elif isinstance(value, KeyValueList):
                value = self.encode_object(value, cached_strings)
            elif value is None:
                value = b"\x84"
            else:
                raise TypeError(type(value))
            items.append(key + value)
        return b"RTON\x01\0\0\0" + b"".join(items) + b"\xffDONE"

    def encode_object(self, data, cached_strings):
        # type 85
        items = []
        for key, value in data.data:
            key = self.encode_cached_string(key, cached_strings)
            if isinstance(value, str):
                if "RTID()" == value[:5] + value[-1:]:
                    value = self.encode_rtid(value)
                else:
                    value = self.encode_cached_string(value, cached_strings)
            elif isinstance(value, bool):
                value = self.encode_bool(value)
            elif isinstance(value, int):
                value = self.encode_int(value)
            elif isinstance(value, float):
                value = self.encode_float(value)
            elif isinstance(value, list):
                value = self.encode_array(value, cached_strings)
            elif isinstance(value, KeyValueList):
                value = self.encode_object(value, cached_strings)
            elif value == None:
                value = b"\x84"
            else:
                raise TypeError(type(value))
            items.append(key + value)
        return b"\x85" + b"".join(items) + b"\xff"

    def encode_array(self, data, cached_strings):
        # type 86
        items = []
        for value in data:
            if isinstance(value, str):
                if "RTID()" == value[:5] + value[-1:]:
                    value = self.encode_rtid(value)
                else:
                    value = self.encode_cached_string(value, cached_strings)
            elif isinstance(value, bool):
                value = self.encode_bool(value)
            elif isinstance(value, int):
                value = self.encode_int(value)
            elif isinstance(value, float):
                value = self.encode_float(value)
            elif isinstance(value, list):
                value = self.encode_array(value, cached_strings)
            elif isinstance(value, KeyValueList):
                value = self.encode_object(value, cached_strings)
            elif value == None:
                value = b"\x84"
            else:
                raise TypeError(type(value))
            items.append(value)
        return b"\x86\xfd" + self.encode_number(len(data)) + b"".join(items) + b"\xfe"

    def encode_cached_string(self, string, cached_strings):
        # type 90, 91
        if string in cached_strings:
            return b"\x91" + self.encode_number(cached_strings[string])
        else:
            cached_strings[string] = len(cached_strings)
            encoded_string = string.encode()
            return b"\x90" + self.encode_number(len(encoded_string)) + encoded_string
