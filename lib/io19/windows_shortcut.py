"""Windows shortcut"""
from enum import Enum
from io import BufferedReader, BytesIO
from struct import unpack
from datetime import datetime, timedelta
from typing import Any, Optional

FILETIME_EPOCH: datetime = datetime(1601, 1, 1)
HEADER_SIZE: int = 0x0000004C
LINK_CLSID: str = '01140200 00000000 c0000000 00000046'


def readshortcut_basic(path: str) -> str:
    """Read shortcut basic"""
    with open(path, 'rb') as stream:
        stream.seek(0x14)
        link_flags: int = unpack('<I', stream.read(4))[0]
        position: int = 0x18
        if (link_flags & 0x01) == 0x01:
            stream.seek(0x4C)
            position: int = 0x4E + unpack('<H', stream.read(2))[0]
            stream.seek(position)

        length: int = unpack('<I', stream.read(4))[0]
        print(length)
        stream.seek(0x0C, 1)
        lbpos: int = unpack('<I', stream.read(4))[0]
        print(lbpos)
        size: int = length - lbpos - 0x02
        stream.seek(position + lbpos)
        return stream.read(size).decode()


class ShellLink:
    """Shell link class"""

    def __init__(self, path: str) -> None:
        with open(path, 'rb') as file:
            self.header: ShellLinkHeader = ShellLinkHeader(file)
            if self.header.link_flags.has_link_target_idlist:
                self.link_target_idlist: LinkTargetIDList = LinkTargetIDList(
                    file
                )

            if self.header.link_flags.has_link_info:
                print('has_link_info')  # TODO - Later

            if self.header.link_flags.has_name:
                print('has_name')  # TODO - Later

            if self.header.link_flags.has_relative_path:
                self.relative_path: StringData = StringData(file)
                print(self.relative_path.string)
            
            if self.header.link_flags.has_working_dir:
                print('has_working_dir')  # TODO - Later
            
            if self.header.link_flags.has_arguments:
                print('has_arguments')  # TODO - Later
            
            if self.header.link_flags.has_icon_location:
                print('has_icon_location')  # TODO - Later
            
            if self.header.link_flags.is_unicode:
                print('is_unicode')  # TODO - Later


class ShellLinkHeader:
    """Shell link header class"""

    def __init__(self, file: BufferedReader) -> None:
        self.header_size: int = unpack('<I', file.read(4))[0]
        assert self.header_size == HEADER_SIZE, self.header_size
        self.link_clsid: str = file.read(16).hex(' ', 4)
        assert self.link_clsid == LINK_CLSID, self.link_clsid
        self.link_flags: LinkFlags = LinkFlags(unpack('>I', file.read(4))[0])
        self.file_attributes: FileAttributesFlags = FileAttributesFlags(
            unpack('>I', file.read(4))[0]
        )
        self.creation_time: Optional[datetime] = read_filetime(file)
        self.access_time: Optional[datetime] = read_filetime(file)
        self.write_time: Optional[datetime] = read_filetime(file)
        self.file_size: int = unpack('<I', file.read(4))[0]  # Lower 32 bits
        self.icon_index: int = unpack('<I', file.read(4))[0]
        self.show_command: ShowCommand = ShowCommand(
            unpack('<I', file.read(4))[0]
        )
        self.hot_key: HotKeyFlags = HotKeyFlags(unpack('<H', file.read(2))[0])
        self.reserved_42: int = unpack('<H', file.read(2))[0]
        # NOTE - A value that MUST be zero
        assert self.reserved_42 == 0, self.reserved_42
        self.reserved_44: int = unpack('<I', file.read(4))[0]
        # NOTE - A value that MUST be zero
        assert self.reserved_44 == 0, self.reserved_44
        self.reserved_48: int = unpack('<I', file.read(4))[0]
        # NOTE - A value that MUST be zero
        assert self.reserved_48 == 0, self.reserved_48 == 0


