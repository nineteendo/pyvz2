#!/usr/bin/env python
"""
Python Vs. Zombies 2, a command-line utility to modify Plants Vs. Zombies 2.

Python 3.8- is not supported & won't receive bug fixes.
"""
# TODO - Separate thread to display text
# TODO - Implement progress bar (sub class of InputEvent)
# TODO - Make tutorial for Mac
# TODO - Make translated tutorials
# TODO - Implement dict & list input
# TODO - Visual feedback for check update

# Linting arguments
# mypy: disable-error-code="assignment, misc"
# pylint: disable=broad-except

# Standard libraries
import sys
from argparse import ArgumentParser, Namespace
from collections.abc import Callable
from datetime import date
from hashlib import md5
from json import JSONDecodeError, dump
from logging import DEBUG, Formatter, basicConfig, critical, exception, info
from logging.handlers import RotatingFileHandler
from os import getcwd, listdir
from os.path import basename, isdir, join
from pathlib import Path
from sys import executable
from threading import Thread
from typing import Any, Optional, Union
from webbrowser import open as display_url

# Custom libraries
from lib.io19 import open_path
from lib.io19.input import (
    Exit, Info, category, demo, dict_picker, entities, input_bool, input_event,
    input_path, input_str, sequence_picker, shortcuts,
)
from lib.io19.load_data import load_dict, load_json
from lib.io19.path import StrPath, edit, run, use_main_dir
from lib.io19.translate import PODecodeError
from lib.io19.translate import gettext as _
from lib.io19.translate import json2mo, pot2json, translations
from lib.io19.update import STATUS_SCHEMA, check_update

__all__: list[str] = []
_LOCALE_DIR: str = 'locales'
_LOG_DIR: str = 'logs'
_LOGGING_FORMAT: str = '%(asctime)s - %(levelname)s - %(message)s'
_LOG_SIZE: int = 5 * 1024 * 1024
_SETTINGS_SCHEMA: dict[str, tuple[type, Any]] = {
    'auto_check_update': (bool, True),
    'encryption_key': (str, '00000000000000000000000000000000'),
    'language': (str, 'en')
}
_TOOLS: dict[str, Callable[..., None]] = {
    'open': open_path
}
_VERSION: str = 'v1.2.2c-alpha'

ShortUrl = Callable[[str], str]

android_app: ShortUrl = lambda i: f'play.google.com/store/apps/details?id={i}'
ernestoam: ShortUrl = lambda wiki: f'ernestoam.fandom.com/wiki/{wiki}'
settings: dict[str, Any] = {}
status: dict[str, Any] = {}
update_settings: dict[str, Any] = {
    'branch': 'beta',
    'message': 'Beta 1.2.2c fixed patching, json encode & progressbar',
    'owner': 'nineteendo',
    'release': False,
    'repo': 'pvz2tools',
    'tag_name': 'v1.0.0'
}
yt_video: ShortUrl = lambda video_id: f'www.youtube.com/watch?v={video_id}'
yt_list: ShortUrl = lambda list_id: f'www.youtube.com/playlist?list={list_id}'


def release_notes() -> None:
    """Show release notes."""
    sequence_picker(_('Release notes: {0}').format(_VERSION), [
        'Addded a menu',
        'Added internationalization',
        'Added jsonpatchwork',
        'Improved logging',
        'Made input more user-friendly',
        'Refactored codebase'
    ], clear=True)


