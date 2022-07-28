from datetime import datetime
from os.path import join as osjoin
from json import dump
from struct import pack

# 3th party libraries
from libraries.pyvz2nineteendo import LogError
from libraries.pyvz2rton import JSONDecoder

options = {
# Default options
	"prefix": "AHZ",
	"profiles": []
}

def member(member, check):
	return type(member) == check
def get_list(start = 1, last_id = 0):
	if member(last_id, list):
		return last_id
	else:
		return list(range(start, last_id + 1))
def get_uid(generated_uid = True, prefix = "", id = 0):
	if member(generated_uid, str):
		return generated_uid
	else:
		a, b = divmod(hash(get_n(generated_uid, prefix, id)), 4294967296)
		b, c = divmod(b, 65536)
		return repr(b) + "." + repr(c) + "." + pack(">i", a).hex()
def get_v(enable_gems = True):
	if member(enable_gems, int):
		return enable_gems
	elif enable_gems:
		return 9 # Allow gems to be set in the stats
	else:
		return 8 # Prevent gems to be set in the stats
def get_n(generated_name = True, prefix = "", id = 0):
	if member(generated_name, str):
		return generated_name
	elif generated_name:
		return prefix + repr(id)
	else:
		return prefix
def get_i(accept_updated_terms = True, i = 0):
	if member(accept_updated_terms, int):
		return accept_updated_terms
	elif accept_updated_terms:
		return int(datetime.timestamp(datetime.now())) + i # # Disable updated terms message
	else:
		return 0 # Enable updated terms message
def get_p(plants = 256):
	if member(plants, list):
		return plants
	else:
		removed_plants = [43, 45, 46, 47, 48, 49, 56, 57, 73]
		return [plant for plant in get_list(1, plants) if not plant in removed_plants]
def get_wm(old_world_map = {}):
	if member(old_world_map, list):
		return old_world_map
	else:
		wm = []
		for world_id in old_world_map:
			for level_id in get_list(1, old_world_map[world_id]):
				level = {}
				level["W"] = int(world_id) # World ID
				level["E"] = level_id # Level ID
				level["S"] = 3 # Unknown
				level["C"] = 7 # Unknown
				level["N"] = 0 # Unknown
				level["G"] = 0 # Unknown
				
				wm.append(level)
		return wm
def get_wmed(new_world_map = {}):
	if member(new_world_map, list):
		return new_world_map
	else:
		wmed = []
		for world_id in new_world_map:
			world = {}
			world["w"] = int(world_id) # World ID
			
			e = []
			for level_id in get_list(1, new_world_map[world_id]):
				level = {}
				level["i"] = level_id # Level ID
				e.append(level)
			
			world["e"] = e # Levels
			world["r"] = False # Unknown
			
			wmed.append(world)
		return wmed
def get_dri(danger_rooms = {}):
	if member(danger_rooms, list):
		return danger_rooms
	else:
		dri = []
		for world_name in danger_rooms:
			world_options = danger_rooms[world_name]
			dangerroom = {}
			dangerroom["wn"] = world_name # World Name
			dangerroom["cl"] = world_options["current_level"] # Current Level
			dangerroom["hl"] = world_options["high_score"] # High Score
			dangerroom["pfco"] = world_options["plant_food"] # Plantfood
			dangerroom["l"] = world_options["lawn_mowers"] # Lawn Mowers https://images.wikia.com/ernestoam/images/b/b1/Endless_Zone_Lawn_Mower_Set_Up_IDs.png
			dangerroom["sb"] = get_p(world_options["plants"]) # Plants
			dangerroom["ts"] = 0 # Unknown
			dangerroom["pl"] = 0 # Unknown
			dangerroom["hr"] = world_options["draw_card"] # Draw a Card
			dangerroom["hm"] = False # Unknown
			
			dri.append(dangerroom)
		return dri
def get_pr(power_up_counts = {}):
	if member(power_up_counts, list):
		return power_up_counts
	else:
		pr = []
		for powerup_name in power_up_counts:
			powerup = {}
			powerup["n"] = powerup_name # Powerup name
			powerup["i"] = power_up_counts[powerup_name]
			
			pr.append(powerup)
		return pr
