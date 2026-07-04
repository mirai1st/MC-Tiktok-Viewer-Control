from TikTokLive import TikTokLiveClient
from TikTokLive.client.errors import UserOfflineError, WebcastBlocked200Error
from TikTokLive.events import ConnectEvent, CommentEvent, GiftEvent, DisconnectEvent
import json
import asyncio
import threading
import random

class TikTokConnection:
    def __init__(self, tiktok_username, callback=None, minecraft_callback=None):
        self.tiktok_username = tiktok_username
        self.client = TikTokLiveClient(unique_id=self.tiktok_username)
        # ensure callbacks are callable; otherwise use a no-op to avoid conditional checks
        self.callback = callback if callable(callback) else (lambda *a, **k: None)
        self.minecraft_callback = minecraft_callback if callable(minecraft_callback) else (lambda *a, **k: None)

        # internal runtime objects
        self._thread = None
        self._loop = None
        self._connected_flag = False

        @self.client.on(ConnectEvent)
        async def on_connect(event: ConnectEvent):
            self.minecraft_callback(f"/say Successfully connected to {self.tiktok_username}'s room!")
            msg = f"Connected to @{event.unique_id} (Room ID: {self.client.room_id})"
            self._connected_flag = True
            self.callback(msg)

        @self.client.on(GiftEvent)
        async def on_gift(event: GiftEvent):
            msg = f"{event.user.unique_id} gifted {event.repeat_count}x \"{event.gift.name}\""
            try:
                with open("gift.json", "r") as f:
                    data = json.load(f)
            except Exception:
                data = {}

            sentGift = event.gift.name
            giftid = data.get("GiftID", {})
            players = data.get("PlayerName", {})
            config = data.get("Config", {})

            # choose player based on Config.PlayerRandomizer (default: False)
            player_list = players.get("name", ["@a"])
            if config.get("PlayerRandomizer", False):
                player_name = random.choice(player_list) if player_list else "@a"
            else:
                player_name = "@a"

            # If selected gift found in config
            if sentGift in giftid:
                gift_data = giftid[sentGift]

                cmds = gift_data.get("commands", [])
                
                if isinstance(cmds, str):
                    cmds = [cmds]
                if cmds is None:
                    cmds = []

                # replace placeholder in every command
                processed_cmds_list = [c.replace("{player}", player_name) for c in cmds]

                # If gift event streakable
                if event.gift.streakable and not event.streaking:
                    self.minecraft_callback(f"/say {msg}")
                    self.minecraft_callback(f"/say Player selected: {player_name}")

                    for i in range(event.repeat_count):
                        await asyncio.sleep(gift_data.get("repeat_delay", 0))
                        
                        self.minecraft_callback("execute as @a at @s run playsound entity.experience_orb.pickup neutral @s ~ ~ ~")
                        for pcmd in processed_cmds_list:
                            self.minecraft_callback(pcmd)
                        self.minecraft_callback(
                            f'/title @a actionbar {{"text":"Gift ({event.user.unique_id}) -> {sentGift} {str(i+1)}/{event.repeat_count}","color":"gold","italic":false}}'
                        )

                # If gift event non streakable  
                elif not event.gift.streakable:
                    self.minecraft_callback("execute as @a at @s run playsound entity.experience_orb.pickup neutral @s ~ ~ ~")
                    self.minecraft_callback(f"/say {msg}")
                    self.minecraft_callback(f"/say Player selected: {player_name}")
                    for pcmd in processed_cmds_list:
                        self.minecraft_callback(pcmd)

            # If gift not found in config
            else:
                self.callback(f"[IGNORED] Gift not in config: {sentGift}")

            self.callback(msg)

        @self.client.on(DisconnectEvent)
        async def on_disconnect(event: DisconnectEvent):
            msg = f"Successfully disconnected from @{self.tiktok_username}."
            self._connected_flag = False
            self.callback(msg)

    def _thread_runner(self):
        """
        Runs inside a background thread. Creates a dedicated event loop for the client,
        schedules client.connect(), and runs the loop forever until stop.
        """
        try:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.create_task(self._safe_connect())
            self._loop.run_forever()
        finally:
            tasks = [t for t in asyncio.all_tasks(self._loop) if not t.done()]
            for t in tasks:
                t.cancel()
            self._loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
            self._loop.close()
            self._loop = None
            self._connected_flag = False
            self.callback("Background event loop stopped.")

    async def _safe_connect(self):
        try:
            await self.client.connect()
        except UserOfflineError:
            self.callback("Error: User is currently offline! Comeback when the user is online.")
        except Exception as e:
            self.callback(f"Error: {e}")
    
    def start(self):
        """
        Starts the TikTok client in a background thread with its own event loop.
        """
        if self._thread and self._thread.is_alive():
            # already running
            return {
                "message": f"Already running @{self.tiktok_username}",
                "current_state": True
            }

        # start background thread
        self._thread = threading.Thread(target=self._thread_runner, daemon=True)
        self._thread.start()

        # give a small moment for thread/loop to initialize (non-blocking)
        # real connection status will be reported through ConnectEvent callback
        return {
            "message": f"Connecting to TikTok user: @{self.tiktok_username}",
            "current_state": True
        }

    def stop(self, timeout=10):
        """
        Safely stops the TikTok client.
        Returns a concurrent.futures.Future (from run_coroutine_threadsafe) so callers can wait if needed.
        """
        if not self._loop:
            # loop not created or already stopped
            self.callback("Event Interrupted: Client is not running.")
            return None

        # schedule disconnect() on the client's loop
        try:
            future = asyncio.run_coroutine_threadsafe(self.client.disconnect(), self._loop)
        except Exception as e:
            self.callback(f"Failed to schedule disconnect: {e}")
            return None

        # when disconnect completes, stop the loop
        def _on_done(_fut):
            try:
                # stop the event loop thread-safe
                if self._loop:
                    self._loop.call_soon_threadsafe(self._loop.stop)
            except Exception:
                pass

        future.add_done_callback(_on_done)
        return future

    @property
    def connected(self):
        return self._connected_flag