def credits_menu() -> None:
    """Show the credits."""
    dict_picker(_('Credits'), {
        **category(_('Developer')),
        **entities('Nice Zombies'),
        **category(_('Libraries')),
        _('i18n by 1'):        'Barry Warsaw, Marc-Andre Lemburg',
        _('i18n by 2'):        'Martin v. Lowis',
        _('io19 by'):          'Nice Zombies',
        _('jsonpatchwork by'): 'Nice Zombies',
        _('natsortof by'):     'Nice Zombies',
        _('py3rijndael by'):   'meyt',
        _('rtonoff by'):       'Nice Zombies',
        **category(_('Code based on')),
        _('1bsr_pgsr.bms by'): 'Luigi Auriemma',
        _('RTONCrypto by'):    'Small Pea',
        _('RTONParser by'):    '1Zulu',
        **category(_('Reverse enineering')),
        _('RSB-format'):       'Watto Studios & TwinKleS-C',
        _('RTON-format'):      'H3x4n1um',
        _('SMF-format'):       'YingFengTingYu',
        **category(_('Inspired by')),
        _('jsonpatch by'):     'Mark Nottingham & Paul C. Bryan',
        _('natsort by'):       'SethMMorton',
        _('yo by'):            'yeoman',
        **category(_('Advisors')),
        **entities('Haruma, NoB, PPP & Sarah Lydia'),
        **category(_('Translators')),
        **entities('Nice Zombies'),
        **category(_('Bug reporters')),
        **entities(
            'Aeziz, dekiel123, Drazzii, ErnestoAM',
            'fake the lawn server member, farhan, Haruma, Icy Studio, Im 12',
            'Jonas Boeykens, maiakiaka, mutaqin-hanif, NoB, plant16gamer',
            'qnmakingstupidstuff, Sarah Lydia & SodiumDoesStuff'
        )
    }, clear=True)


def pyvz2_github(path: str) -> str:
    """Get PyVZ2 GitHub url."""
    return (
        f'github.com/{update_settings["owner"]}/{update_settings["repo"]}/' +
        f'{path}'
    )


def download_page() -> str:
    """Get GitHub download page."""
    if update_settings['release']:
        return 'releases/latest'

    return f'archive/refs/heads/{update_settings["branch"]}.zip'


def display_url_from_key(key: str) -> bool:
    """Display url from locale key."""
    return display_url('https://' + {
        _('Branches'): pyvz2_github('branches'),
        _('Changelog'): pyvz2_github('blob/master/changelog.md'),
        _('Donate'): 'www.paypal.com/paypalme/nineteendo',
        _('Install BlueStacks'): 'www.bluestacks.com/download.html',
        _('Install PvZ2'): android_app('com.ea.game.pvz2_row'),
        _('Install QuickEdit'): android_app('com.rhmsoft.edit'),
        _('Install Visual Studio Code'): 'code.visualstudio.com/Download',
        _('Issues'): pyvz2_github('issues'),
        _('Join us on Discord'): 'discord.com/invite/CVZdcGKVSw',
        _('Download update'): pyvz2_github(download_page()),
        _('License'): pyvz2_github('blob/master/LICENSE'),
        _('Make pull request'): pyvz2_github('compare'),
        _('Milestones'): pyvz2_github('milestones'),
        _('Readme'): pyvz2_github('blob/master/README.md'),
        _('Releases'): pyvz2_github('releases'),
        _('Report issue'): pyvz2_github('issues/new'),
        _('Search suggestions'): pyvz2_github('labels/enhancement'),
        _('Fork repository'): pyvz2_github('fork'),
        _('Tips & tricks'): ernestoam('Plants_vs._Zombies_2_Hacking_Guide'),
        _('Video tutorials'): yt_list(_('PLn00gyIpKcgKp7zVLZldwUtmk-3B9wWP8')),
        _('Watch tutorial (Android)'): yt_video(_('YBrmMYZGD3k')),
        _('Watch tutorial (Windows)'): yt_video(_('LJ4qC6wHfUA'))
    }[key])


def update_language() -> None:
    """Update language & save settings."""
    save_settings()
    translations(
        ['io19', 'pyvz2'], localedir=_LOCALE_DIR,
        languages=[settings['language']]
    ).install()


def save_settings() -> None:
    """Save settings."""
    with open('settings.json', 'w', encoding='utf8') as file:
        dump(settings, file, indent='\t')


def save_status() -> None:
    """Save status."""
    with open('status.json', 'w', encoding='utf8') as file:
        dump(status, file, indent='\t')


def setup() -> None:
    """Load & save settings & status."""
    settings.update(load_json('settings.json', _SETTINGS_SCHEMA))
    update_language()
    status.update(load_json('status.json', STATUS_SCHEMA))
    save_status()


def tools_menu() -> None:
    """Open tools menu."""
    tool: Optional[Union[Exit[str], str]] = None
    while True:
        tool = dict_picker(_('Tools'), {
            0: _('File manager'),
            1: Exit(_('Back'))
        }, clear=True, value=tool)
        if tool is None or isinstance(tool, Exit):
            return None

        if tool == _('File manager'):
            open_path('~')


