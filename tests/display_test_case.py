"""Base for tests of what the rules send to the display.

Connects MPF's mock BCP client as `local_display`, the connection name the
widget and slide players send to, and records every message.
"""
from tests.test_act_one import ActOneTestCase


class DisplayTestCase(ActOneTestCase):

    def get_use_bcp(self):
        return True

    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.machine_config_patches["bcp"] = {
            "connections": {"local_display": {"type": "mpf.tests.MpfBcpTestCase.MockBcpClient"}},
            "servers": []}

    def setUp(self):
        super().setUp()
        self.sent = []

    def drain_display(self):
        """Move everything MPF has sent to the display into self.sent."""
        client = self.machine.bcp.transport.get_named_client("local_display")
        while not client.send_queue.empty():
            self.sent.append(client.send_queue.get_nowait())
        return self.sent

    def widgets_played(self):
        """Return (widget name, context, settings) for every widget played."""
        played = []
        for cmd, args in self.drain_display():
            if cmd == "trigger" and args.get("name") == "widgets_play":
                for name, settings in args.get("settings", {}).items():
                    played.append((name, args.get("context"), settings))
        return played

    def contexts_cleared(self):
        return [args.get("context") for cmd, args in self.drain_display()
                if cmd == "trigger" and args.get("name") == "widgets_clear"]
