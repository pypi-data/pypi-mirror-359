# logbuch/integrations/__init__.py

from .github_gists import GitHubGistManager, GistError
from .smart_suggestions import SmartSuggestionEngine

try:
    from .cloud_sync import CloudSyncManager, CloudProvider
except ImportError:
    CloudSyncManager = None
    CloudProvider = None

try:
    from .webhook_server import WebhookServer
except ImportError:
    WebhookServer = None

__all__ = [
    'GitHubGistManager',
    'GistError',
    'SmartSuggestionEngine'
]

if CloudSyncManager:
    __all__.extend(['CloudSyncManager', 'CloudProvider'])

if WebhookServer:
    __all__.append('WebhookServer')