def general_settings_menu() -> None:
    """Open general settings menu."""
    answer: Optional[Union[Exit[str], str]] = None
    while True:
        answer = dict_picker(_('General'), {
            0: _('Encryption key'),
            1: Exit(_('Back'))
        }, clear=True, value=answer)
        if answer is None or isinstance(answer, Exit):
            return None

        if answer == _('Encryption key'):
            encryption_key: Optional[str] = input_str(
                _('Enter encryption key:'), hide=True
            )
            if isinstance(encryption_key, str):
                settings['encryption_key'] = md5(
                    encryption_key.encode()
                ).hexdigest()  # nosec B324

        save_settings()


def make_translation_menu(language_dir: StrPath) -> None:
    """Open make translation menu."""
    answer: Optional[Union[Exit[str], str]] = None
    while True:
        answer = dict_picker(
            _('Make translation for {0}').format(basename(language_dir)), {
                0: _('Open {0}.json in external editor').format('io19'),
                1: _('Open {0}.json in external editor').format('pyvz2'),
                2: _('Generate translation'),
                3: Exit(_('Back'))
            }, clear=True, value=answer
        )
        if answer is None or isinstance(answer, Exit):
            return None

        try:
            if answer == _('Open {0}.json in external editor').format('io19'):
                edit(join(language_dir, 'LC_MESSAGES', 'io19.json'))
            elif answer == _('Open {0}.json in external editor').format(
                'pyvz2'
            ):
                edit(join(language_dir, 'LC_MESSAGES', 'pyvz2.json'))
            elif answer == _('Generate translation'):
                return json2mo(language_dir, ['io19', 'pyvz2'])
        except (FileNotFoundError, JSONDecodeError, ValueError) as err:
            exception(err)
            input_event(err, clear=True)


def contribute_translation_menu() -> None:
    """Open contribute translation menu."""
    answer: Optional[Union[Exit[str], str]] = None
    while True:
        answer = dict_picker(_('Contribute translation'), {
            0: _('Fork repository'),
            1: _('Upload locales directory'),
            2: _('Make pull request'),
            3: Exit(_('Back'))
        }, clear=True, value=answer)
        if answer is None or isinstance(answer, Exit):
            return None

        if answer == _('Upload locales directory'):
            edit('locales')
        else:
            display_url_from_key(answer)


def language_menu() -> None:  # noqa: MC0001
    """Open language menu."""
    answer: Optional[Union[Exit[str], str]] = None
    while True:
        answer = dict_picker(_('Language'), {
            0: _('Change language'),
            1: _('Make translation'),
            2: _('Contribute translation'),
            3: Exit(_('Back'))
        }, clear=True, value=answer)
        if answer is None or isinstance(answer, Exit):
            return None

        try:
            if answer == _('Change language'):
                language: Optional[str] = sequence_picker(
                    _('Select language:'), sorted(['en'] + list(filter(
                        lambda i: isdir(join(_LOCALE_DIR, i)),
                        listdir(_LOCALE_DIR))
                    )), clear=True, make_lowercase=True,
                    value=settings['language']
                )
                if isinstance(language, str):
                    settings['language'] = language
                    update_language()
                    answer = _('Change language')  # Update language
            elif answer == _('Make translation'):
                language_dir: Optional[Path] = input_path(
                    _('Choose language directory:'), _LOCALE_DIR,
                    allow_create=True, clear=True, dirs_only=True,
                    sub_dirs=False
                )
                if language_dir is None:
                    continue

                if not getattr(sys, 'frozen', False):
                    pygettext: str = join('lib', 'i18n', 'pygettext.py')
                    run([
                        executable, pygettext, '-d', join(_LOCALE_DIR, 'io19'),
                        join(_LOCALE_DIR, 'io19.pot'), join('lib', 'io19')
                    ])
                    run([
                        executable, pygettext, '-d',
                        join(_LOCALE_DIR, 'pyvz2'),
                        join(_LOCALE_DIR, 'pyvz2.pot'), 'pyvz2.py'
                    ])

                pot2json(language_dir, ['io19', 'pyvz2'], _VERSION)
                make_translation_menu(language_dir)
            elif answer == _('Contribute translation'):
                contribute_translation_menu()
        except (
            JSONDecodeError, PermissionError, PODecodeError, ValueError
        ) as err:
            exception(err)
            input_event(err, clear=True)


