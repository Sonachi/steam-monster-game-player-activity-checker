import json
import urllib.request
import logging
import time
from multiprocessing.pool import ThreadPool

def calculate_upgrade_cost(cost, cost_exponential_base, level):
  #Calculates sum of geometric series
  return cost*(1-cost_exponential_base**level)/(1-cost_exponential_base)
  
def check_player(steamid, gameid):
  #Check a player's stats in specified room
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
      for player in players["response"]["names"][:10]:
        steamid = 76561197960265728+int(player["accountid"])
        async_result = pool.apply_async(check_player, (steamid, gameid))
        return_val = async_result.get()
        player_dict[steamid]=return_val
        checked_count += 1
        dt = time.time() - prev_time
        if dt > 30:
            logging.debug("Checked "+str(checked_count)+" accounts in room. Last checked: "+ str(steamid))
            prev_time = time.time()         
      sorted_players = sorted(player_dict.items(), key=lambda t: t[1])
      f = open("Room"str(gameid)+" "+time.strftime('%Y%m%d-%H%M%S')+".dump", 'w')
      json.dump(sorted_players,f)
      f.close()
      
      for top in sorted_players[:150]:
        print(top) 
      
logging.basicConfig(filename='scanner.log',level=logging.DEBUG, format='%(asctime)s %(message)s')
with open('upgrades.json') as upgrades_data:    
  upgrades = json.load(upgrades_data)
do_scan()