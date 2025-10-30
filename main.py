import json
import os
import time
import re
from colorama import init, Fore

#   Config
CURRENT_FILE_PATH = os.path.dirname(os.path.abspath(__file__))
TF2_PATH = "C:\Program Files (x86)\Steam\steamapps\common\Team Fortress 2\\tf"
CONSOLE_OUTPUT_PATH = f"{TF2_PATH}\console.txt"
TEMP_JSON_PATH = f"{CURRENT_FILE_PATH}\\temp.json"
WEAPONS_JSON_PATH = f"{CURRENT_FILE_PATH}\weapons.json"
EXPORT_FOLDER_PATH = f"{CURRENT_FILE_PATH}\export"
START_TIME = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
START_TIME_SECONDS = time.perf_counter()


WEAPON_CACHE = {}
players = [] # list[player]
cycles = 0
hostname = ""
map_name = "" 
init(autoreset=True)

#   Class to store each player with there name, current class, crit amount, kills, and deaths
class Player:
    def __init__(self, name: str, current_class: str, crit_amount: int = 0, kills: int = 0, deaths: int = 0):
        self.name = name
        self.current_class = current_class
        self.crit_amount = crit_amount
        self.kills = kills
        self.deaths = deaths


        self.steam_id = ""
        self.play_time = ""
        self.active = True

    def update_class(self, new_class: str):
        """
        Updates the player's class if it has changed.
        """
        if self.current_class != new_class:
            print(f"{Fore.BLUE}{self.name} has changed to a {new_class}")
            self.current_class = new_class
    
    def add_crit(self):
        """
        Increments the player's crit hit count by one and logs the update.
        """
        self.crit_amount += 1
        print(f"{Fore.LIGHTRED_EX}{self.name} got a crit ({self.crit_amount} total)")

    def add_kill(self):
        """
        Increments the player's kill count count by one.
        """
        self.kills += 1

    def add_death(self):
        """
        Increments the player's death count count by one.
        """
        self.deaths += 1


def export_json():
    """
    Takes all current data and from the temp file, and dumps it to an export.json file.
    """
    end_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    end_time_seconds = time.perf_counter()
    elapsed_time = end_time_seconds - START_TIME_SECONDS

    temp_data = {}
    try:
        with open(TEMP_JSON_PATH, 'r', encoding="utf-8") as temp_file:
            temp_data = json.load(temp_file)
    except FileNotFoundError:
        print(f"{Fore.RED}-File not found 'temp.json'.")
    except json.JSONDecodeError:
        print(f"{Fore.RED}-File 'temp.json' is invalid JSON.")

    merged_players = temp_data.get("Players", {})

    for player in players:
        merged_players[player.name] = {
            "Kills": player.kills,
            "Deaths": player.deaths,    
            "KD Ratio": round(player.kills / player.deaths, 2) if player.deaths > 0 else player.kills,
            "Crits Kills": player.crit_amount,
            "Crit Kill Percent": round(player.crit_amount / player.kills * 100, 2) if player.kills > 0 else 0,
            "Active": player.active,
            "Disconnect Cycle": None,
            "Steam ID": player.steam_id
        }

    export_data = {
        "Start Time": START_TIME,
        "End Time": end_time,
        "Elapsed Time": round(elapsed_time),
        "Cycles": cycles,
        "Hostname": hostname,
        "Map": map_name,
        "Players": merged_players
    }


    export_json_path = f"{EXPORT_FOLDER_PATH}\{end_time}.json"
    try:
        with open(export_json_path, 'w', encoding="utf-8") as f:
            json.dump(export_data, f, indent=4, ensure_ascii=False)

        print(f"{Fore.YELLOW}-Exported data to '{export_json_path}'.")
    except FileNotFoundError:
        print(f"{Fore.YELLOW}-Failed to export data to '{EXPORT_FOLDER_PATH}'.")

def build_cache():
    """
    Takes data from the weapons.json file and builds a cache for them for faster speed.
    """
    global WEAPON_CACHE

    with open(WEAPONS_JSON_PATH, 'r') as file:
        weaponClasses = json.load(file)
    
    WEAPON_CACHE = {
        weapon: cls
        for cls, weapons in weaponClasses.items()
        for weapon in weapons
    }
        
#   Handle logic when the status cycle is run
def handle_cycle(line_number: int):
    """
    Handles the logic when the status command is ran in the console.
    """
    global cycles, map_name, hostname, players

    cycles += 1
    status_players = []
    print(f"{Fore.YELLOW}-New Cycle ({cycles} total).")

    with open(CONSOLE_OUTPUT_PATH, "r", encoding="utf-8", errors="ignore") as f:
#       Skip to the right line number
        for _ in range(line_number):
            next(f, None)

        for line in f:
            line_number += 1
            line_text = line.strip()

#           Stop reading when __Done__ is printed
            if line_text == "__DONE__":
                break

#           Hostname line
            if line_text.lower().startswith("hostname"):
                hostname = line.split(":", 1)[1].strip()

#           Map line
            elif line_text.lower().startswith("map"):
                parts = line.split(":", 1)
                if len(parts) > 1:
                    map_name = parts[1].split()[0]

            elif line_text.startswith("#"):
                match = re.search(r'"(.*?)"', line_text)
                if match:
                    username = match.group(1).strip()
                    status_players.append(username)