class LinkFlags:
    """
    Link flags class
    NOTE - Big-endian
    """

    def __init__(self, flags: int) -> None:
        self.has_link_target_idlist:          bool = flags & 0x80000000 != 0
        self.has_link_info:                   bool = flags & 0x40000000 != 0
        self.has_name:                        bool = flags & 0x20000000 != 0
        self.has_relative_path:               bool = flags & 0x10000000 != 0
        self.has_working_dir:                 bool = flags & 0x08000000 != 0
        self.has_arguments:                   bool = flags & 0x04000000 != 0
        self.has_icon_location:               bool = flags & 0x02000000 != 0
        self.is_unicode:                      bool = flags & 0x01000000 != 0
        self.force_no_link_info:              bool = flags & 0x00800000 != 0
        self.has_exp_string:                  bool = flags & 0x00400000 != 0
        self.run_in_separate_process:         bool = flags & 0x00200000 != 0
        self.unused_00100000:                 bool = flags & 0x00100000 != 0
        self.has_darwin_id:                   bool = flags & 0x00080000 != 0
        self.run_as_user:                     bool = flags & 0x00040000 != 0
        self.has_exp_icon:                    bool = flags & 0x00020000 != 0
        self.no_pidl_alias:                   bool = flags & 0x00010000 != 0
        self.unused_00008000:                 bool = flags & 0x00008000 != 0
        self.run_with_shim_layer:             bool = flags & 0x00004000 != 0
        self.force_no_link_track:             bool = flags & 0x00002000 != 0
        self.enable_target_metadata:          bool = flags & 0x00001000 != 0
        self.disable_link_path_tracking:      bool = flags & 0x00000800 != 0
        self.disable_known_folder_tracking:   bool = flags & 0x00000400 != 0
        self.disable_known_folder_alias:      bool = flags & 0x00000200 != 0
        self.allow_link_to_link:              bool = flags & 0x00000100 != 0
        self.unalias_on_save:                 bool = flags & 0x00000080 != 0
        self.prefer_environment_path:         bool = flags & 0x00000040 != 0
        self.keep_local_idlist_for_unctarget: bool = flags & 0x00000020 != 0
        self.unknown_0000001f:                 int = flags & 0x0000001F


class FileAttributesFlags:
    """
    File attributes flags class
    NOTE - Big-endian
    """

    def __init__(self, flags: int) -> None:
        self.FILE_ATTRIBUTE_READONLY:            bool = flags & 0x80000000 != 0
        self.FILE_ATTRIBUTE_HIDDEN:              bool = flags & 0x40000000 != 0
        self.FILE_ATTRIBUTE_SYSTEM:              bool = flags & 0x20000000 != 0
        self.RESERVED_10000000:                  bool = flags & 0x10000000 != 0
        assert not self.RESERVED_10000000
        self.FILE_ATTRIBUTE_DIRECTORY:           bool = flags & 0x08000000 != 0
        self.FILE_ATTRIBUTE_ARCHIVE:             bool = flags & 0x04000000 != 0
        self.RESERVED_02000000:                  bool = flags & 0x02000000 != 0
        assert not self.RESERVED_02000000
        self.FILE_ATTRIBUTE_NORMAL:              bool = flags & 0x01000000 != 0
        self.FILE_ATTRIBUTE_TEMPORARY:           bool = flags & 0x00800000 != 0
        self.FILE_ATTRIBUTE_SPARSE_FILE:         bool = flags & 0x00400000 != 0
        self.FILE_ATTRIBUTE_REPARSE_POINT:       bool = flags & 0x00200000 != 0
        self.FILE_ATTRIBUTE_COMPRESSED:          bool = flags & 0x00100000 != 0
        self.FILE_ATTRIBUTE_OFFLINE:             bool = flags & 0x00080000 != 0
        self.FILE_ATTRIBUTE_NOT_CONTENT_INDEXED: bool = flags & 0x00040000 != 0
        self.FILE_ATTRIBUTE_ENCRYPTED:           bool = flags & 0x00020000 != 0
        self.UNKNOWN_0001FFFF:                    int = flags & 0x0001FFFF
        assert not self.FILE_ATTRIBUTE_NORMAL or not (
            self.FILE_ATTRIBUTE_READONLY or self.FILE_ATTRIBUTE_HIDDEN or
            self.FILE_ATTRIBUTE_SYSTEM or self.FILE_ATTRIBUTE_DIRECTORY or
            self.FILE_ATTRIBUTE_ARCHIVE or self.FILE_ATTRIBUTE_TEMPORARY or
            self.FILE_ATTRIBUTE_SPARSE_FILE or
            self.FILE_ATTRIBUTE_REPARSE_POINT or
            self.FILE_ATTRIBUTE_COMPRESSED or self.FILE_ATTRIBUTE_OFFLINE or
            self.FILE_ATTRIBUTE_NOT_CONTENT_INDEXED or
            self.FILE_ATTRIBUTE_ENCRYPTED
        )


