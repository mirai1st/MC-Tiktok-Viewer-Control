from TikTokLive import TikTokLiveClient
from TikTokLive.client.errors import UserOfflineError
from TikTokLive.events import ConnectEvent, CommentEvent, GiftEvent
from minecraft import sendMinecraftCommands
import win32com.client as comclt
# import random # <-- for randomizer playerTarget (Multiplayer)
import asyncio
import sys


if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

wsh = comclt.Dispatch("WScript.Shell")
playerTarget = "MiraiMorikawa"
tiktokID = "ownytv"
randomizer = ["MiraiMorikawa", "Qianng"]

# def randomizer():
#     playerTarget = random.choice(randomizer)

sendMinecraftCommands(f"say Minecraft Tiktok Viewer Control V1.1 - Made by Mirai1st, Thank you for using this program!")

client: TikTokLiveClient = TikTokLiveClient(unique_id=tiktokID)

@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    sendMinecraftCommands(f"say Connected to {event.unique_id}'s Room!")
    print(f"Connected to @{event.unique_id} (Room ID: {client.room_id}")

@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    # Streakable gift & streak is over

    if event.gift.streakable and not event.streaking:
        print(f"{event.user.unique_id} gifted {event.repeat_count}x \"{event.gift.name}\"")

        sendMinecraftCommands("execute at @a run playsound minecraft:entity.experience_orb.pickup voice @a")
        sendMinecraftCommands("say " + event.user.unique_id + " gifted " + str(event.repeat_count) + "x " + event.gift.name)

        if (event.gift.name == "Finger Heart"):
            for i in range(event.repeat_count):
                await asyncio.sleep(0.5)
                sendMinecraftCommands(f"effect give {playerTarget} minecraft:poison 10")
        elif (event.gift.name == "Doughnut"):
            for i in range(event.repeat_count):
                await asyncio.sleep(0.5)
                sendMinecraftCommands(f"execute at {playerTarget} run summon minecraft:lightning_bolt")
        elif (event.gift.name == "Better Luck"):
            for i in range(event.repeat_count):
                await asyncio.sleep(0.5)
                sendMinecraftCommands(f"execute at {playerTarget} run summon minecraft:zombie")
        elif (event.gift.name == "Rosa"):
            for i in range(event.repeat_count):
                await asyncio.sleep(0.5)
                sendMinecraftCommands(f"say Dropped 1x hold item from {playerTarget}'s inventory.")
                wsh.SendKeys("q")
        elif (event.gift.name == "New Year Keyboard"):
            for i in range(event.repeat_count):
                await asyncio.sleep(0.5)
                sendMinecraftCommands(f"execute at {playerTarget} run summon minecraft:creeper")
        elif (event.gift.name == "Rose"):
            for i in range(event.repeat_count):
                await asyncio.sleep(0.5)
                sendMinecraftCommands(f"effect give {playerTarget} minecraft:regeneration 10 2")

        # Non-streakable gift
    elif not event.gift.streakable:
        print(f"{event.user.unique_id} gifted \"{event.gift.name}\"")

        sendMinecraftCommands(f"execute at {playerTarget} run playsound minecraft:entity.experience_orb.pickup voice @a")
        sendMinecraftCommands("say " + event.user.unique_id + " gifted " + str(event.repeat_count) + "x " + event.gift.name)

        if (event.gift.name == "Finger Heart"):
            sendMinecraftCommands(f"effect give {playerTarget} minecraft:poison 10")
        elif (event.gift.name == "Doughnut"):
            sendMinecraftCommands(f"execute at {playerTarget} run summon lightning_bolt")
        elif (event.gift.name == "Better Luck"):
            sendMinecraftCommands(f"execute at {playerTarget} run summon minecraft:zombie")
        elif (event.gift.name == "Rosa"):
            sendMinecraftCommands(f"say Dropped 1x Hold Item from {playerTarget}'s inventory.")
            wsh.SendKeys("q")
        elif (event.gift.name == "New Year Keyboard"):
            sendMinecraftCommands(f"execute at {playerTarget} run summon minecraft:creeper")
        elif (event.gift.name == "Rose"):
            sendMinecraftCommands(f"effect give {playerTarget} minecraft:regeneration 10")

        # Comment Event
async def on_comment(event: CommentEvent) -> None:
    print(f"{event.user.nickname}: {event.comment}")
    # sendMinecraftCommands(f"msg MiraiMorikawa {event.user.nickname}: {event.commvent}") # Minecraft commands

client.add_listener(CommentEvent, on_comment)

# Gift Listener

if __name__ == '__main__':
    try:
        client.run()
    except UserOfflineError:
        print(f"ERROR: Coudn't start service, tiktok {tiktokID} is offline.")
        sendMinecraftCommands("ERROR: Coudn't start service, tiktok {tiktokID} is offline.")
