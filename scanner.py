import json
import urllib.request
import logging
import time
from multiprocessing.pool import ThreadPool

def calculate_upgrade_cost(cost, cost_exponential_base, level):
  #Calculates sum of geometric series
  return cost*(1-cost_exponential_base**level)/(1-cost_exponential_base)
  
def check_player(steamid, gameid):
  gold = 0
  try:
    with urllib.request.urlopen("http://steamapi-a.akamaihd.net/ITowerAttackMiniGameService/GetPlayerData/v0001/?gameid="+str(gameid)+"&steamid="+str(steamid)+"&include_tech_tree=1&format=json") as player_data:
      player_info = json.loads(player_data.read().decode('utf-8'))
      if "gold" not in player_info["response"]["player_data"]:
        return 0
      gold = player_info["response"]["player_data"]["gold"]
      tech_tree = player_info["response"]["tech_tree"]
      
      #Calculate upgrades cost
      for upgrade in tech_tree["upgrades"]:
        if upgrade["level"]>0:
          cur_upgrade = upgrades[upgrade["upgrade"]]
          gold += calculate_upgrade_cost(cur_upgrade["cost"],float(cur_upgrade["cost_exponential_base"]),upgrade["level"])
      return gold
  except Exception as e:
    logging.exception(e)
    print(steamid)
    
def do_scan():
  prev_time = time.time()
  player_dict = {}
  gameid = 37559
  with urllib.request.urlopen("https://steamapi-a.akamaihd.net/ITowerAttackMiniGameService/GetPlayerNames/v0001/?gameid="+str(gameid)+"&format=json") as server_data:
  
    logging.debug("Got room data for room #"+str(gameid))
    players = json.loads(server_data.read().decode('utf-8'))
    checked_count = 0
    with ThreadPool(processes=6) as pool:
      for player in players["response"]["names"]:
        steamid = 76561197960265728+int(player["accountid"])
        async_result = pool.apply_async(check_player, (steamid, gameid))
        return_val = async_result.get()
        player_dict[steamid]=return_val
        checked_count += 1
        dt = time.time() - prev_time
        if dt > 30:
            logging.debug("Checked "+str(checked_count)+" accounts in room. Last checked: "+ str(steamid))
            prev_time = time.time()         
      sorted_players = sorted(player_dict.items(), key=operator.itemgetter(1))
      for top in sorted_players[:150]:
        print(top) 
      
