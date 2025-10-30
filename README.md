# TF2 Stat Tracker

A Python-based stat tracker that monitors and records player performance from **Team Fortress 2** console logs in real time. It parses console output, tracks kills, deaths, crits, player classes, and exports the data to JSON files for later analysis.

---

## Features

* Real-time monitoring of `console.txt`
* Automatic export of stats to timestamped JSON files
* Tracks kills, deaths, crit kills, KD ratios, and player classes
* Maintains persistent session data using `temp.json`
* Configurable weapon cache for faster processing

---

## Requirements

* Python 3.8+
* Modules:

  ```bash
  pip install -r requirements.txt
  ```

---

# Setup

## WARNING

This script could potentially be classified as a **CHEAT** because it reports the classes of other players in the game. Use at your own risk. The script only has access to information that you, the player, already have.

---

### 1. Clone or download the repository

```bash
git clone https://github.com/kisstopherr/TF2-Stat-Tracker.git
cd TF2-Stat-Tracker
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

**OR**

```bash
pip install colorama
```

### 3. Configure TF2 and required files

* **TF2 Path:** The default TF2 path in `main.py` is:

  ```
  C:\Program Files (x86)\Steam\steamapps\common\Team Fortress 2\tf
  ```

  Update this path in `main.py` if your installation is located elsewhere.

* **Console Logging:** In your TF2 folder, open the `cfg` folder and locate `autoexec.cfg`. Add the following lines:

  ```cfg
  con_logfile console.txt
  con_timestamp 0
  alias export_stats "echo export_stats"
  // Optional: bind [key] "export_stats"
  exec autostatus
  ```

* Move the `autostatus.cfg` file from the repository into the `cfg` folder.

### 4. Run the tracker

```bash
python main.py
```

If everything is set up correctly, the tracker will start monitoring your console log in real time.

--- 


# Basic Script Outline

The script can be broken down into the following main components:


1. **Player Class**

   * Represents each player with attributes: name, current class, kills, deaths, crits, Steam ID, and active status.
   * Methods to update class, increment kills/deaths/crit counts, and log changes.

2. **Data Management**

   * `build_cache()` reads `weapons.json` and builds a mapping of weapons to classes.
   * `clear_temp()` resets `temp.json` to store new session data.
   * `add_temp_players()` updates temporary player data during the session.
   * `export_json()` merges temp data with live data and writes a timestamped JSON export.

3. **Console Parsing**

   * `follow_file()` continuously reads new lines from `console.txt` in real-time.
   * `handle_cycle()` parses the status cycle lines for hostname, map, and current active players.
   * `checkPlayerWeapon()` extracts kill events, weapon class, and crit information from console lines.
   * `update_class()` updates player stats based on parsed kill and class data.

4. **Player Management**

   * `get_player()` finds existing players or creates new player instances.
   * Handles player disconnects and updates active status.

5. **Main Loop**

   * Initializes weapon cache and temp JSON.
   * Watches console log for new lines.
   * Processes status cycles, kill events, and user commands like `export_stats`.
   * Continuously updates player statistics in real time and exports when requested.

This structure allows the script to run continuously while updating player stats dynamically and safely exporting session data.