def get_tyi(level_name = "egypt1"):
	if member(level_name, dict):
		return level_name
	else:
		tyi = {}
		tyi["wml"] = level_name # Level Name
		tyi["lst"] = 0 # Unknown
		tyi["nst"] = 0 # Unknown
		return tyi
def get_pbi(boosted_plants = 256):
	if member(boosted_plants, list):
		return boosted_plants
	else:
		unboosted_plants = [29, 30, 32, 33, 41, 68, 72, 79, 89, 94, 97, 111, 118, 124, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 145, 155, 181, 184, 188]
		pbi = []
		for boosted_plant in range(1, boosted_plants + 1):
			if not boosted_plant in unboosted_plants:
				plant = {}
				plant["p"] = boosted_plant # Plant ID
				plant["c"] = 127 # Unknown
				plant["a"] = 4 # Boost Type https://pastebin.com/tpZaxBgX
				plant["b"] = [] # Unknown
				plant["t"] = 0 # Next time accessible
				
				pbi.append(plant)
		return pbi
def get_upsi(bought_plant_pots = 6):
	if member(bought_plant_pots, list):
		return bought_plant_pots
	else:
		bought_pot_ids = [201, 301, 2, 102, 202, 302]
		return sorted([bought_pot_ids[extra_pot] for extra_pot in range(0, bought_plant_pots)])
def get_mcs(enable_treasure_yeti = True):
	if member(enable_treasure_yeti, int):
		return enable_treasure_yeti
	elif enable_treasure_yeti:
		return 3
	else:
		return 2 # Unknown
def get_ap(played_mini_games = {}):
	if member(played_mini_games, list):
		return played_mini_games
	else:
		ap = []
		for played_pack in played_mini_games["mini_games"]:
			pack = {}
			pack["i"] = int(played_pack) # Mini Game ID
			
			lp = []
			for level_id in played_mini_games["mini_games"][played_pack]:
				level = {}
				level["i"] = level_id # Level ID
				level["p"] = played_mini_games["wave"] # Wave
				level["s"] = 1 # Unknown
				
				lp.append(level)
			
			pack["lp"] = lp
			
			ap.append(pack)
		return ap
def get_up(collected_rewards = {}):
	if member(collected_rewards, list):
		return collected_rewards
	else:
		ap = []
		for minigame_id in collected_rewards:
			minigame = {}
			minigame["i"] = int(minigame_id) # Mini Game ID
			
			up = []
			for played_pack in collected_rewards[minigame_id]:
				pack = {}
				pack["i"] = played_pack # pack ID
				pack["p"] = 0 # Unknown
				
				up.append(pack)
			
			minigame["up"] = up
			
			ap.append(minigame)
		return ap
def get_plis(upgraded_plants = 256):
	if member(upgraded_plants, list):
		return upgraded_plants
	else:
		plis = []
		for upgraded_plant in get_p(upgraded_plants["plants"]):
			plant = {}
			plant["p"] = upgraded_plant # Plant ID
			plant["l"] = upgraded_plants["level"] # Plant Level
			plant["x"] = upgraded_plants["seed_packets"] # Seed mini_gameets
			plant["m"] = upgraded_plants["mastery"] # Plant Mastery
			
			plis.append(plant)
		return plis
