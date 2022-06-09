import os
import sys
import json
import requests
import websocket
import threading
from time import time
from base64 import b64decode
from datetime import datetime

if sys.platform == "linux":
    os.system("clear")
else:
    os.system("cls")

class Discord(websocket.WebSocketApp):

    def __init__(self):
        self.timestamp = lambda: str(datetime.fromtimestamp(time())).split(" ")[1]

        self.token = None
        self.guild = None
        self.vanity = None

        self._guilds = {}

        self.socket_headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0"
        }

        super().__init__("wss://gateway.discord.gg/?encoding=json&v=9",
            header=self.socket_headers,
            on_open=lambda ws: self.sock_open(ws),
            on_message=lambda ws, msg: self.sock_message(ws, msg),
            on_close=lambda ws, close_code, close_msg: self.sock_close(
                ws, close_code, close_msg)
        )

    def get_token_id(self):
        try:
            return b64decode(self.token.split(".")[0].encode()).decode()
        except:
            return "0" * 18

    def log(self, text: str, value: str):
        print("\x1b[38;2;73;73;73m[\x1b[0m%s\x1b[38;2;73;73;73m]\x1b[0m %s \x1b[38;2;73;73;73m%s\x1b[0m" % (self.timestamp(), text, value))

    def update_vanity(self):
        headers = {
            "authorization": self.token,
            "content-type": "application/json",
        }

        response = requests.patch("https://ptb.discord.com/api/v9/guilds/%s/vanity-url" % (self.guild), json={"code": self.vanity}, headers=headers)
        if response.status_code == 200:
            self.log("Successfully claimed", self.vanity)
            return self.close()
        else:
            self.log("Failed to update vanity.", "")

    def heartbeat_thread(self, interval):
        try:
            while True:
                if self.verbose: self.log("Sent heartbeat")
                self.send(json.dumps({
                    "op": 1,
                    "d": str(self.packets)
                }))
                time.sleep(interval)
        except Exception:
            return

    def sock_open(self, ws):
        self.send(json.dumps({
            "op": 2,
            "d": {
                "token": self.token,
                "capabilities": 125,
                "properties": {
                "os": "Windows",
                "browser": "Firefox",
                "device": "",
                "system_locale": "en-US",
                "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0",
                "browser_version": "94.0",
                "os_version": "10",
                "referrer": "",
                "referring_domain": "",
                "referrer_current": "",
                "referring_domain_current": "",
                "release_channel": "stable",
                "client_build_number": 103981,
                "client_event_source": None
            },
            "presence": {
                "status": "online",
                "since": 0,
                "activities": [],
                "afk": False
            },
            "compress": False,
                "client_state": {
                    "guild_hashes": {},
                    "highest_last_message_id": "0",
                    "read_state_version": 0,
                    "user_guild_settings_version": -1,
                    "user_settings_version": -1
                }
            }
        }))
        self.log("Sent authentication payload with", self.get_token_id())

    def sock_message(self, ws, message):
        decoded = json.loads(message)

        if decoded == None:
            return

        if decoded["op"] == 10:
            threading.Thread(target=self.heartbeat_thread, args=(decoded["d"]["heartbeat_interval"] / 1000,), daemon=True).start()

        if decoded["t"] == "READY":
            self.log("Successfully connected to", self.get_token_id())
            for guild in decoded["d"]["guilds"]:
                self._guilds[guild["id"]] = {"name": guild["name"], "member_count": guild["member_count"]}

            if not self.guild in self._guilds:
                self.log("You are not inside", self.guild)
                self.close()

        if decoded["t"] == "GUILD_UPDATE":
            guild = decoded["d"]["id"]
            vanity_url = decoded["d"]["vanity_url_code"]
            if guild == self.guild:
                if vanity_url != self.vanity:
                    self.log("%s has updated their vanity to" % (decoded["d"]["name"]), vanity_url)
                    self.update_vanity()

    def sock_close(self, ws, close_code, close_msg):
        if self.verbose: self.log("An error has occured", close_msg)
        return False

    def run(self):
        self.token = input("\x1b[38;2;73;73;73m[\x1b[0m%s\x1b[38;2;73;73;73m]\x1b[0m Token\x1b[38;2;73;73;73m:\x1b[0m " % (self.timestamp()))
        self.guild = input("\x1b[38;2;73;73;73m[\x1b[0m%s\x1b[38;2;73;73;73m]\x1b[0m Guild\x1b[38;2;73;73;73m:\x1b[0m " % (self.timestamp()))
        self.vanity = input("\x1b[38;2;73;73;73m[\x1b[0m%s\x1b[38;2;73;73;73m]\x1b[0m Vanity\x1b[38;2;73;73;73m:\x1b[0m " % (self.timestamp()))

        print()
        self.run_forever()

if __name__ == "__main__":
    Discord().run()
