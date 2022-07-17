# SaveMaxer
## Folders
- libraries: 3th party libraries from PyVZ2. **GPL-3.0 LICENCE**
- options: templates (see below)
- options_unused: unused templates
## Files
- fail.txt: file with the last errors
- max.py a tool to generate PVZ2 Save Files
- README.md: this file

## Templates
All info is sorted alphabetically on **FILE NAME**
### Group Format:
```
[KEY]--[INFO]
````
* [KEY], **case-sensitive**, is the key for selecting a template
* [INFO], is the info displayed about the group
* Example:
	```
	a--Android Templates
	```
* Displayed: `Android Templates`

### Naming Format:
```
[KEY]--[UNPACK_INFO]--[PATCH_INFO].json
````
* [KEY], **case-sensitive**, is the key for selecting a template
* [UNPACK_INFO], is the info displayed during unpacking
* [PATCH_INFO], is the info displayed during patching
* Example:
	```
	5--Decode RTON--Encode JSON.json
	```
* Displayed: `5: Decode RTON`

## JSON options
Key | Purpose
--- | ---
prefix | Prefix for profile names
profiles | Profiles, see **Profiles**

### Profiles
Key | Purpose
--- | ---
generated_uid | Generate uid, **string:** use this as "uid"
enable_gems | Enable setting gems, **number:** use this as "v"
generated_name | Generate name, **string:** use this as "n"
accept_updated_terms | Accept updated terms, **number:** use this as "i"
last_level | Last played level
coins | Coins
gems | Gems
gauntlets | Gauntlets
mints | Mints
penny_fuel | Penny fuel
plants | Last plant ID, **list:** use this as "p"
killed_zombies | Last killed zombie ID, **list:** use this as "kz"
old_world_map | Old world map, see **World Map**, **list:** use this as "wm"
new_world_map | New world map, see **World Map**, **list:** use this as "wmed"
game_features | Last game feature ID, **list:** use this as "gf"
narrations | Last narration ID, **list:** use this as "ne"
travel_log_narrations | Last travel log narration ID, **list:** use this as "ct"
danger_rooms | Danger rooms, see **Danger Room**, **list:** use this as "wm"
costumes | Last costume ID, **list:** use this as "cos"
power_up_counts | Power up counts, see **Power Ups**, **list:** use this as "pr"
treasure_yeti | Treasure yeti level name, **object:** use this as "tyi"
boosted_plants_backup | Last boosted plant ID backup, **list:** use this as "pbi"
zen_garden_plants | Zen Garden Plants
bought_plant_pots | Bought plant pots, **list:** use this as upsi
sprouts | Sprouts
boosted_plants | Last boosted plant ID, **list:** use this as "pli"
start_from_zen_garden | Start from zen garden
enable_treasure_yeti | Enable treasure yeti, **number:** use this as "mcs"
played_mini_games | Played mini games, see **Mini Games**, **list:** use this as **ap**
collected_rewards | Collected rewards, see **Rewards**, **list:** use this as **up**
upgraded_plants | Upgraded plants, see **Upgraded Plants**, **list:** use this as "plis"

### World Map
Key | Purpose
--- | ---
**WORLD ID** | last level ID, **list:** use this as levels

### Danger Room
Key | Purpose
--- | ---
**WORLD NAME** | Danger Room Options, see **Danger Room Options**

### Danger Room Options
Key | Purpose
--- | ---
current_level | Current level
high_score | High score
plant_food | Plant food
lawn_mowers | Lawn mower layout
plants | Last plant ID, **list:** use this as "sb"
draw_card | Draw a card

### Power Ups
Key | Purpose
--- | ---
**POWERUP NAME** | Power up count

### Mini Games
Key | Purpose
--- | ---
mini_games | See **Mini Game Options**
wave | Zen Garden Endless Wave

### Mini Game options
Key | Purpose
--- | ---
**PACK ID** | **MINI GAME IDS**

### Upgraded Plants
Key | Purpose
--- | ---
plants | Last plant ID, **list:** use this as plants
level | Plant level
seed_packets | Plant seed packets
mastery | Plant Mastery level