def update_settings_menu() -> None:
    """Open update settings menu."""
    answer: Optional[Union[Exit[str], str]] = None
    while True:
        answer = dict_picker(_('Update'), {
            0: _('Check for updates'),
            **({1: _('Download update')} if status['outdated'] else {}),
            2: _('Auto check update'),
            3: Exit(_('Back'))
        }, clear=True, value=answer)
        if answer is None or isinstance(answer, Exit):
            return None

        if answer == _('Check for updates'):
            check_update(update_settings, status, save_status)
        elif answer == _('Auto check update'):
            auto_check_update: Optional[bool] = input_bool(
                _('Auto check update'), clear=True,
                value=settings['auto_check_update']
            )
            if isinstance(auto_check_update, bool):
                settings['auto_check_update'] = auto_check_update
                save_settings()
        else:
            display_url_from_key(answer)


def settings_menu() -> None:  # noqa: MC0001
    """Open settings menu."""
    answer: Optional[Union[Exit[str], str]] = None
    while True:
        answer = dict_picker(_('Settings'), {
            0: _('General'),
            1: _('Language'),
            2: _('Configurations'),
            3: _('Update'),
            **category(''),
            4: _('Open in default program'),
            5: _('Import'),
            6: _('Reset'),
            **category(''),
            7: Exit(_('Back'))
        }, clear=True, value=answer)
        if answer is None or isinstance(answer, Exit):
            return None

        try:
            if answer == _('General'):
                general_settings_menu()
            elif answer == _('Language'):
                language_menu()
                answer = _('Language')  # Update language
            elif answer == _('Configurations'):
                config_dir: Optional[Path] = input_path(
                    _('Choose config directory:'), 'configs',
                    clear=True, dirs_only=True, sub_dirs=False
                )
                if isinstance(config_dir, Path):
                    open_path(config_dir, all_dirs=False)
            elif answer == _('Update'):
                update_settings_menu()
            elif answer == _('Open in default program'):
                edit('settings.json')
                input_event(_('Press any key to reload settings'), clear=True)
                setup()
                answer = _('Open in default program')  # Update language
            elif answer == _('Import'):
                source: Optional[Path] = input_path(
                    _('Select source'), '', clear=True, files_only=True,
                    file_extensions=('.json',)
                )
                if isinstance(source, Path):
                    settings.update(load_json(
                        source, _SETTINGS_SCHEMA, strict=True
                    ))
                    update_language()
                    answer = _('Import')  # Update language
            elif answer == _('Reset'):
                settings.update(load_dict(_SETTINGS_SCHEMA, {}))
                update_language()
                answer = _('Reset')  # Update language
        except JSONDecodeError as err:
            exception(err)
            input_event(err, clear=True)


def get_started_menu() -> None:
    """Open get started menu."""
    answer: Optional[Union[Exit[str], str]] = None
    while True:
        answer = dict_picker(_('Get started'), {
            'a':  Info(_('Android')),
            'a0': _('Install PvZ2'),
            'a1': _('Install QuickEdit'),
            'b':  Info(_('PC')),
            'b0': _('Install Visual Studio Code'),
            'b1': _('Install BlueStacks'),
            'c':  Info(_('Tutorial')),
            'c0': _('Watch tutorial (Android)'),
            'c1': _('Watch tutorial (Windows)'),
            'c2': Info(_('Watch tutorial (Mac)')),
            'd':  Info(_('Back')),
            'd0': Exit(_('Back'))
        }, clear=True, value=answer)
        if answer is None or isinstance(answer, Exit):
            return None

        display_url_from_key(answer)


