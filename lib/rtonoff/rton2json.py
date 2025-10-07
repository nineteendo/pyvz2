"""
RTON/OFF rton2json
"""

from json import dumps
from struct import error, unpack

INFINITY = float('Infinity')
NEGATIVE_INFINITY = -INFINITY


def parse_number(file):
    """
    Parse number of a variable length
    """
    num = file.read(1)[0]
    result = num % 128
    i = 1
    while num >= 128:
        i *= 128
        num = file.read(1)[0]
        result += num % 128 * i
    return result


def parse_text(file):
    """
    Parse text
    """
    byte = file.read(parse_number(file))
    try:
        return byte.decode()
    except UnicodeDecodeError:
        return byte.decode('latin-1')


def parse_false(_1, _2: bytes, _3: list, _4: list):
    """
    Type 00
    """
    return b"false"


def parse_true(_1, _2: bytes, _3: list, _4: list):
    """
    Type 01
    """
    return b"true"


def parse_int8(file, _1: bytes, _2: list, _3: list):
    """
    Type 08
    """
    return repr(unpack("b", file.read(1))[0]).encode()


def parse_zero(_1, _2: bytes, _3: list, _4: list):
    """
    Type 09, 0b, 11, 13, 21, 27, 41, 47
    """
    return b"0"


def parse_uint8(file, _1: bytes, _2: list, _3: list):
    """
    Type 0a
    """
    return repr(file.read(1)[0]).encode()


def parse_int16(file, _1: bytes, _2: list, _3: list):
    """
    Type 10
    """
    return repr(
        unpack("<h", file.read(2))[0]
    ).encode()


def parse_uint16(file, _1: bytes, _2: list, _3: list):
    """
    Type 12
    """
    return repr(
        unpack("<H", file.read(2))[0]
    ).encode()


def parse_int32(file, _1: bytes, _2: list, _3: list):
    """
    Type 20
    """
    return repr(
        unpack("<i", file.read(4))[0]
    ).encode()


def parse_float32(file, _1: bytes, _2: list, _3: list):
    """
    Type 22
    """
    float_value = unpack("<f", file.read(4))[0]
    if float_value != float_value:
        return b'NaN'
    if float_value == INFINITY:
        return b'Infinity'
    if float_value == NEGATIVE_INFINITY:
        return b'-Infinity'
    return repr(float_value).encode()


def parse_zero_point_zero(
        _1, _2: bytes, _3: list, _4: list
):
    """
    Type 23, 43
    """
    return b"0.0"


def parse_uvarint(file, _1: bytes, _2: list, _3: list):
    """
    Type 24, 28, 44 & 48
    """
    return repr(parse_number(file)).encode()


