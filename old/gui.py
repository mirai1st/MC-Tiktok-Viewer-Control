from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, CommentEvent, GiftEvent
import customtkinter as tk
from customtkinter import *
from test.filehandling import load_config
from time import sleep
import win32com.client as comclt

# Root config

root = CTk()
root.title("Minecraft Viewer Control (Tiktok)")
root.grid_columnconfigure(0, weight=1)
root.resizable(False, False)
log = ""

# Functions 

def logPanelInsert(text):
    logPanel.insert("end", text + "\n")

def randomizer(): # Function of randomizer checkbox
    logPanelInsert("Randomizer: " + isRandomizer.get())
    print("Randomizer: " + isRandomizer.get())

def start_service():
    logPanelInsert("> Starting service... 0%")
    sendMinecraftCommands(f"say Minecraft Tiktok Viewer Control V1.1 - Made by Mirai1st, Thank you for using this program!")

# Connection to tiktok

def showLogPanel():
    if logPanel.winfo_ismapped():
        logPanel.pack_forget()
    else:
        logPanel.pack() 

# Loads data

if (load_config("client_id") != ""):
    username = load_config("client_id")
else:
    username = ""

# clientConnectError = False

isRandomizer = tk.StringVar(value=load_config("isRandomizer"))
isLogPanelEnabled = tk.StringVar(value=load_config("isLogPanelEnabled"))

lbClientId = tk.CTkLabel(root, text="Minecraft Viewer Control", fg_color="transparent", font=("Inter Bold", 20))
lbClientId.grid(row=0, column=0, padx=12, pady=(10, 0), sticky="w")

lbClientId = tk.CTkLabel(root, text="Insert Client ID", font=("Inter", 15), fg_color="transparent")
lbClientId.grid(row=1, column=0, padx=12, sticky="w")

inputClientId = tk.CTkEntry(root, placeholder_text=username)
inputClientId.grid(row=1, column=1, padx=10)

checkboxRandomizer = tk.CTkCheckBox(root, text="Randomizer Mode (Multiplayer)", font=("Inter", 12), command=randomizer, variable=isRandomizer, onvalue="on", offvalue="off", height=20)
checkboxRandomizer.grid(row=2, column=0, padx=10, pady=10, sticky="w")

# if (clientConnectError == True):
#     lbErrorClient = tk.CTkLabel(root, text="Can't connect to client_id. Is client_id invalid?", fg_color="transparent")
#     lbErrorClient.grid(row=1, column=0, padx=10)

btnLogPanel = tk.CTkSwitch(root, text="Enable Log Panel", command=showLogPanel, variable=isLogPanelEnabled, onvalue="on", offvalue="off")
btnLogPanel.grid(row=3, column=0, padx=10, pady=10, sticky="w")

logPanel = tk.CTkTextbox(root)
logPanel.grid(row=4, column=0, padx=10, sticky="ew", columnspan=2)
# logPanel.configure(state="disabled")  # configure textbox to be read-only

btnStartServices = tk.CTkButton(root, text="Start Services", command=start_service)
btnStartServices.grid(row=10, column=0, padx=(10, 0), sticky="ew", columnspan=1)

btnStop = tk.CTkButton(root, text="Stop", state="disable", fg_color="#8b0000")
btnStop.grid(row=10, column=1, padx=(10, 10), pady=10, sticky="ew")

# End
root.mainloop()

# if __name__ == "__main__":
#     # controlPanelGUI()