def help_menu() -> None:
    """Open help menu."""
    answer: Optional[Union[Exit[str], str]] = None
    while True:
        answer = dict_picker(_('Help'), {
            0:   _('Get started'),
            1:   _('Keyboard shortcuts reference'),
            2:   _('Video tutorials'),
            3:   _('Tips & tricks'),
            **category(''),
            4:   _('Join us on Discord'),
            5:   _('Search suggestions'),
            6:   _('Report issue'),
            7:   _('Open log'),
            **category(''),
            8:   _('Donate'),
            9:   _('Fork repository'),
            'a': _('Make pull request'),
            **category(''),
            'b': Exit(_('Back'))
        }, clear=True, value=answer)
        if answer is None or isinstance(answer, Exit):
            return None

        if answer == _('Get started'):
            get_started_menu()
        elif answer == _('Keyboard shortcuts reference'):
            shortcuts()
        elif answer == _('Open log'):
            edit(join('logs', 'pyvz2.log'))
        else:
            display_url_from_key(answer)


def about_menu() -> None:
    """Open about menu."""
    answer: Optional[Union[Exit[str], str]] = None
    while True:
        answer = dict_picker(_('About'), {
            0: _('Credits'),
            1: _('Release notes'),
            **category(''),
            2: _('Branches'),
            3: _('Changelog'),
            4: _('License'),
            5: _('Issues'),
            6: _('Milestones'),
            7: _('Readme'),
            8: _('Releases'),
            **category(''),
            9: Exit(_('Back'))
        }, clear=True, value=answer)
        if answer is None or isinstance(answer, Exit):
            return None

        if answer == _('Credits'):
            credits_menu()
        elif answer == _('Release notes'):
            release_notes()
        else:
            display_url_from_key(answer)


def main_menu() -> None:  # noqa: MC0001
    """Open main menu."""
    if status['skipped_update']:
        pass
    elif status['outdated']:
        if dict_picker(_('New update available'), {
            0: Exit(_('Close')),
            1: _('Update')
        }, clear=True) == _('Update'):
            display_url_from_key(_('Download update'))

        status['skipped_update'] = True
        save_status()
    elif (
        settings['auto_check_update'] and
        date.today().strftime('%Y-%m-%d') != status['last_checked_update']
    ):
        Thread(target=check_update, args=(
            update_settings, status, save_status
        ), daemon=True).start()

    answer: Optional[Union[Exit[str], str]] = None
    while True:
        answer = dict_picker(_('Main menu'), {
            0: _('Tools'),
            1: _('Demo'),
            2: _('Settings'),
            3: _('Help'),
            4: _('About'),
            5: Exit(_('Exit'))
        }, clear=True, value=answer)
        if answer is None or isinstance(answer, Exit):
            return None

        if answer == _('Tools'):
            tools_menu()
        elif answer == _('Demo'):
            demo()
        elif answer == _('Settings'):
            settings_menu()
            answer = _('Settings')  # Update language
        elif answer == _('Help'):
            help_menu()
        elif answer == _('About'):
            about_menu()


def main() -> None:
    """Start PyVZ2."""
    cwd: str = getcwd()
    use_main_dir()
    file_handler: RotatingFileHandler = RotatingFileHandler(
        join(_LOG_DIR, 'pyvz2.log'), maxBytes=_LOG_SIZE, backupCount=1
    )
    file_handler.setFormatter(Formatter(_LOGGING_FORMAT))
    basicConfig(level=DEBUG, handlers=[file_handler])
    info('Program started')
    setup()
    parser: ArgumentParser = ArgumentParser(
        description='Python 3 tool for modifying Plants Vs. Zombies 2'
    )
    parser.add_argument('tool', nargs='?', choices=_TOOLS)
    parser.add_argument('path', nargs='?')
    parser.add_argument(
        '-V', '--version', action='version', version=f'%(prog)s {_VERSION}'
    )
    args: Namespace = parser.parse_args()
    try:
        tool: Optional[str] = args.tool
        path: Optional[str] = args.path
        if tool is None:
            main_menu()
        elif path is None:
            parser.error(f'{tool} requires a path')
        else:
            _TOOLS[tool](join(cwd, path))
    except (Exception, GeneratorExit) as err:
        critical(err, exc_info=True)
        input_event(err)
    except KeyboardInterrupt:
        # We're not interested in displaying KeyboardInterrupt
        pass


if __name__ == '__main__':
    main()