def parse_varint(file, _1: bytes, _2: list, _3: list):
    """
    Type 25 & 45
    """
    num = parse_number(file)
    if num / 2:  # Odd number
        num = -num - 1
    return repr(num // 2).encode()


def parse_uint32(file, _1: bytes, _2: list, _3: list):
    """
    Type 26
    """
    return repr(
        unpack("<I", file.read(4))[0]
    ).encode()


def parse_int64(file, _1: bytes, _2: list, _3: list):
    """
    Type 40
    """
    return repr(
        unpack("<q", file.read(8))[0]
    ).encode()


def parse_float64(file, _1: bytes, _2: list, _3: list):
    """
    Type 42
    """
    double_value = unpack("<d", file.read(8))[0]
    if double_value != double_value:
        return b'NaN'
    if double_value == INFINITY:
        return b'Infinity'
    if double_value == NEGATIVE_INFINITY:
        return b'-Infinity'
    return repr(double_value).encode()


def parse_uint64(file, _1: bytes, _2: list, _3: list):
    """
    Type 46
    """
    return repr(
        unpack("<Q", file.read(8))[0]
    ).encode()


def parse_rtid_zero(_1):
    """
    Type 8300
    """
    return b'"RTID(0)"'


def parse_zero_ref(_1, _2: bytes, _3: list, _4: list):
    """
    Type 84
    """
    return b'"RTID(0)"'


def parse_cached_str_recall(
        file, _1: str, cached_strings, _2: list
):
    """
    Type 91
    """
    return cached_strings[parse_number(file)]


def parse_cached_printable_str_recall(
        file, _1: str, _2: list,
        cached_printable_strings
):
    """
    Type 93
    """
    return cached_printable_strings[
        parse_number(file)
    ]


class RTONDecoder():
    """
    RTON Decoder class
    """

    def __init__(
            self, comma=b",", currrent_indent=b"\n",
            double_point=b": ", ensure_ascii=False,
            indent=b"\t", repair_files=True,
            sort_keys=False,
            warning_message=lambda x: None
    ):
        self.comma = comma
        self.currrent_indent = currrent_indent
        self.double_point = double_point
        self.ensure_ascii = ensure_ascii
        self.warning_message = warning_message
        self.indent = indent
        self.repair_files = repair_files
        self.sort_keys = sort_keys
        self.rtid_mappings = {
            b"\x83\x00": parse_rtid_zero,
            b"\x83\x02": self.parse_rtid_uid,
            b"\x83\x03": self.parse_rtid_ref
        }
        self.key_mappings = {
            b"\x81": self.parse_str,
            b"\x82": self.parse_printable_str,
            b"\x83": self.parse_rtid,
            b"\x84": parse_zero_ref,

            b"\x90": self.parse_cached_str,
            b"\x91": parse_cached_str_recall,
            b"\x92": self.parse_cached_printable_str,
            b"\x93": parse_cached_printable_str_recall
        }
        self.value_mappings = {
            b"\x00": parse_false,
            b"\x01": parse_true,

            b"\x08": parse_int8,
            b"\x09": parse_zero,  # int8_zero
            b"\x0a": parse_uint8,
            b"\x0b": parse_zero,  # uint8_zero

            b"\x10": parse_int16,
            b"\x11": parse_zero,  # int16_zero
            b"\x12": parse_uint16,
            b"\x13": parse_zero,  # uint16_zero

            b"\x20": parse_int32,
            b"\x21": parse_zero,  # int32_zero
            b"\x22": parse_float32,
            b"\x23": (
                parse_zero_point_zero  # float32_zero
            ),
            b"\x24": parse_uvarint,  # int32_uvarint
            b"\x25": parse_varint,  # int32_varint
            b"\x26": parse_uint32,
            b"\x27": parse_zero,  # uint_32_zero
            b"\x28": parse_uvarint,  # uint32_uvarint

            b"\x40": parse_int64,
            b"\x41": parse_zero,  # int64_zero
            b"\x42": parse_float64,
            b"\x43": (
                parse_zero_point_zero  # float64_zero
            ),
            b"\x44": parse_uvarint,  # int64_uvarint
            b"\x45": parse_varint,  # int64_varint
            b"\x46": parse_uint64,
            b"\x47": parse_zero,  # uint64_zero
            b"\x48": parse_uvarint,  # uint64_uvarint

            b"\x81": self.parse_str,
            b"\x82": self.parse_printable_str,
            b"\x83": self.parse_rtid,
            b"\x84": parse_zero_ref,
            b"\x85": self.parse_object,
            b"\x86": self.parse_list,

            b"\x90": self.parse_cached_str,
            b"\x91": parse_cached_str_recall,
            b"\x92": self.parse_cached_printable_str,
            b"\x93": parse_cached_printable_str_recall
        }

    def parse_utf8_text(self, file):
        """
        Parse unicode string
        """
        character_length = parse_number(file)
        string = file.read(
            parse_number(file)
        ).decode()
        length = len(string)
        if character_length != length:
            self.warning_message(
                f"SilentError: {file.name}" +
                f"pos {file.tell()}: " +
                f"Unicode string of length {length} " +
                f"found, expected {character_length}"
            )
        return string

    def parse_str(self, file, _1: bytes, _2: list, _3: list):
        """
        Type 81
        """
        return dumps(
            parse_text(file),
            ensure_ascii=self.ensure_ascii
        ).encode()

    def parse_printable_str(
            self, file, _1: bytes, _2: list, _3: list
    ):
        """
        Type 82
        """
        return dumps(
            self.parse_utf8_text(file),
            ensure_ascii=self.ensure_ascii
        ).encode()

    def parse_rtid(
            self, file, _1: bytes, _2: list, _3: list
    ):
        """
        Type 83
        """
        return self.rtid_mappings[
            b"\x83" + file.read(1)
        ](file)

    def parse_rtid_uid(self, file):
        """
        Type 8302
        """
        source = self.parse_utf8_text(file)
        minor = parse_number(file)
        major = parse_number(file)
        micro = file.read(4)[::-1].hex()
        return dumps(
            f"RTID({major}.{minor}.{micro}@{source})",
            ensure_ascii=self.ensure_ascii
        ).encode()

    def parse_rtid_ref(self, file):
        """
        Type 8303
        """
        source = self.parse_utf8_text(file)
        target = self.parse_utf8_text(file)
        return dumps(
            f"RTID({target}@{source})",
            ensure_ascii=self.ensure_ascii
        ).encode()

    def parse_root_object(self, file):
        """
        Type 85*
        HEADER = file.read(4)
        VERSION = unpack("<I", file.read(4))[0]
        """
        file.seek(8)
        return self.parse_object(
            file, self.currrent_indent, [], []
        )

    def parse_object(
            self, file, currrent_indent, cached_strings,
            cached_printable_strings
    ):
        """
        Type 85
        """
        new_indent = currrent_indent + self.indent
        items = []
        try:
            code = file.read(1)
            while code != b"\xff":
                key = self.key_mappings[code](
                    file, new_indent, cached_strings,
                    cached_printable_strings
                )
                value = self.value_mappings[file.read(1)](
                    file, new_indent, cached_strings,
                    cached_printable_strings
                )
                items.append(
                    key + self.double_point + value
                )
                code = file.read(1)
        except KeyError as k:
            if (
                    len(k.args) != 1 or
                    not isinstance(k.args[0], bytes)
            ):
                raise Exception(k) from k
            key = k.args[0]
            if key:
                raise TypeError(
                    f"unknown tag {key.hex()}"
                ) from k
            if not self.repair_files:
                raise EOFError from k
            self.warning_message(
                f"SilentError: {file.name } " +
                f"pos {file.tell()}: end of file"
            )
        except (error, IndexError):
            if not self.repair_files:
                raise EOFError from k
            self.warning_message(
                f"SilentError: {file.name } " +
                f"pos {file.tell()}: end of file"
            )
        if not items:
            return b"{}"
        if self.sort_keys:
            items = sorted(items)
        return (
            b"{" + new_indent +
            (self.comma + new_indent).join(items) +
            currrent_indent + b"}"
        )

    def parse_list(
            self, file, currrent_indent, cached_strings,
            cached_printable_strings
    ):
        """
        Type 86
        """
        start_code = file.read(1)
        if start_code != b"\xfd":
            raise TypeError(
                f"unknown tag 86{start_code.hex()}"
            )
        new_indent = currrent_indent + self.indent
        items = []
        list_length = parse_number(file)
        try:
            code = file.read(1)
            while code != b"\xfe":
                value = self.value_mappings[code](
                    file, new_indent, cached_strings,
                    cached_printable_strings
                )
                items.append(value)
                code = file.read(1)
        except KeyError as k:
            if (
                    len(k.args) != 1 or
                    not isinstance(k.args[0], bytes)
            ):
                raise Exception(k) from k
            key = k.args[0]
            if key:
                raise TypeError(
                    f"unknown tag {key.hex()}"
                ) from k
            if not self.repair_files:
                raise EOFError from k
            self.warning_message(
                f"SilentError: {file.name } " +
                f"pos {file.tell()}: end of file"
            )
        except (error, IndexError):
            if not self.repair_files:
                raise EOFError from k
            self.warning_message(
                f"SilentError: {file.name } " +
                f"pos {file.tell()}: end of file"
            )
        length = len(items)
        if list_length != length:
            self.warning_message(
                f"SilentError: {file.name } " +
                f"pos {file.tell()}: List of length {length} " +
                f"found, expected {list_length}"
            )
        if not items:
            return b"[]"
        return (
            b"[" + new_indent +
            (self.comma + new_indent).join(items) +
            currrent_indent + b"]"
        )

    def parse_cached_str(
            self, file, _1: bytes, cached_strings, _2: list
    ):
        """
        Type 90
        """
        string = dumps(
            parse_text(file),
            ensure_ascii=self.ensure_ascii
        ).encode()
        cached_strings.append(string)
        return string

    def parse_cached_printable_str(
            self, file, _1: str, _2: list,
            cached_printable_strings
    ):
        """
        Type 92
        """
        string = dumps(
            self.parse_utf8_text(file),
            ensure_ascii=self.ensure_ascii
        ).encode()
        cached_printable_strings.append(string)
        return string
