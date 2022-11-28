# Imports
import pymem, pymem.process, keyboard, ctypes, os, time
from struct import pack
from time import sleep
from colorama import Fore, Back, Style
from win32gui import GetWindowText, GetForegroundWindow

# Logo
logo = """
██████╗░██╗░░░░░██╗░░░██╗████████╗░█████╗░  ░█████╗░░██████╗░██████╗░░█████╗░
██╔══██╗██║░░░░░██║░░░██║╚══██╔══╝██╔══██╗  ██╔══██╗██╔════╝██╔════╝░██╔══██╗
██████╔╝██║░░░░░██║░░░██║░░░██║░░░██║░░██║  ██║░░╚═╝╚█████╗░██║░░██╗░██║░░██║
██╔═══╝░██║░░░░░██║░░░██║░░░██║░░░██║░░██║  ██║░░██╗░╚═══██╗██║░░╚██╗██║░░██║
██║░░░░░███████╗╚██████╔╝░░░██║░░░╚█████╔╝  ╚█████╔╝██████╔╝╚██████╔╝╚█████╔╝
╚═╝░░░░░╚══════╝░╚═════╝░░░░╚═╝░░░░╚════╝░  ░╚════╝░╚═════╝░░╚═════╝░░╚════╝░"""

# Clear function
clear = lambda: os.system("cls" if os.name in ("nt", "dos") else "clear") # Don't touch this

# Switches
glowSwitch = False
brightnessChamsSwitch = False
triggerbotSwitch = False
bhopSwitch = False

# Offsets
m_iTeamNum = (0xF4)
m_iGlowIndex = (0x10488)
m_fFlags = (0x104)
m_iCrosshairId = (0x11838)
dwLocalPlayer = (0xDE7964)
dwEntityList = (0x4DFCE74)
dwForceAttack = (0x322AC7C)
dwForceJump = (0x52B8BFC)
dwGlowObjectManager = (0x5357948)
model_ambient_min = (0x5A118C)
m_flFlashMaxAlpha = (0x1046C)
m_vecOrigin = (0x138)

# Pymem
pm = pymem.Pymem("csgo.exe")
client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
engine = pymem.process.module_from_name(pm.process_handle, "engine.dll").lpBaseOfDll

# Glow function
def glow():
    localPlayer = pm.read_int(client + dwLocalPlayer)
    localTeam = pm.read_int(localPlayer + m_iTeamNum)
    glowManager = pm.read_int(client + dwGlowObjectManager)
    for i in range(0, 32):
        player = pm.read_int(client + dwEntityList + i * 0x10)
        if player and not (player < 0):
            playerTeam = pm.read_int(player + m_iTeamNum)
            glowIndex = pm.read_int(player + m_iGlowIndex)
            if (playerTeam != localTeam):
                pm.write_float(glowManager + (glowIndex * 0x38) + 0x8, float(0.9)) # Red
                pm.write_float(glowManager + (glowIndex * 0x38) + 0xC, float(0)) # Green
                pm.write_float(glowManager + (glowIndex * 0x38) + 0x10, float(0)) # Blue
                pm.write_float(glowManager + (glowIndex * 0x38) + 0x14, float(0.9)) # Alpha
                pm.write_int(glowManager + (glowIndex * 0x38) + 0x28, 1) # Enable enemy glow
            elif (playerTeam == localTeam):
                pm.write_float(glowManager + (glowIndex * 0x38) + 0x8, float(0)) # Red
                pm.write_float(glowManager + (glowIndex * 0x38) + 0xC, float(0.9)) # Green
                pm.write_float(glowManager + (glowIndex * 0x38) + 0x10, float(0.9)) # Blue
                pm.write_float(glowManager + (glowIndex * 0x38) + 0x14, float(0.9)) # Alpha
                pm.write_int(glowManager + (glowIndex * 0x38) + 0x28, 1) # Enable team glow

# Brightness chams function
def brightness_chams():
    brightness = float(7)
    pointer = pm.read_int(engine + model_ambient_min - 0x2c)
    val = int("".join(bin(c).replace("0b", "").rjust(8, "0") for c in pack("!f", brightness)), 2) ^ pointer
    pm.write_int(engine + model_ambient_min, val)

# Triggerbot function
def triggerbot():
    if not keyboard.is_pressed("shift"):
        time.sleep(0.1)

    if keyboard.is_pressed("shift"):
        player = pm.read_int(client + dwLocalPlayer)
        entity_id = pm.read_int(player + m_iCrosshairId)
        entity = pm.read_int(client + dwEntityList + (entity_id - 1) * 0x10)

        entity_team = pm.read_int(entity + m_iTeamNum)
        player_team = pm.read_int(player + m_iTeamNum)

        if entity_id > 0 and entity_id <= 64 and player_team != entity_team:
            pm.write_int(client + dwForceAttack, 6)

        time.sleep(0.006)

# Bunnyhop function
def bhop():
    if keyboard.is_pressed("space"):
        force_jump = client + dwForceJump
        player = pm.read_int(client + dwLocalPlayer)
        if player:
            on_ground = pm.read_int(player + m_fFlags)
            if on_ground and on_ground == 257:
                pm.write_int(force_jump, 5)
                time.sleep(0.08)
                pm.write_int(force_jump, 4)

    time.sleep(0.002)

