"""19.io functions for checking for updates."""
# Standard libraries
from collections.abc import Callable
from datetime import date
from http.client import HTTPResponse
from json import load
from logging import warning
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

__all__: list[str] = ['STATUS_SCHEMA']
__all__ += ['check_update', 'github_api_call']

STATUS_SCHEMA: dict[str, tuple[type, Any]] = {
    'last_checked_update': (str, '1970-01-01'),
    'outdated': (bool, False),
    'skipped_update': (bool, False)
}


def github_api_call(*path: str) -> HTTPResponse:
    """Make GitHub API call with the specified path."""
    return urlopen(f'https://api.github.com/{"/".join(path)}')  # nosec B310


def check_update(
    update_settings: dict[str, Any], status: dict[str, Any],
    update_status: Callable[[], None]
) -> None:
    """Check for update on GitHub."""
    status['last_checked_update'] = date.today().strftime('%Y-%m-%d')
    owner: str = update_settings['owner']
    repo: str = update_settings['repo']
    branch: str = update_settings['branch']
    try:
        status['skipped_update'] = status['outdated']
        if update_settings['release']:
            with github_api_call(
                'repos', owner, repo, 'releases', 'latest'
            ) as response:
                tag_name: str = load(response)['tag_name']
                status['outdated'] = update_settings['tag_name'] != tag_name
        else:
            with github_api_call(
                'repos', owner, repo, 'branches', branch
            ) as response:
                message: str = (
                    load(response)['commit']['commit']['message']
                ).partition('\n\n')[0]
                status['outdated'] = update_settings['message'] != message

        update_status()
    except URLError as err:
        warning(err)
