import logging
import subprocess

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.event import KeywordQueryEvent

logger = logging.getLogger(__name__)


class SystemManagementDirect(Extension):
    def __init__(self):
        logger.info("Loading Gnome Settings Extension")
        super(SystemManagementDirect, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    def __init__(self):
        self._commands = {
            "lock-screen": [["loginctl", "lock-session"]],
            "suspend": [["loginctl", "lock-session"],
                        ["systemctl", "suspend", "-i"]],
            "naptime": [["systemctl", "suspend", "-i"]],
            "shutdown": [["systemctl", "poweroff", "-i"]],
            "restart": [["systemctl", "reboot", "-i"]],
            "logout": [["bash", "-c", "sleep 1 && pkill -KILL -u $USER"]],
            "safe-logout": [["bash", "-c", "sleep 1 && loginctl terminate-session $(loginctl session-status | head -1 | awk '{print $1}')"]]  # noqa
        }
        super().__init__()
        
    def on_event(self, event, extension):
        keyword = event.get_keyword()

        # Find the keyword id using the keyword (since the keyword can be changed by users)
        for id, kw in extension.preferences.items():
            if kw == keyword:
                self.on_match(id)
                return HideWindowAction()
        return None

    def on_match(self, id):
        commands = self._commands.get(id, None)
        if not commands:
            return
        
        for cmd in commands:
            subprocess.Popen(cmd)
            

SystemManagementDirect().run()