# Switches function
def switches():
    global glowSwitch, brightnessChamsSwitch, triggerbotSwitch, bhopSwitch
    while True:
        if glowSwitch == True:
            glow()
        if brightnessChamsSwitch == True:
            brightness_chams()
        if triggerbotSwitch == True:
            triggerbot()
        if bhopSwitch == True:
            bhop()

        # Glow switch
        if keyboard.is_pressed("f1"):
            if glowSwitch == True:
                glowSwitch = False
                print(f"{Fore.GREEN}[{Fore.RESET}+{Fore.GREEN}]{Fore.RESET} Glow disabled.")
                time.sleep(0.5)
            elif glowSwitch == False:
                glowSwitch = True
                print(f"{Fore.GREEN}[{Fore.RESET}+{Fore.GREEN}]{Fore.RESET} Glow enabled.")
                time.sleep(0.5)
        
        # Brightness chams switch
        if keyboard.is_pressed("f2"):
            if brightnessChamsSwitch == True:
                brightnessChamsSwitch = False
                print(f"{Fore.GREEN}[{Fore.RESET}+{Fore.GREEN}]{Fore.RESET} Brightness chams disabled.")
                time.sleep(0.5)
            elif brightnessChamsSwitch == False:
                brightnessChamsSwitch = True
                print(f"{Fore.GREEN}[{Fore.RESET}+{Fore.GREEN}]{Fore.RESET} Brightness chams enabled.")
                time.sleep(0.5)

        # Triggerbot switch
        if keyboard.is_pressed("f3"):
            if triggerbotSwitch == True:
                triggerbotSwitch = False
                print(f"{Fore.GREEN}[{Fore.RESET}+{Fore.GREEN}]{Fore.RESET} Triggerbot disabled.")
                time.sleep(0.5)
            elif triggerbotSwitch == False:
                triggerbotSwitch = True
                print(f"{Fore.GREEN}[{Fore.RESET}+{Fore.GREEN}]{Fore.RESET} Triggerbot enabled.")
                time.sleep(1)
        
        # Bhop switch
        if keyboard.is_pressed("f4"):
            if bhopSwitch == True:
                bhopSwitch = False
                print(f"{Fore.GREEN}[{Fore.RESET}+{Fore.GREEN}]{Fore.RESET} Bunnyhop disabled.")
                time.sleep(0.5)
            elif bhopSwitch == False:
                bhopSwitch = True
                print(f"{Fore.GREEN}[{Fore.RESET}+{Fore.GREEN}]{Fore.RESET} Bunnyhop enabled.")
                time.sleep(0.5)
        
        # Exit switch
        if keyboard.is_pressed("f7"):
            print(f"{Fore.GREEN}[{Fore.RESET}+{Fore.GREEN}]{Fore.RESET} Exiting...")
            time.sleep(1)
            exit()

# Main cheat function
def main():
    clear()
    os.system("title Pluto External - 1.0 - discord.gg/kws")
    print(Fore.RED + logo + Style.RESET_ALL)
    print("-----------------------------------------------------------------------------")
    print(f"{Fore.GREEN}[{Fore.RESET}+{Fore.GREEN}]{Fore.RESET} Found CS:GO process: {Fore.CYAN}{pm.process_id}{Fore.RESET}")
    print(f"{Fore.GREEN}[{Fore.RESET}+{Fore.GREEN}]{Fore.RESET} Found client.dll: {Fore.CYAN}{hex(client)}{Fore.RESET}")
    print(f"{Fore.GREEN}[{Fore.RESET}+{Fore.GREEN}]{Fore.RESET} Found engine.dll: {Fore.CYAN}{hex(engine)}{Fore.RESET}")
    print("-----------------------------------------------------------------------------")
    print(f"{Fore.MAGENTA}[{Fore.RESET}!{Fore.MAGENTA}]{Fore.RESET} Press {Fore.MAGENTA}F1{Fore.RESET} to toggle glow.")
    print(f"{Fore.MAGENTA}[{Fore.RESET}!{Fore.MAGENTA}]{Fore.RESET} Press {Fore.MAGENTA}F2{Fore.RESET} to toggle brightness chams. {Fore.RED}(CAN'T TURN OFF){Fore.RESET}")
    print(f"{Fore.MAGENTA}[{Fore.RESET}!{Fore.MAGENTA}]{Fore.RESET} Press {Fore.MAGENTA}F3{Fore.RESET} to toggle triggerbot.")
    print(f"{Fore.MAGENTA}[{Fore.RESET}!{Fore.MAGENTA}]{Fore.RESET} Press {Fore.MAGENTA}F4{Fore.RESET} to toggle bunnyhop.")
    print(f"{Fore.MAGENTA}[{Fore.RESET}!{Fore.MAGENTA}]{Fore.RESET} Press {Fore.MAGENTA}F7{Fore.RESET} to exit.")
    print("-----------------------------------------------------------------------------")
    print(f"{Fore.GREEN}[{Fore.RESET}+{Fore.GREEN}]{Fore.RESET} Cheat loaded.")
    switches()

# Main
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{Fore.RED}[{Fore.RESET}!{Fore.RED}]{Fore.RESET} Error: {str(e)}")
        time.sleep(5)
        exit()
    except KeyboardInterrupt:
        print(f"{Fore.GREEN}[{Fore.RESET}+{Fore.GREEN}]{Fore.RESET} Exiting...")
        time.sleep(1)
        exit()