def generate_save_file():
	json_data = {}
	json_data["version"] = 1

	objects = []
	entries = options["profiles"]
	split_task(len(entries))
	for i, profile_options in enumerate(entries):
		profile = {}
		profile["uid"] = get_uid(profile_options["generated_uid"], options["prefix"], i) # Uid
		profile["objclass"] = "PlayerInfo" # Player Info
		
		objdata = {}
		objdata["v"] = get_v(profile_options["enable_gems"])
		objdata["n"] = get_n(profile_options["generated_name"], options["prefix"], i) # Name
		objdata["i"] = get_i(profile_options["accept_updated_terms"], i)
		objdata["l"] = profile_options["last_level"] # Last level
		objdata["c"] = profile_options["coins"] # Coins
		objdata["g"] = profile_options["gems"] # Gems
		objdata["t"] = profile_options["gauntlets"] # Gauntlets
		objdata["m"] = profile_options["mints"] # Mints
		objdata["pf"] = profile_options["penny_fuel"] # Penny Fuel
		#objdata["pt"] = 888888888 # Perk Progression
		objdata["p"] = get_p(profile_options["plants"]) # Plants https://pastebin.com/bSeTQTRa https://pastebin.com/JyCbwEq2
		objdata["kz"] = get_list(0, profile_options["killed_zombies"]) # Killed Zombies https://pastebin.com/1WhUWS1Q
		objdata["wm"] = get_wm(profile_options["old_world_map"]) # Old World Map
		objdata["wmed"] = get_wmed(profile_options["new_world_map"]) # New World Map
		objdata["gf"] = get_list(0, profile_options["game_features"]) # Game Features https://pastebin.com/W1hSXBPB
		objdata["ne"] = get_list(1, profile_options["narrations"]) # Narrations https://pastebin.com/hHvqxxr2
		objdata["ct"] = get_list(1, profile_options["travel_log_narrations"]) # Travel Log
		objdata["dri"] = get_dri(profile_options["danger_rooms"]) # Dangerroom
		objdata["cos"] = get_list(0, profile_options["costumes"]) # Costumes https://pastebin.com/RG41dYRv
		objdata["pr"] = get_pr(profile_options["power_up_counts"]) # Powerups
		objdata["tyi"] = get_tyi(profile_options["treasure_yeti"]) # Treasure Yeti In
		objdata["pbi"] = get_pbi(profile_options["boosted_plants_backup"]) # Boosted Plant Backup?
		objdata["gpi"] = profile_options["zen_garden_plants"] # Zen Garden Plants
		objdata["upsi"] = get_upsi(profile_options["bought_plant_pots"]) # Plant Pots
		objdata["spr"] = profile_options["sprouts"] # Sprouts
		objdata["pli"] = get_pbi(profile_options["boosted_plants"]) # Boosted Plants
		objdata["izg"] = profile_options["start_from_zen_garden"] # Start from Zen Garden
		objdata["mcs"] = get_mcs(profile_options["enable_treasure_yeti"]) # Enable Treasure Yeti
		objdata["ap"] = get_ap(profile_options["played_mini_games"]) # Played Mini Games
		objdata["puc"] = get_up(profile_options["collected_rewards"]) # Collected rewards
		objdata["plis"] = get_plis(profile_options["upgraded_plants"]) # Plant Leveling

		profile["objdata"] = objdata # Profile Data
		
		objects.append(profile)
		finish_sub_task()
	json_data["objects"] = objects # Profiles
	merge_task()
	return json_data

# Start of the code
try:
	logerror = LogError()
	application_path = logerror.application_path
	error_message = logerror.error_message
	warning_message = logerror.warning_message
	input_level = logerror.input_level
	split_task = logerror.split_task
	merge_task = logerror.merge_task
	finish_sub_task = logerror.finish_sub_task

	logerror.check_version(3, 9, 0)
	branches = {
		"beta": "Beta 1.2.1c Progress bar after a suggestion of TheEarthIsGreenNBlue",
		"master": "Merge branch 'beta'"
	}
	release_tag = "1.2"
	print("""\033[95m
\033[1mSaveMaxer v1.2.1b (c) 2022 Nineteendo\033[22m
\033[1mFollow PyVZ2 development:\033[22m \033[4mhttps://discord.gg/CVZdcGKVSw\033[24m
\033[0m""")
	getupdate = logerror.get_update("Nineteendo/PVZ2tools", branches, release_tag)
	options = logerror.load_template(options, 2)
	encode_root_object = JSONDecoder().encode_root_object

	logerror.set_levels(2)
	split_task(3)
	json_data = generate_save_file()
	finish_sub_task()
	dump(json_data, open(osjoin(application_path, "pp.dat.json"), "w"), ensure_ascii = False, indent = 4)
	finish_sub_task()
	patch_data = JSONDecoder().encode_root_object(open(osjoin(application_path, "pp.dat.json"), "rb"))
	open(osjoin(application_path, "pp.dat"), "wb").write(patch_data)
	finish_sub_task()
	
	logerror.finish_program()
except Exception as e:
	logerror.set_levels(0)
	error_message(e)
except BaseException as e:
	logerror.set_levels(0)
	warning_message(type(e).__name__ + " : " + str(e))
logerror.close() # Close log