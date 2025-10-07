"""io19 functions for translating applications."""
# Linting arguments
# mypy: disable-error-code=attr-defined
# pylint: disable=too-many-branches, too-many-locals, too-many-statements

# Standard libraries
from ast import literal_eval
from builtins import __dict__
from collections.abc import Callable, Iterable
from datetime import datetime, timezone
from email.parser import HeaderParser
from gettext import NullTranslations, translation
from io import BufferedReader
from json import dump, load
from os import makedirs, unlink
from os.path import basename, dirname, exists, join
from typing import Any, Optional

# Custom libraries
from ..i18n.msgfmt import make
from .path import StrPath

NullTranslations().install()

__all__: list[str] = ['PODecodeError']
__all__ += ['gets', 'getss', 'gettext', 'json2mo', 'pot2json', 'translations']
_ID: int = 1
_STR: int = 2
_UNLINK_PO: bool = True


class PODecodeError(RuntimeError):
    """Error during portable object decoding."""


def gettext(message: str) -> str:
    """Translate message with installed translation."""
    # noinspection PyUnresolvedReferences
    return __dict__['_'](message)


def gets(
    dic: dict[str, Optional[Any]], *paths: str, default: Any = None
) -> Any:
    """Get value of nested dict."""
    if not paths:
        raise ValueError('No path specified')

    obj: dict[str, Optional[Any]] = dic
    for i, path in enumerate(paths[:-1]):
        if not isinstance(obj, dict):
            raise ValueError(
                f'Invalid type for {" > ".join(map(repr, paths[:i + 1]))}, ' +
                f'got {type(obj)}, expected {dict}'
            )

        obj = obj.get(path, {})

    return obj.get(paths[-1], default)


def _get_header(
    data: dict[str, Optional[Any]], language: str, domain: str, version: str
) -> dict[str, Optional[Any]]:
    """Get header for translation."""
    now: datetime = datetime.now(timezone.utc).astimezone()
    return {
        'title': gets(data, '', 'title', default=domain),
        'copyright': {
            'year': gets(data, '', 'copyright', 'year', default=now.year),
            'organization': gets(data, '', 'copyright', 'organization')
        },
        'first_author': {
            'full_name': gets(data, '', 'first_author', 'full_name'),
            'email_address': gets(data, '', 'first_author', 'email_address'),
            'year': gets(data, '', 'first_author', 'year', default=now.year)
        },
        'project_id_version': version,
        'pot_creation_date': now.strftime('%Y-%m-%d %H:%M%z'),
        'po_revision_date': now.strftime('%Y-%m-%d %H:%M%z'),
        'last_translator': {
            'full_name': gets(data, '', 'last_translator', 'full_name'),
            'email_address': gets(data, '', 'last_translator', 'email_address')
        },
        'language_team': {
            'language': gets(
                data, '', 'language_team', 'language', default=language
            ),
            'email_address': gets(data, '', 'language_team', 'email_address')
        }
    }


def pot2json(  # noqa: MC0001
    language_dir: StrPath, domains: list[str], version: str
) -> None:
    """Convert portable object template file to json."""
    for domain in domains:
        message_dir: str = join(language_dir, 'LC_MESSAGES')
        old_data: dict[str, Optional[Any]] = {}
        json_path: str = join(message_dir, f'{domain}.json')
        if exists(json_path):
            with open(json_path, 'rb') as file:
                new_data: Any = load(file)
                if isinstance(new_data, dict):
                    old_data = new_data

        data: dict[str, Optional[Any]] = {}
        header: dict[str, Any] = _get_header(
            old_data, basename(language_dir), domain, version
        )
        data[''] = header
        with open(join(dirname(language_dir), f'{domain}.pot'), 'rb') as file:
            lines: list[bytes] = file.readlines()

        encoding: str = 'latin-1'
        header_data: str = ''
        msgid: str = ''
        section: int = 0
        for i, line_bytes in enumerate(lines):
            line = line_bytes.decode(encoding)
            if not line.startswith('#'):
                # Not a comment
                pass
            elif section != _STR:
                # Skip comments
                continue
            elif msgid:
                # Not a header
                data[msgid] = old_data.get(msgid)
                msgid = ''
                continue
            else:
                # A header
                continue

            if line.startswith('msgctxt'):
                # msgctxt section
                raise PODecodeError(f'Line {i}: msgctxt is not supported')

            if line.startswith('msgid_plural'):
                # message with plural forms
                raise PODecodeError(f'Line {i}: msgid_plural is not supported')

            if line.startswith('msgid'):
                # msgid section
                if section != _STR:
                    pass
                elif msgid:
                    # Not a header
                    data[msgid] = old_data.get(msgid)
                    msgid = ''
                else:
                    header_parser: HeaderParser = HeaderParser()
                    charset: Optional[str] = header_parser.parsestr(
                        header_data
                    ).get_content_charset()
                    if charset:
                        encoding = charset

                section = _ID
                line = line[5:]
            elif line.startswith('msgstr['):
                # message with plural forms
                raise PODecodeError(f'Line {i}: msgstr[...] is not supported')
            elif line.startswith('msgstr'):
                # msgstr section
                if section != _ID:
                    raise PODecodeError(f'Line {i}: not preceded by msgid')

                section = _STR
                line = line[6:]

            line = line.strip()
            if not line:
                continue

            line_data: str = literal_eval(line)
            if not isinstance(line_data, str):
                raise PODecodeError(f'Line {i}: not a string')

            if section == _ID:
                msgid += line_data
            elif section != _STR:
                raise PODecodeError(f'Line {i}: not preceded by msgid')
            elif not msgid:
                header_data += line_data

        if section != _STR:
            pass
        elif msgid:
            # Not a header
            data[msgid] = old_data.get(msgid)
        for line in header_data.split('\n'):
            key: str
            value: str
            key, _1, value = line.partition(':')
            key, value = key.strip(), value.strip()
            if key == 'POT-Creation-Date':
                header[key.lower().replace('-', '_')] = value

        makedirs(message_dir, exist_ok=True)
        with open(
            join(message_dir, f'{domain}.json'), 'w', encoding='utf8'
        ) as file:
            dump(data, file, indent='\t', ensure_ascii=False)