logging.basicConfig(filename='scanner.log',level=logging.DEBUG, format='%(asctime)s %(message)s')
upgrades_string = """[{
    "name": "Light Armor",
    "multiplier": "1.3",
    "type": 0,
    "cost": 100,
    "cost_exponential_base": "2.5",
    "desc": "Increases your health (HP)"
  },
  {
    "name": "Auto-fire Cannon",
    "initial_value": 10,
    "multiplier": 1,
    "type": 1,
    "cost": 150,
    "cost_exponential_base": "1.3",
    "desc": "Inflicts damage on your target every second"
  },
  {
    "name": "Armor Piercing Round",
    "multiplier": 1,
    "type": 2,
    "cost": 200,
    "cost_exponential_base": "1.2",
    "desc": "Increases your click damage"
  },
  {
    "name": "+Damage to Fire Monsters",
    "multiplier": "1.5",
    "type": 3,
    "cost": 50,
    "cost_exponential_base": "2.2",
    "desc": "Do additional damage to Fire Monsters"
  },
  {
    "name": "+Damage to Water Monsters",
    "multiplier": "1.5",
    "type": 4,
    "cost": 50,
    "cost_exponential_base": "2.2",
    "desc": "Do additional damage to Water Monsters"
  },
  {
    "name": "+Damage to Air Monsters",
    "multiplier": "1.5",
    "type": 5,
    "cost": 50,
    "cost_exponential_base": "2.2",
    "desc": "Do additional damage to Air Monsters"
  },
  {
    "name": "+Damage to Earth Monsters",
    "multiplier": "1.5",
    "type": 6,
    "cost": 50,
    "cost_exponential_base": "2.2",
    "desc": "Do additional damage to Earth Monsters"
  },
  {
    "name": "Lucky Shot",
    "multiplier": "1.5",
    "type": 7,
    "cost": 50,
    "cost_exponential_base": "2.5",
    "required_upgrade": 2,
    "required_upgrade_level": 5,
    "desc": "Increase your critical hit click damage"
  },
  {
    "name": "Heavy Armor",
    "multiplier": 10,
    "type": 0,
    "cost": 10000,
    "cost_exponential_base": "2.2",
    "required_upgrade": 0,
    "required_upgrade_level": 10,
    "desc": "Increases your health (HP)"
  },
  {
    "name": "Advanced Targeting",
    "multiplier": 10,
    "type": 1,
    "cost": 10000,
    "cost_exponential_base": "2.2",
    "required_upgrade": 1,
    "required_upgrade_level": 10,
    "desc": "Increases the damage inflicted by your Auto-fire Cannon"
  },
  {
    "name": "Explosive Rounds",
    "multiplier": 10,
    "type": 2,
    "cost": 10000,
    "cost_exponential_base": "2.2",
    "required_upgrade": 2,
    "required_upgrade_level": 10,
    "desc": "Increases your click damage"
  },
  {
    "name": "Medics",
    "type": 8,
    "cost": 5000,
    "cost_exponential_base": "2.2",
    "required_upgrade": 0,
    "ability": 7,
    "desc": "Slowly heals everyone in the current lane that is still alive"
  },
  {
    "name": "Morale Booster",
    "type": 8,
    "cost": 10000000,
    "cost_exponential_base": "2.2",
    "required_upgrade": 1,
    "required_upgrade_level": 20,
    "ability": 5,
    "desc": "Increases all damage done by players in the current lane"
  },
  {
    "name": "Good Luck Charms",
    "type": 8,
    "cost": 1000000,
    "cost_exponential_base": "2.2",
    "required_upgrade": 2,
    "required_upgrade_level": 5,
    "ability": 6,
    "desc": "Increases chance to do critical click damage for players in the current lane"
  },
  {
    "name": "Metal Detector",
    "type": 8,
    "cost": 10000000,
    "cost_exponential_base": "2.2",
    "ability": 8,
    "desc": "Increases gold dropped by enemies in the current lane"
  },
  {
    "name": "Decrease Cooldowns",
    "type": 8,
    "cost": 10000000,
    "cost_exponential_base": "2.2",
    "ability": 9,
    "desc": "While active, decreases cooldowns for any newly activated ability in the current lane (does not stack)."
  },
  {
    "name": "Tactical Nuke",
    "type": 8,
    "cost": 100000,
    "cost_exponential_base": 5,
    "required_upgrade": 2,
    "required_upgrade_level": 10,
    "ability": 10,
    "desc": "Launches a tactical nuclear missile that does high damage to your current target."
  },
  {
    "name": "Cluster Bomb",
    "type": 8,
    "cost": 1000000,
    "cost_exponential_base": "2.2",
    "ability": 11,
    "required_upgrade": 1,
    "required_upgrade_level": 10,
    "desc": "Drops a cluster bomb, damaging all enemies in your lane."
  },
  {
    "name": "Napalm",
    "type": 8,
    "cost": 2000000,
    "cost_exponential_base": "2.2",
    "ability": 12,
    "required_upgrade": 1,
    "required_upgrade_level": 10,
    "desc": "Drops napalm, inflicting damage on all enemies in your lane over time."
  },
  {
    "name": "Boss Loot",
    "multiplier": "0.01",
    "type": 9,
    "cost": 100000,
    "cost_exponential_base": "2.2",
    "required_upgrade": 1,
    "required_upgrade_level": 10,
    "desc": "Increase your chance to get loot after defeating a boss"
  },
  {
    "name": "Energy Shields",
    "multiplier": 100,
    "type": 0,
    "cost": 100000,
    "cost_exponential_base": "2.2",
    "required_upgrade": 8,
    "required_upgrade_level": 10,
    "desc": "Increases your health (HP)"
  },
  {
    "name": "Farming Equipment",
    "multiplier": 100,
    "type": 1,
    "cost": 100000,
    "cost_exponential_base": "2.2",
    "required_upgrade": 9,
    "required_upgrade_level": 10,
    "desc": "Increases the damage inflicted by your Auto-fire Cannon"
  },
  {
    "name": "Railgun",
    "multiplier": 100,
    "type": 2,
    "cost": 100000,
    "cost_exponential_base": "2.2",
    "required_upgrade": 10,
    "required_upgrade_level": 10,
    "desc": "Increases your click damage"
  }]"""
upgrades = json.loads(upgrades_string)
do_scan()