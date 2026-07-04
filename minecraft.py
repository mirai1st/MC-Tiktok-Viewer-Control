from mctools import RCONClient
import time

class connection:  
    ''' Class Connection: Connect to Minecraft server via RCON '''
    def __init__(self):
        self.rcon = None
        self.connected = False
    
    def start_server(self, ip, port, password, username):
        """
        IP: Any - IP address of the Minecraft server,
        Port: int - RCON port of the Minecraft server,
        Password: str - RCON password of the Minecraft server

        Please setting in the server.properties file:
        enable-rcon=true,
        rcon.password=your_password,
        rcon.port=your_port,
        """

        try:
            self.rcon = RCONClient(ip, port)
            self.rcon.login(password)
            self.connected = True
            self.username = username
            self.sendMinecraftCommand(f"say Minecraft Tiktok Viewer Control V2 - Made by Mirai1st, Thank you for using this program!")
            time.sleep(2)

            return {
                "message": "Successfully connected to " + ip + ":" + str(port) + ". \nYou can now use Minecraft commands.",
                "current_state": True
            }
        
        except ConnectionRefusedError as e:
            return {
                "message": "Error: Couldn't connect to Minecraft server " + ip + ":" + str(port) + ". Connection refused. \n-> ConnectionRefusedError: " + str(e),
                "current_state": False
            }
        except TimeoutError as e:
            return {
                "message": "Error: Couldn't connect to Minecraft server " + ip + ":" + str(port) + ". Connection timed out. \n-> TimeoutError: " + str(e),
                "current_state": False
            }
        except Exception as e:
            return {
                "message": "Error: An error occurred. \n-> ErrorException: " + str(e),
                "current_state": False
            }
        
            
    def stop_server(self):
        if self.rcon:
            self.rcon.stop()
            self.connected = False
            return {
                "message": "Disconnected from Minecraft server.",
                "current_state": False
            }
        else:
            return {
                "message": "No active connection to disconnect.",
                "current_state": False
            }
    
    def sendMinecraftCommand(self, command):
        if not self.connected:
            return "Not connected."

        try:
            response = self.rcon.command(command) # Minecraft command
            print(response)
        except:
            print("WARNING: Couldn't send command to Minecraft server.")