def read_filetime(file: BufferedReader) -> Optional[datetime]:
    """Read filetime"""
    intervals: int = unpack('<Q', file.read(8))[0]
    if intervals:
        return FILETIME_EPOCH + timedelta(microseconds=intervals // 10)


class ShowCommand(Enum):
    """Show command enum"""
    SW_SHOWNORMAL:      'ShowCommand' = 0x00000001
    SW_SHOWMAXIMIZED:   'ShowCommand' = 0x00000003
    SW_SHOWMINNOACTIVE: 'ShowCommand' = 0x00000007

    @classmethod
    def _missing_(cls, value: Any) -> Optional['ShowCommand']:
        if isinstance(value, int):
            # NOTE - All other values MUST be treated as SW_SHOWNORMAL.
            return cls.SW_SHOWNORMAL


class HotKeyFlags:
    """Hot key flags class"""

    def __init__(self, hot_key: int) -> None:
        self.UNKNOWN_F800:     int = (hot_key & 0xF800) >> 11
        self.HOTKEYF_ALT:     bool = hot_key & 0x0400 != 0
        self.HOTKEYF_CONTROL: bool = hot_key & 0x0200 != 0
        self.HOTKEYF_SHIFT:   bool = hot_key & 0x0100 != 0
        self.KEY:              Key = Key(hot_key & 0x00FF)


class Key(Enum):
    """
    Key enum
    https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
    """
    NONE:                   'Key' = 0x00
    VK_LBUTTON:             'Key' = 0x01
    VK_RBUTTON:             'Key' = 0x02
    VK_CANCEL:              'Key' = 0x03
    VK_MBUTTON:             'Key' = 0x04
    VK_XBUTTON1:            'Key' = 0x05
    VK_XBUTTON2:            'Key' = 0x06
    UNUSED_07:              'Key' = 0x07
    VK_BACK:                'Key' = 0x08
    VK_TAB:                 'Key' = 0x09
    RESERVED_0A:            'Key' = 0x0A
    RESERVED_0B:            'Key' = 0x0B
    VK_CLEAR:               'Key' = 0x0C
    VK_RETURN:              'Key' = 0x0D
    UNUSED_0E:              'Key' = 0x0E
    UNUSED_0F:              'Key' = 0x0F
    VK_SHIFT:               'Key' = 0x10
    VK_CONTROL:             'Key' = 0x11
    VK_MENU:                'Key' = 0x12
    VK_PAUSE:               'Key' = 0x13
    VK_CAPITAL:             'Key' = 0x14
    VK_KANA:                'Key' = 0x15  # VK_HANGUEL or VK_HANGUL
    VK_IME_ON:              'Key' = 0x16
    VK_JUNJA:               'Key' = 0x17
    VK_FINAL:               'Key' = 0x18
    VK_HANJA:               'Key' = 0x19  # VK_KANJI
    VK_IME_OFF:             'Key' = 0x1A
    VK_ESCAPE:              'Key' = 0x1B
    VK_CONVERT:             'Key' = 0x1C
    VK_NONCONVERT:          'Key' = 0x1D
    VK_ACCEPT:              'Key' = 0x1E
    VK_MODECHANGE:          'Key' = 0x1F
    VK_SPACE:               'Key' = 0x20
    VK_PRIOR:               'Key' = 0x21
    VK_NEXT:                'Key' = 0x22
    VK_END:                 'Key' = 0x23
    VK_HOME:                'Key' = 0x24
    VK_LEFT:                'Key' = 0x25
    VK_UP:                  'Key' = 0x26
    VK_RIGHT:               'Key' = 0x27
    VK_DOWN:                'Key' = 0x28
    VK_SELECT:              'Key' = 0x29
    VK_PRINT:               'Key' = 0x2A
    VK_EXECUTE:             'Key' = 0x2B
    VK_SNAPSHOT:            'Key' = 0x2C
    VK_INSERT:              'Key' = 0x2D
    VK_DELETE:              'Key' = 0x2E
    VK_HELP:                'Key' = 0x2F
    VK_0:                   'Key' = 0x30
    VK_1:                   'Key' = 0x31
    VK_2:                   'Key' = 0x32
    VK_3:                   'Key' = 0x33
    VK_4:                   'Key' = 0x34
    VK_5:                   'Key' = 0x35
    VK_6:                   'Key' = 0x36
    VK_7:                   'Key' = 0x37
    VK_8:                   'Key' = 0x38
    VK_9:                   'Key' = 0x39
    UNUSED_3A:              'Key' = 0x3A
    UNUSED_3B:              'Key' = 0x3B
    UNUSED_3C:              'Key' = 0x3C
    UNUSED_3D:              'Key' = 0x3D
    UNUSED_3E:              'Key' = 0x3E
    UNUSED_3F:              'Key' = 0x3F
    UNUSED_40:              'Key' = 0x40
    VK_A:                   'Key' = 0x41
    VK_B:                   'Key' = 0x42
    VK_C:                   'Key' = 0x43
    VK_D:                   'Key' = 0x44
    VK_E:                   'Key' = 0x45
    VK_F:                   'Key' = 0x46
    VK_G:                   'Key' = 0x47
    VK_H:                   'Key' = 0x48
    VK_I:                   'Key' = 0x49
    VK_J:                   'Key' = 0x4A
    VK_K:                   'Key' = 0x4B
    VK_L:                   'Key' = 0x4C
    VK_M:                   'Key' = 0x4D
    VK_N:                   'Key' = 0x4E
    VK_O:                   'Key' = 0x4F
    VK_P:                   'Key' = 0x50
    VK_Q:                   'Key' = 0x51
    VK_R:                   'Key' = 0x52
    VK_S:                   'Key' = 0x53
    VK_T:                   'Key' = 0x54
    VK_U:                   'Key' = 0x55
    VK_V:                   'Key' = 0x56
    VK_W:                   'Key' = 0x57
    VK_X:                   'Key' = 0x58
    VK_Y:                   'Key' = 0x59
    VK_Z:                   'Key' = 0x5A
    VK_LWIN:                'Key' = 0x5B
    VK_RWIN:                'Key' = 0x5C
    VK_APPS:                'Key' = 0x5D
    RESERVED_5E:            'Key' = 0x5E
    VK_SLEEP:               'Key' = 0x5F
    VK_NUMPAD0:             'Key' = 0x60
    VK_NUMPAD1:             'Key' = 0x61
    VK_NUMPAD2:             'Key' = 0x62
    VK_NUMPAD3:             'Key' = 0x63
    VK_NUMPAD4:             'Key' = 0x64
    VK_NUMPAD5:             'Key' = 0x65
    VK_NUMPAD6:             'Key' = 0x66
    VK_NUMPAD7:             'Key' = 0x67
    VK_NUMPAD8:             'Key' = 0x68
    VK_NUMPAD9:             'Key' = 0x69
    VK_MULTIPLY:            'Key' = 0x6A
    VK_ADD:                 'Key' = 0x6B
    VK_SEPARATOR:           'Key' = 0x6C
    VK_SUBTRACT:            'Key' = 0x6D
    VK_DECIMAL:             'Key' = 0x6E
    VK_DIVIDE:              'Key' = 0x6F
    VK_F1:                  'Key' = 0x70
    VK_F2:                  'Key' = 0x71
    VK_F3:                  'Key' = 0x72
    VK_F4:                  'Key' = 0x73
    VK_F5:                  'Key' = 0x74
    VK_F6:                  'Key' = 0x75
    VK_F7:                  'Key' = 0x76
    VK_F8:                  'Key' = 0x77
    VK_F9:                  'Key' = 0x78
    VK_F10:                 'Key' = 0x79
    VK_F11:                 'Key' = 0x7A
    VK_F12:                 'Key' = 0x7B
    VK_F13:                 'Key' = 0x7C
    VK_F14:                 'Key' = 0x7D
    VK_F15:                 'Key' = 0x7E
    VK_F16:                 'Key' = 0x7F
    VK_F17:                 'Key' = 0x80
    VK_F18:                 'Key' = 0x81
    VK_F19:                 'Key' = 0x82
    VK_F20:                 'Key' = 0x83
    VK_F21:                 'Key' = 0x84
    VK_F22:                 'Key' = 0x85
    VK_F23:                 'Key' = 0x86
    VK_F24:                 'Key' = 0x87
    UNUSED_88:              'Key' = 0x88
    UNUSED_89:              'Key' = 0x89
    UNUSED_8A:              'Key' = 0x8A
    UNUSED_8B:              'Key' = 0x8B
    UNUSED_8C:              'Key' = 0x8C
    UNUSED_8D:              'Key' = 0x8D
    UNUSED_8E:              'Key' = 0x8E
    UNUSED_8F:              'Key' = 0x8F
    VK_NUMLOCK:             'Key' = 0x90
    VK_SCROLL:              'Key' = 0x91
    UNKNOWN_92:             'Key' = 0x92
    UNKNOWN_93:             'Key' = 0x93
    UNKNOWN_94:             'Key' = 0x94
    UNKNOWN_95:             'Key' = 0x95
    UNKNOWN_96:             'Key' = 0x96
    UNUSED_97:              'Key' = 0x97
    UNUSED_98:              'Key' = 0x98
    UNUSED_99:              'Key' = 0x99
    UNUSED_9A:              'Key' = 0x9A
    UNUSED_9B:              'Key' = 0x9B
    UNUSED_9C:              'Key' = 0x9C
    UNUSED_9D:              'Key' = 0x9D
    UNUSED_9E:              'Key' = 0x9E
    UNUSED_9F:              'Key' = 0x9F
    VK_LSHIFT:              'Key' = 0xA0
    VK_RSHIFT:              'Key' = 0xA1
    VK_LCONTROL:            'Key' = 0xA2
    VK_RCONTROL:            'Key' = 0xA3
    VK_LMENU:               'Key' = 0xA4
    VK_RMENU:               'Key' = 0xA5
    VK_BROWSER_BACK:        'Key' = 0xA6
    VK_BROWSER_FORWARD:     'Key' = 0xA7
    VK_BROWSER_REFRESH:     'Key' = 0xA8
    VK_BROWSER_STOP:        'Key' = 0xA9
    VK_BROWSER_SEARCH:      'Key' = 0xAA
    VK_BROWSER_FAVORITES:   'Key' = 0xAB
    VK_BROWSER_HOME:        'Key' = 0xAC
    VK_VOLUME_MUTE:         'Key' = 0xAD
    VK_VOLUME_DOWN:         'Key' = 0xAE
    VK_VOLUME_UP:           'Key' = 0xAF
    VK_MEDIA_NEXT_TRACK:    'Key' = 0xB0
    VK_MEDIA_PREV_TRACK:    'Key' = 0xB1
    VK_MEDIA_STOP:          'Key' = 0xB2
    VK_MEDIA_PLAY_PAUSE:    'Key' = 0xB3
    VK_LAUNCH_MAIL:         'Key' = 0xB4
    VK_LAUNCH_MEDIA_SELECT: 'Key' = 0xB5
    VK_LAUNCH_APP1:         'Key' = 0xB6
    VK_LAUNCH_APP2:         'Key' = 0xB7
    RESERVED_B8:            'Key' = 0xB8
    RESERVED_B9:            'Key' = 0xB9
    VK_OEM_1:               'Key' = 0xBA
    VK_OEM_PLUS:            'Key' = 0xBB
    VK_OEM_COMMA:           'Key' = 0xBC
    VK_OEM_MINUS:           'Key' = 0xBD
    VK_OEM_PERIOD:          'Key' = 0xBE
    VK_OEM_2:               'Key' = 0xBF
    VK_OEM_3:               'Key' = 0xC0
    RESERVED_C1:            'Key' = 0xC1
    RESERVED_C2:            'Key' = 0xC2
    RESERVED_C3:            'Key' = 0xC3
    RESERVED_C4:            'Key' = 0xC4
    RESERVED_C5:            'Key' = 0xC5
    RESERVED_C6:            'Key' = 0xC6
    RESERVED_C7:            'Key' = 0xC7
    RESERVED_C8:            'Key' = 0xC8
    RESERVED_C9:            'Key' = 0xC9
    RESERVED_CA:            'Key' = 0xCA
    RESERVED_CB:            'Key' = 0xCB
    RESERVED_CC:            'Key' = 0xCC
    RESERVED_CD:            'Key' = 0xCD
    RESERVED_CE:            'Key' = 0xCE
    RESERVED_CF:            'Key' = 0xCF
    RESERVED_D0:            'Key' = 0xD0
    RESERVED_D1:            'Key' = 0xD1
    RESERVED_D2:            'Key' = 0xD2
    RESERVED_D3:            'Key' = 0xD3
    RESERVED_D4:            'Key' = 0xD4
    RESERVED_D5:            'Key' = 0xD5
    RESERVED_D6:            'Key' = 0xD6
    RESERVED_D7:            'Key' = 0xD7
    UNUSED_D8:              'Key' = 0xD8
    UNUSED_D9:              'Key' = 0xD9
    UNUSED_DA:              'Key' = 0xDA
    VK_OEM_4:               'Key' = 0xDB
    VK_OEM_5:               'Key' = 0xDC
    VK_OEM_6:               'Key' = 0xDD
    VK_OEM_7:               'Key' = 0xDE
    VK_OEM_8:               'Key' = 0xDF
    RESERVED_E0:            'Key' = 0xE0
    UNKNOWN_E1:             'Key' = 0xE1
    VK_OEM_102:             'Key' = 0xE2
    UNKNOWN_E3:             'Key' = 0xE3
    UNKNOWN_E4:             'Key' = 0xE4
    VK_PROCESSKEY:          'Key' = 0xE5
    UNKNOWN_E6:             'Key' = 0xE6
    VK_PACKET:              'Key' = 0xE7
    UNUSED_E8:              'Key' = 0xE8
    UNKNOWN_E9:             'Key' = 0xE9
    UNKNOWN_EA:             'Key' = 0xEA
    UNKNOWN_EB:             'Key' = 0xEB
    UNKNOWN_EC:             'Key' = 0xEC
    UNKNOWN_ED:             'Key' = 0xED
    UNKNOWN_EE:             'Key' = 0xEE
    UNKNOWN_EF:             'Key' = 0xEF
    UNKNOWN_F0:             'Key' = 0xF0
    UNKNOWN_F1:             'Key' = 0xF1
    UNKNOWN_F2:             'Key' = 0xF2
    UNKNOWN_F3:             'Key' = 0xF3
    UNKNOWN_F4:             'Key' = 0xF4
    UNKNOWN_F5:             'Key' = 0xF5
    VK_ATTN:                'Key' = 0xF6
    VK_CRSEL:               'Key' = 0xF7
    VK_EXSEL:               'Key' = 0xF8
    VK_EREOF:               'Key' = 0xF9
    VK_PLAY:                'Key' = 0xFA
    VK_ZOOM:                'Key' = 0xFB
    VK_NONAME:              'Key' = 0xFC
    VK_PA1:                 'Key' = 0xFD
    VK_OEM_CLEAR:           'Key' = 0xFE
    UNKNOWN_FF:             'Key' = 0xFF


class LinkTargetIDList:
    """Link target idlist class"""

    def __init__(self, file: BufferedReader) -> None:
        self.idlist_size: int = unpack('<H', file.read(2))[0]
        self.idlist: IDList = IDList(file.read(self.idlist_size))


class IDList:
    """Idlist class"""

    def __init__(self, data: bytes) -> None:
        file: BytesIO = BytesIO(data)
        self.item_idlist: list[ItemID] = []
        item_id: ItemID = ItemID(file)
        while item_id.item_id_size >= 2:
            self.item_idlist.append(item_id)
            item_id = ItemID(file)

        assert item_id.item_id_size == 0, item_id.item_id_size
        assert file.tell() == len(data), file.tell()


class ItemID:
    """Item id class"""

    def __init__(self, file: BufferedReader) -> None:
        self.item_id_size: int = unpack('<H', file.read(2))[0]
        self.data: bytes = file.read(self.item_id_size - 2)  # NOTE - Shellbag

# class LinkInfo:
#     """Link info class"""
#     def __init__(self, file: BufferedReader) -> None:
#         pass


class StringData:
    """String data class"""

    def __init__(self, file: BufferedReader) -> None:
        self.count_characters: int = unpack('<H', file.read(2))[0]
        print(self.count_characters)
        file.seek(0x0E, 1)
        lbpos: int = unpack('<I', file.read(4))[0]
        print(lbpos)
        size: int = self.count_characters - lbpos - 0x02
        file.seek(lbpos - 0x14, 1)
        self.string: str = file.read(size).decode()

print(readshortcut_basic(r'C:\Users\wanne\Desktop\drama-jonasfix.lnk'))
ShellLink(r'C:\Users\wanne\Desktop\drama-jonasfix.lnk')
print(readshortcut_basic(r'C:\Users\Public\Desktop\OBS Studio.lnk'))
ShellLink(r'C:\Users\Public\Desktop\OBS Studio.lnk')