#               Extract Steam3 ID and convert to Steam64
                steam3_match = re.search(r'\[U:1:(\d+)\]', line_text)
                if steam3_match:
                    account_id = int(steam3_match.group(1))
                    steam64 = account_id + 76561197960265728
                    for player in players:
                        if player.name.strip().lower() == username.lower():
                            player.steam_id = str(steam64)
                            break

    status_players = [p.lower().strip() for p in status_players]

#   Handle disconnects
    for player in players[:]:
        if player.name.lower().strip() not in status_players:
            player.active = False
            players.remove(player)
            print(f"{Fore.YELLOW}-'{player.name}' has left at cycle: {cycles}.")
            add_temp_players(player)


def clear_temp():
    """
    Clears and resets temp.json for a new session.
    Resets to the defult of { "Players": {} }
    """
    with open(TEMP_JSON_PATH, 'w', encoding="utf-8") as f:
        data = {"Players": {}}
        json.dump(data, f, indent=4)
    print(f"{Fore.YELLOW}-Temp JSON file has been cleared & reset.")



def add_temp_players(player: Player):
    """
    Adds a player to the temp JSON file under "Players".
    """
    if not os.path.exists(TEMP_JSON_PATH):
        data = {"Players": {}}
    else:
        with open(TEMP_JSON_PATH, 'r', encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {"Players": {}}

#   Really make sure "Players" is in the file
    if "Players" not in data:
        data = {"Players": {}}
    data["Players"][player.name] = {
        "Kills": player.kills,
        "Deaths": player.deaths,    
        "KD Ratio": round(player.kills / player.deaths, 2) if player.deaths > 0 else player.kills,
        "Crits Kills": player.crit_amount,
        "Crit Kill Percent": round(player.crit_amount / player.kills * 100, 2) if player.kills > 0 else 0,
        "Active": player.active,
        "Discount Cycle": cycles,
        "Steam ID": player.steam_id
    }
    
    with open(TEMP_JSON_PATH, 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    player = None

#   Gets the player and class and crit flag
def checkPlayerWeapon(msg: str) -> tuple[str | None, str | None, bool | None]:
    """
    Parses a console line to extract player name, weapon class, and crit flag.
    Returns a tuple: (player_name, player_class, is_crit, victim_name)
    """

    match = re.match(r"(.+?) killed (.+?) with ([^\.]+)\.?(?: \((crit)\))?", msg)
    if not match:
        return (None, None, None, None)


    player_name = match.group(1).strip()
    victim_name = match.group(2).strip()
    weapon_name = match.group(3).strip()
    crit_flag = match.group(4) == "crit"
    player_class = None

    player_class = WEAPON_CACHE.get(weapon_name)

    return (player_name, player_class, crit_flag, victim_name)


#   Find or create player instance
def get_player(name: str, current_class: str = '') -> Player:
    """
    Finds an existing Player instance or creates a new one if not found.
    Returns an instance of the Player class
    """

    for p in players:
        if p.name == name:
            return p

    new_player = Player(name, current_class)
    players.append(new_player)

    if current_class:
        print(f"{Fore.BLUE}{name} is now a {current_class}")
        
    return new_player


#   Update class and crit count 
def update_class(update_info: tuple[str, str, bool, str]):
    """
    Updates a player's class and critical hit count based on parsed console data.
    """
    killer_name, new_class, crit, victim_name = update_info
    if not killer_name:
        return

#   Process killer
    killer = get_player(killer_name, new_class or "")
    killer.update_class(new_class or "")
    killer.add_kill()
    if crit:
        killer.add_crit()

#   Always print kill message
    if victim_name:
        #print(f"{killer_name} killed {victim_name}")
#       Process victim
        victim = get_player(victim_name, "")
        victim.add_death()

def follow_file(path: str):
    """
    Generator that continuously reads new lines from a file as it updates.
    yields a tuple (line, line_number)
    """

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        line_number = sum(1 for _ in f)

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
#               Wait for new data
                time.sleep(0.5)
                continue
            line_number += 1
            yield line.strip(), line_number 



#   Main loop of the program
if __name__ == "__main__":
    
    start_cache_time = time.perf_counter()
    build_cache()
    end_cache_time = time.perf_counter()
    cache_elapsed_time = end_cache_time - start_cache_time
    print(f"{Fore.YELLOW}-Built cache in {cache_elapsed_time:6f} seconds.")

#   Clear & reset the temp file from the last session
    clear_temp() 
    print(f"{Fore.YELLOW}-TF2 Stat Tracker listening.")

    try:
        for line, line_number in follow_file(CONSOLE_OUTPUT_PATH):
            if line == "export_stats":
                export_json()
            # TF2 Console is just weird and prints it on 2 lines or backwards or NORMAL idk :(
            elif "[Status Cycle] Running" in line or "Status Running" in line or "[Status Cycle]" in line:
                handle_cycle(line_number)

            result = checkPlayerWeapon(line)
            if result[1] is not None:
                update_class(result)
            
    except Exception as e:
        print(f"ERROR: {e}")
