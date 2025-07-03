import asyncio
import re
import sys
import zlib
import websockets
import json
import random
import aiohttp
from enum import Enum
from typing import Optional, Dict, Any, List, Callable, Coroutine

# --------------- fast json ------------------------------------------- #
try:
    import orjson
    jloads = orjson.loads
    jdumps = orjson.dumps
except ImportError:
    jloads = json.loads
    jdumps = json.dumps

ZLIB_END = b"\x00\x00\xff\xff"
ROBLOX_MARK = b"roblox.com/groups/"
GROUP_RE = re.compile(rb"roblox\.com/groups/(\d+)")
INTENTS = (1 << 9) | (1 << 12) | (1 << 15)  # Message Content + Direct Messages + Guild Messages

class Restart(Enum):
    RESUME = 1
    IDENTIFY = 2
    RETRY_LATER = 3  # op 9, resumable = False

class DiscordBot:
    def __init__(
        self,
        token: str,
        prefix: Optional[str] = "--",
        bot: Optional[bool] = False,
        log_webhook: Optional[str] = None,
        channel_ids: Optional[List[int]] = None,
    ):
        """Initializes the bot with proper zlib handling."""
        self.session_id: Optional[str] = None
        self.heartbeat_interval: float = 30.0
        self.seq_num: Optional[int] = None
        self.resume_url: Optional[str] = None
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.started: bool = False
        self.token: str = f"{'Bot ' if bot else ''}{token}"
        self.prefix: str = prefix
        self.log_webhook: Optional[str] = log_webhook
        self.userid: Optional[str] = None
        self.groupsids: List[str] = []
        self.groupsid: Optional[str] = None
        self.heartbeat_task: Optional[asyncio.Task] = None
        self._running = True
        self.decomp: Optional[zlib._Decompress] = None
        self.buf: bytearray = bytearray()
        self.restart_state = Restart.IDENTIFY
        self.backoff = 1.0
        self.group_handlers: List[Callable[[str], Coroutine[Any, Any, None]]] = [] # type: ignore
        self.channel_ids = {int(c) for c in channel_ids} if channel_ids else set()
        self._connection_open = False
        self._connection_lock = asyncio.Lock()

    def on_group(self, func: Callable[[str], Coroutine[Any, Any, None]]):
        """Decorator to register group handler functions."""
        self.group_handlers.append(func)
        return func

    def _is_ws_open(self) -> bool:
        if not self._connection_open or self.ws is None:
            return False
        return True

    async def send_startup_embed(self):
        """Sends startup embed using asynchronous HTTP client."""
        if not self.log_webhook:
            return
            
        embed = {
            "username": "TK Claimer 7.0",
            "embeds": [
                {
                    "title": "TK Claimer 7.0",
                    "description": "Claimer started. Waiting for groups now.",
                    "footer": {
                        "text": "I feel dizzy 🥹🤭",
                        "icon_url": "https://cdn.discordapp.com/avatars/1058766073568174231/e05509a85a378ed3fc8c7e7274cbfcd7.webp?size=1024&format=webp&width=0&height=256",
                    },
                }
            ],
        }
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(self.log_webhook, json=embed)
        except Exception as e:
            print(f"Failed to send startup embed: {e}")

    async def _recv_json(self) -> Dict[str, Any]:
        """Receives and decompresses messages with zlib."""
        if not self._is_ws_open():
            return {}
            
        try:
            message = await self.ws.recv()
            if isinstance(message, str):
                return jloads(message.encode())
            
            self.buf.extend(message)
            if len(self.buf) < 4 or self.buf[-4:] != ZLIB_END:
                return {}
            
            decompressed = self.decomp.decompress(self.buf)
            self.buf.clear()
            return jloads(decompressed)
        except websockets.ConnectionClosed as e:
            print(f"Connection closed during receive: {e.code} - {e.reason}")
            self._connection_open = False
            return {}
        except Exception as e:
            print(f"Receive error: {e}")
            return {}

    async def send_heartbeat(self):
        """Sends heartbeat with proper interval management."""
        try:
            while self._running:
                await asyncio.sleep(self.heartbeat_interval)
                
                if not self._is_ws_open() or not self._running:
                    break
                    
                try:
                    await self.ws.send(jdumps({"op": 1, "d": self.seq_num}))
                except websockets.ConnectionClosed:
                    self._connection_open = False
                    break
                except Exception as e:
                    print(f"Heartbeat send error: {e}")
                    break
        except asyncio.CancelledError:
            pass

    async def on_message(self, data: Dict[str, Any]):
        """Handles gateway events with proper decompression."""
        if not data:
            return
            
        try:
            if "s" in data:
                self.seq_num = data["s"]
                
            op = data.get("op")
            event_type = data.get("t")
            
            # Handle critical operations
            if op == 7:  # Reconnect
                print("Received reconnect request (OP 7)")
                self.restart_state = Restart.RESUME
                await self.close_connection()
                return
            elif op == 9:  # Invalid session
                print("Received invalid session notification (OP 9)")
                self.restart_state = Restart.RETRY_LATER
                if not data.get("d", False):
                    self.session_id = None
                    self.resume_url = None
                await self.close_connection()
                return
            elif op == 10:  # Hello
                print("Received hello (OP 10)")
                self.heartbeat_interval = data["d"]["heartbeat_interval"] / 1000
                if self.heartbeat_task:
                    self.heartbeat_task.cancel()
                self.heartbeat_task = asyncio.create_task(self.send_heartbeat())
                return
            
            # Handle events
            if event_type == "READY":
                self._handle_ready_event(data)
            elif event_type == "MESSAGE_CREATE":
                await self._handle_message_event(data)
                
        except Exception as e:
            print(f"Error processing event: {e}")

    def _handle_ready_event(self, data: Dict[str, Any]):
        """Processes READY event and initializes session."""
        self.session_id = data["d"]["session_id"]
        self.resume_url = data["d"]["resume_gateway_url"]
        self.userid = data["d"]["user"]["id"]
        
        print(f"🚀 Logged in as {data['d']['user']['username']}")
        print(f"🔗 Resume URL: {self.resume_url}")
        print(f"🔑 Session id: {self.session_id}")
        
        self.started = True
        asyncio.create_task(self.send_startup_embed())

    async def _handle_message_event(self, data: Dict[str, Any]):
        """Processes MESSAGE_CREATE events."""
        try:
            channel_id = data["d"].get("channel_id")
            if not channel_id or int(channel_id) not in self.channel_ids:
                return
                
            content = data["d"]["content"]
            author = data["d"]["author"]
            
            if content.startswith(self.prefix) and author["id"] == self.userid:
                if content == f"{self.prefix}groups":
                    await self._send_group_list(channel_id)
            elif "roblox.com/groups" in content:
                await self._process_roblox_group(content)
        except Exception as e:
            print(f"Error processing message: {e}")

    async def _send_group_list(self, channel_id: str):
        """Sends list of tracked groups to a channel."""
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    f"https://discord.com/api/v9/channels/{channel_id}/messages",
                    json={"content": f"> **TK SB** \n\n> Roblox Groups:\n> {', '.join(self.groupsids)}"},
                    headers={"Authorization": self.token}
                )
        except Exception as e:
            print(f"Failed to send group list: {e}")

    async def _process_roblox_group(self, content: str):
        """Extracts and processes Roblox group IDs."""
        try:
            # Extract using regex for reliability
            match = re.search(r"roblox\.com/groups/(\d+)", content)
            if not match:
                return
                
            group_id = match.group(1)
            if group_id not in self.groupsids:
                print(f"🎯 New group detected: {group_id}")
                self.groupsid = group_id
                self.groupsids.append(group_id)
                
                # Call all registered group handlers
                for handler in self.group_handlers:
                    try:
                        asyncio.create_task(handler(group_id))
                    except Exception as e:
                        print(f"Error in group handler: {e}")
        except Exception as e:
            print(f"Error processing Roblox group: {e}")

    async def connect(self):
        """Manages connection lifecycle with backoff and state handling."""
        async with self._connection_lock:
            while self._running:
                try:
                    # Reset decompressor and buffer for new connection
                    self.decomp = zlib.decompressobj()
                    self.buf.clear()
                    
                    self._connection_open = True
                    url = self._get_connection_url()
                    print(f"🔌 Connecting to {url}...")
                    
                    async with websockets.connect(
                        url,
                        max_size=2**24,
                        ping_interval=None,
                        ping_timeout=None,
                        close_timeout=10
                    ) as self.ws:
                        print("✅ WebSocket connected")
                        await self._send_connect_payload()
                        print("📤 Sent connection payload")
                        await self._event_loop()
                    
                except websockets.ConnectionClosed as e:
                    print(f"🔌 Connection closed: {e.code} - {e.reason}")
                    self._connection_open = False
                except asyncio.CancelledError:
                    print("Connection task cancelled")
                    break
                except Exception as e:
                    print(f"🔥 Connection error: {e}")
                    self._connection_open = False
                
                if not self._running:
                    break
                    
                await self._handle_reconnect()

    def _get_connection_url(self) -> str:
        """Determines proper connection URL based on state."""
        if self.restart_state is Restart.RESUME and self.resume_url:
            return self.resume_url
        return "wss://gateway.discord.gg"

    async def _send_connect_payload(self):
        """Sends appropriate connection payload (Identify/Resume)."""
        if self.restart_state is Restart.RESUME and self.session_id:
            payload = {
                "op": 6,
                "d": {
                    "token": self.token,
                    "session_id": self.session_id,
                    "seq": self.seq_num
                }
            }
            print("🔄 Sending RESUME payload...")
        else:
            payload = {
                "op": 2,
                "d": {
                    "token": self.token,
                    "intents": 513 | INTENTS,
                    "properties": {
                        "os": "windows",
                        "browser": "brave",
                        "device": "sex puppet 2000"
                    }
                }
            }
            print("🆔 Sending IDENTIFY payload...")
        
        await self.ws.send(jdumps(payload))

    async def _event_loop(self):
        """Main event processing loop."""
        print("👂 Listening for events...")
        while self._running and self._is_ws_open():
            data = await self._recv_json()
            if not data:
                continue
            await self.on_message(data)
        print("🔇 Event loop ended")

    async def _handle_reconnect(self):
        """Handles reconnection logic with backoff."""
        print("♻️ Preparing to reconnect...")
        
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
            self.heartbeat_task = None
            
        if self.restart_state is Restart.RETRY_LATER:
            print("🔄 Resetting session after invalid session")
            self.session_id = self.resume_url = self.seq_num = None
            self.restart_state = Restart.IDENTIFY
            
        delay = min(self.backoff + random.uniform(0, 1), 30)
        print(f"⏳ Reconnecting in {delay:.1f} seconds...")
        await asyncio.sleep(delay)
        self.backoff = min(self.backoff * 2, 30)
        print(f"📈 New backoff: {self.backoff:.1f}s")

    async def close_connection(self):
        """Closes current connection cleanly."""
        if not self._connection_open:
            return
            
        self._connection_open = False
        if self.ws:
            try:
                await self.ws.close(code=1000)
            except Exception:
                pass
        self.started = False
        print("🔒 Connection closed cleanly")

    async def run(self):
        """Main entry point for the bot."""
        try:
            await self.connect()
        except asyncio.CancelledError:
            await self.stop()

    async def stop(self):
        """Stops the bot gracefully."""
        print("🛑 Stopping bot...")
        self._running = False
        await self.close_connection()
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
        print("👋 Bot stopped successfully")



async def main():
    client = DiscordBot(
        token="NzY5NjYzOTc5MjQ4NDE4ODM4.Gw8onE.GjpoMjH8F5Fwawd6LML5aFRP1pBbdR832E38Zc",
        channel_ids=[1197900179135807608]
    )

    @client.on_group
    async def log(gid: str):
        print("Found group", gid)


    await client.run()

if __name__ == "__main__":
    asyncio.run(main())