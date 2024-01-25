import discord
# from keep_alive import keep_alive
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents().all()
intents.members = True

client = discord.Client(intents=intents)


# Functions
#calculate Line movement function
def calculate_line_movement():
  results = []
  # Step 1: Get Event IDs
  #api_url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey=5e7c521ab26381b068424419c586233a&regions=us&markets=h2h&oddsFormat=american&bookmakers=draftkings"
  api_url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey=5e7c521ab26381b068424419c586233a&regions=us&markets=h2h&oddsFormat=american&bookmakers=draftkings"
  response = requests.get(api_url)

  # Check if the request was successful (status code 200)
  if response.status_code != 200:
    print(f"Error in API request. Status code: {response.status_code}")
    print (results)

  odds_data = response.json()
  # Extract the first 5 event IDs
  event_ids = [game['id'] for game in odds_data[:5]]

  # Step 2: Iterate Through Event IDs
  for event_id in event_ids:
    # Step 3: Get Current and Previous Odds
    #current_api_url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey=5e7c521ab26381b068424419c586233a&regions=us&markets=h2h&oddsFormat=american&bookmakers=draftkings&eventIds={event_id}"
    current_api_url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey=5e7c521ab26381b068424419c586233a&regions=us&markets=h2h&oddsFormat=american&bookmakers=draftkings&eventIds={event_id}"
    current_response = requests.get(current_api_url)

    # Check if the request was successful (status code 200)
    if current_response.status_code != 200:
      print(
          f"Error in API request. Status code: {current_response.status_code}")
      continue

    current_odds = current_response.json()

    if not current_odds or not current_odds[0].get('bookmakers'):
      print("No odds or bookmakers available for the current event ID.")
      continue

    # Call the API to get previous odds
    previous_timestamp = (datetime.utcnow() -
                            timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    #previous_api_url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds-history/?apiKey=5e7c521ab26381b068424419c586233a&regions=us&markets=h2h&date=2023-12-30T17:14:40Z&oddsFormat=american&eventIds={event_id}&bookmakers=draftkings"
    previous_api_url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds-history/?apiKey=5e7c521ab26381b068424419c586233a&regions=us&markets=h2h&date={previous_timestamp}&bookmakers=draftkings&oddsFormat=american&eventIds={event_id}"
    previous_response = requests.get(previous_api_url)

    # Check if the request was successful (status code 200)
    if previous_response.status_code != 200:
      print(
          f"Error in API request. Status code: {previous_response.status_code}"
      )
      continue

    previous_odds = previous_response.json()

    if not previous_odds:
      print("No previous odds available for the current event ID.")
      continue

    # Step 4: Calculate Time Difference
    current_timestamp = current_odds[0]['bookmakers'][0]['markets'][0][
        'last_update']
    previous_timestamp = previous_odds['timestamp']
    current_time = datetime.strptime(current_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    previous_time = datetime.strptime(previous_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    time_difference = (current_time - previous_time).seconds // 3600

    # Step 5: Calculate Line Movement
    current_team_1_price = current_odds[0]['bookmakers'][0]['markets'][0][
        'outcomes'][0]['price']
    previous_team_1_price = previous_odds['data'][0]['bookmakers'][0][
        'markets'][0]['outcomes'][0]['price']

    current_team_2_price = current_odds[0]['bookmakers'][0]['markets'][0][
        'outcomes'][1]['price']
    previous_team_2_price = previous_odds['data'][0]['bookmakers'][0][
        'markets'][0]['outcomes'][1]['price']

    line_movement_percentage_home = round(
        ((current_team_1_price - previous_team_1_price) /
          abs(previous_team_1_price)) * 100, 1)
    line_movement_percentage_away = round(
        ((current_team_2_price - previous_team_2_price) /
          abs(previous_team_2_price)) * 100, 1)

    # Step 6: Print Results
    team_1 = current_odds[0]['bookmakers'][0]['markets'][0]['outcomes'][
        0]['name']
    team_2 = current_odds[0]['bookmakers'][0]['markets'][0]['outcomes'][
        1]['name']

    results.append(
        f"{team_1} moneyline has moved {line_movement_percentage_home}% "
        f"from {previous_team_1_price} to {current_team_1_price} in the past {time_difference} hours."
    )

    results.append(
        f"{team_2} moneyline has moved {line_movement_percentage_away}% "
        f"from {previous_team_2_price} to {current_team_2_price} in the past {time_difference} hours."
    )

    # print (results)

    print(f"{team_1} moneyline has moved {line_movement_percentage_home}% "
        f"from {previous_team_1_price} to {current_team_1_price} in the past {time_difference} hours.")

    print(f"{team_2} moneyline has moved {line_movement_percentage_away}% "
        f"from {previous_team_2_price} to {current_team_2_price} in the past {time_difference} hours.")


#onready and on message functions for discord
# @client.event
# async def on_ready():
#   print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message):
  if message.author == client.user:
    return

  ## Start of creating our discord bot Commands##
  #command for line movement results
  if message.content.startswith("$results"):
    results = calculate_line_movement()

#     # Send each prediction as a separate message
    for result in results:
      await message.channel.send(result)


# keep_alive()
client.run(DISCORD_TOKEN)