def getss(
    dic: dict[str, Optional[Any]], *paths: str, value_type: type = str
) -> Any:
    """Get value of nested dict strict."""
    if not paths:
        raise ValueError('No path specified')

    obj: Any = dic
    for i, path in enumerate(paths):
        if not isinstance(obj, dict):
            raise ValueError(
                f'Invalid type for {" > ".join(map(repr, paths[:i + 1]))}, ' +
                f'got {type(obj)}, expected {dict}'
            )

        obj = obj.get(path)
        if obj is None:
            raise ValueError(
                f'Missing value for {" > ".join(map(repr, paths))}'
            )

    if not isinstance(obj, value_type):
        raise ValueError(
            f'Invalid type for {" > ".join(map(repr, paths))}, got ' +
            f'{type(obj)}, expected {value_type}'
        )

    return obj


def json2mo(
    language_dir: StrPath, domains: list[str], *, unlink_po: bool = _UNLINK_PO
) -> None:
    """Convert json file to machine object file."""
    for domain in domains:
        data: dict[str, Any] = {}
        message_dir: str = join(language_dir, 'LC_MESSAGES')
        with open(
            join(message_dir, f'{domain}.json'), 'r', encoding='utf8'
        ) as file:
            old_data: Any = load(file)
            if isinstance(old_data, dict):
                data = old_data

        language_path: str = join(message_dir, f'{domain}.po')
        with open(language_path, 'w', encoding='utf8') as file:
            file.write(f'''# {getss(data, '', 'title')}.
# Copyright (C) {getss(data, '', 'copyright', 'year', value_type=int)} \
{getss(data, '', 'copyright', 'organization')}
# {getss(data, '', 'first_author', 'full_name')} \
<{getss(data, '', 'first_author', 'email_address')}>, \
{getss(data, '', 'first_author', 'year', value_type=int)}.
#
msgid ''
msgstr ''
'Project-Id-Version: {getss(data, '', 'project_id_version')}\\n'
'POT-Creation-Date: {getss(data, '', 'pot_creation_date')}\\n'
'PO-Revision-Date: {getss(data, '', 'po_revision_date')}\\n'
'Last-Translator: {getss(data, '', 'last_translator', 'full_name')} \
{getss(data, '', 'last_translator', 'email_address')}\\n'
'Language-Team: {getss(data, '', 'language_team', 'language')} \
<{getss(data, '', 'language_team', 'email_address')}>\\n'
'Content-Type: text/plain; charset=utf8\\n'
''')
            for msgid in data:
                if msgid:
                    file.write(f'\n\nmsgid {msgid!r}\nmsgstr ')
                    file.write(f'{getss(data, msgid)!r}')

        make(language_path, join(message_dir, f'{domain}.mo'))
        if unlink_po:
            unlink(language_path)


def translations(
    domains: Iterable[str], localedir: Optional[StrPath] = None,
    languages: Optional[Iterable[str]] = None,
    class_: Optional[Callable[[BufferedReader], NullTranslations]] = None,
    fallback: bool = True
) -> NullTranslations:
    """Get translations for all domains."""
    old_translation: NullTranslations = NullTranslations()
    for domain in domains:
        new_translation: NullTranslations = translation(
            domain, localedir=localedir, languages=languages, class_=class_,
            fallback=fallback
        )
        new_translation.add_fallback(old_translation)
        old_translation = new_translation

    return old_translation
