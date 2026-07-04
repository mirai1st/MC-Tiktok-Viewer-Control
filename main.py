import customtkinter as ctk
import minecraft
from datetime import datetime
import json_loader
import json
import threading
import tiktokconnection as tiktokconn

def main():
    server = minecraft.connection()
    tiktok_client = None  # global handle to the TikTokConnection instance
    
    # Gift Window
    def giftwindow():
        log_message("Opening Gift Window...")
        giftwindow = ctk.CTkToplevel()
        giftwindow.after(201, lambda :giftwindow.iconbitmap('assets/MinecraftVCIcon.ico'))
        giftwindow.title("Gift Configurations")
        giftwindow.grid_rowconfigure(3, weight=1)   # row 2 grows (textbox)
        giftwindow.grid_columnconfigure(0, weight=1) # column 0 grows
        giftwindow.lift()
        giftwindow.focus_force()
        
        label = ctk.CTkLabel(giftwindow, text="Gift are constructed using JSON format. \nPlease refer to the documentation for more details.", font=("Inter", 14), justify="left")
        label.grid(row=0, column=0, padx=10, pady=(10,0), sticky="w")

        gift_textbox = ctk.CTkTextbox(giftwindow, width=330, height=400, font=("Inter", 15))
        gift_textbox.grid(row=1, column=0, padx=10, pady=(10,10), sticky="nsew")

        data = json_loader.load_json()
        gift_textbox.delete("1.0", ctk.END)
        gift_textbox.insert(ctk.END, json.dumps(data, indent=4))
    
        def save_gift_config():
            content = gift_textbox.get("1.0", ctk.END)
            try:
                parsed_json = json.loads(content)
                with open('gift.json', 'w') as f:
                    json.dump(parsed_json, f, indent=4)
                giftwindow.destroy()
                log_message("Gift configuration saved successfully.")
            except json.JSONDecodeError:
                log_message("Error: Invalid JSON format. Please correct it before saving.")

        close_btn = ctk.CTkButton(giftwindow, text="Save & Close", command=save_gift_config)
        close_btn.grid(row=2, column=0, padx=10, pady=(10,10), sticky="sw")

        giftwindow.mainloop()

    def mcmd(cmd):
        server.sendMinecraftCommand(cmd)

    # Log message to textbox (thread-safe)
    def log_message(message):
        def _insert():
            dt = datetime.now()
            log_box.insert(
                ctk.END,
                f"[{dt.date()} / {dt.hour}:{dt.minute}] {message}\n"
            )
            log_box.see(ctk.END)
        # schedule on main thread
        log_box.after(0, _insert)

    # Start server connection with threading
    def on_start():
        nonlocal tiktok_client
        def start_tiktok():
            nonlocal tiktok_client
            username = username_box.get().strip()
            if not username:
                log_message("Please enter a TikTok username.")
                # restore button
                start_btn.configure(text="Start Server", command=on_start, fg_color="#008EB5", hover_color="#0058D4")
                return

            tiktok_client = tiktokconn.TikTokConnection(username, callback=log_message, minecraft_callback=mcmd)
            result = tiktok_client.start()
            log_message(result["message"])

        def start_thread():
            start_btn.configure(text="Wait", fg_color="#006B8B", command=lambda: None)
            try:
                result = server.start_server(ip=ip_box.get(), port=serverport_box.get(), password=password_box.get(), username=username_box.get())
                log_message(result["message"])
            except Exception as e:
                log_message(f"Failed to start MC server: {e}")
                start_btn.configure(text="Start Server", command=on_start, fg_color="#008EB5", hover_color="#0058D4")
                return

            # set correct button depending on state
            if result["current_state"] == True:
                log_message("Making a bridge to the client...")
                start_tiktok()
                start_btn.configure(text="Stop Server", command=stop_server, fg_color="#A30000", hover_color="#8B0000")
                return None
            else: 
                start_btn.configure(text="Start Server", command=on_start, fg_color="#008EB5", hover_color="#0058D4")

        log_message("Creating a connection to the server...")
        threading.Thread(target=start_thread, daemon=True).start()

    # Stop server connection (safe, non-blocking)
    def stop_server():
        nonlocal tiktok_client
        log_message("Stopping TikTok client...")
        # stop TikTok client safely
        if tiktok_client is None:
            log_message("TikTok client not running.")
            return

        future = tiktok_client.stop()
        if future is None:
            log_message("No running TikTok loop to stop.")
            # still stop MC server
            mc_result = server.stop_server()
            log_message(mc_result["message"])
            start_btn.configure(text="Start Server", command=on_start, fg_color="#008EB5", hover_color="#0058D4")
            tiktok_client = None
            return

        # wait for the future in a background thread (do not block GUI)
        def wait_for_stop(fut):
            try:
                fut.result(timeout=15)  # wait for disconnect to complete
                log_message("TikTok client disconnected.")
            except Exception as e:
                log_message(f"Error while stopping TikTok client: {e}")
            finally:
                # Stop MC server and update UI on main thread
                def _finalize():
                    mc_result = server.stop_server()
                    log_message(mc_result["message"])
                    start_btn.configure(text="Start Server", command=on_start, fg_color="#008EB5", hover_color="#0058D4")
                log_box.after(0, _finalize)

        threading.Thread(target=wait_for_stop, args=(future,), daemon=True).start()

    # This function saves the current configuration (username, ip, etc) to a JSON file
    def save_config():
        config_data = {
            "username": username_box.get(),
            "server_ip": ip_box.get(),
            "server_port": serverport_box.get(),
            "server_pass": password_box.get()
        }
        try: 
            with open('config.json', 'w') as config_file:
                json.dump(config_data, config_file, indent=4)
            log_message("Config successfully saved!")
        except json.JSONDecodeError:
            log_message("Error: Invalid JSON format. Please correct it before saving.")
    
    # loads cool stuff
    def load_existing_config():
        try:
            with open('config.json', 'r') as config_file:
                config_data = json.load(config_file)
                username_box.delete(0, ctk.END)
                username_box.insert(0, config_data.get("username", ""))
                ip_box.delete(0, ctk.END)
                ip_box.insert(0, config_data.get("server_ip", ""))
                serverport_box.delete(0, ctk.END)
                serverport_box.insert(0, config_data.get("server_port", ""))
                password_box.delete(0, ctk.END)
                password_box.insert(0, config_data.get("server_pass", ""))
            log_message("Config successfully loaded!")
        except FileNotFoundError:
            log_message("No existing config found. Please enter your settings.")
        except json.JSONDecodeError:
            log_message("Error: Invalid JSON format in config file.")

    ctk.set_appearance_mode("dark")
    app = ctk.CTk()
    app.after(201, lambda :app.iconbitmap('assets/MinecraftVCIcon.ico'))
    app.title("Minecraft Viewer Control V2 (Beta)")
    app.grid_rowconfigure(3, weight=1)   # row 2 grows (textbox)
    app.grid_columnconfigure(0, weight=1) # column 0 grows
    app.resizable(False, False)

    lbClientId = ctk.CTkLabel(app, text="Minecraft Viewer Control", fg_color="transparent", font=("Inter Bold", 20))
    lbClientId.grid(row=0, column=0, padx=12, pady=(10, 0), sticky="w")

    # Username label and input box
    lbClientId = ctk.CTkLabel(app, text="Insert Tiktok Username", font=("Inter", 15), fg_color="transparent")
    lbClientId.grid(row=1, column=0, padx=12, sticky="w")
    username_box = ctk.CTkEntry(app, placeholder_text="your_client_id")
    username_box.grid(row=1, column=0, pady=2, padx=(300,10), sticky="ew", columnspan=2)

    # IP Address label and input box
    lbServerIP = ctk.CTkLabel(app, text="Insert MC Server IP", font=("Inter", 12), fg_color="transparent")
    lbServerIP.grid(row=2, column=0, padx=12, sticky="w")
    ip_box = ctk.CTkEntry(app, placeholder_text="e.g. localhost")
    ip_box.grid(row=2, column=0, pady=2, padx=(300,10), sticky="ew", columnspan=2)

    # IP Address label and input box
    lbServerPort = ctk.CTkLabel(app, text="Server RCON Port", font=("Inter", 12), fg_color="transparent")
    lbServerPort.grid(row=3, column=0, padx=12, sticky="w")
    serverport_box = ctk.CTkEntry(app, placeholder_text="e.g. 27756")
    serverport_box.grid(row=3, column=0, pady=2, padx=(300,10), sticky="ew", columnspan=2)
    
    lbPassword = ctk.CTkLabel(app, text="Server RCON Password", font=("Inter", 12), fg_color="transparent")
    lbPassword.grid(row=4, column=0, padx=12, sticky="w")
    password_box = ctk.CTkEntry(app, placeholder_text="e.g. 12345678", show="*")
    password_box.grid(row=4, column=0, pady=2, padx=(300,10), sticky="ew", columnspan=2)

    gift_btn = ctk.CTkButton(app, text="Gift Configurations", command=giftwindow, fg_color="green", hover_color="#005F00")
    gift_btn.grid(row=5, column=0, pady=10, padx=(10,10), sticky="w")

    log_box = ctk.CTkTextbox(app, width=350, height=200)
    log_box.grid(row=6, column=0, columnspan=2, padx=10, pady=(0,10), sticky="nsew")

    start_btn = ctk.CTkButton(app, text="Start Server", command=on_start, fg_color="#008EB5", hover_color="#0058D4")
    save_btn = ctk.CTkButton(app, text="Save Config", command=save_config, fg_color="green", hover_color="#005F00")

    start_btn.grid(row=7, column=0, pady=10, padx=10, sticky="w")
    save_btn.grid(row=7, column=0, pady=10, padx=(160,10), sticky="w")

    load_existing_config()
    
    app.mainloop()

main()
