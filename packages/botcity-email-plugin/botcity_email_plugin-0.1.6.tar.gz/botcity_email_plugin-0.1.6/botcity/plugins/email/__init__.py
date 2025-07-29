from . import _version
from .plugin import BotEmailPlugin, MailFilters
from .servers_config import MailServers

__version__ = _version.get_versions()['version']
