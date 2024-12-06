import serial
import time
import pygame
import requests
from bs4 import BeautifulSoup
import json

# Initialize pygame mixer
pygame.mixer.init()

# Sound file mapping
sounds = {
    "block": r"C:\Users\hossa\Documents\599A3\CPSC599A3\block.mp3",
    "punch": r"C:\Users\hossa\Documents\599A3\CPSC599A3\Punch.mp3",
    "powerUp": r"C:\Users\hossa\Documents\599A3\CPSC599A3\PowerUp.mp3",
    "superBlock": r"C:\Users\hossa\Documents\599A3\CPSC599A3\SuperBlock.mp3",
    "combination": r"C:\Users\hossa\Documents\599A3\CPSC599A3\combinationAttack.mp3"
}


# Connect to Arduino
arduino_port = "COM3"  # Change this to your Arduino's port
baud_rate = 9600
ser = serial.Serial(arduino_port, baud_rate)
time.sleep(2)  # Wait for Arduino to initialize

print("Connected to Arduino.")

# Function to scrape the latest match result
def get_latest_match(player_name):
    # Load cookies from file
    with open("cookies.json", "r") as file:
        cookies = json.load(file)

    # Convert cookies into a format compatible with requests
    session_cookies = {cookie["name"]: cookie["value"] for cookie in cookies}

    # URL to scrape
    url = "https://www.streetfighter.com/6/buckler/profile/3035797296/battlelog/casual?page=1"

    # Headers for the request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    }

    response = requests.get(url, headers=headers, cookies=session_cookies)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        newest_match = soup.find("div", class_="battle_data_inner_log__p5QL6")

        if newest_match:
            # Extract the match date
            match_date_div = newest_match.find("p", class_="battle_data_date__f1sP6")
            match_date = match_date_div.get_text(strip=True) if match_date_div else None

            # Extract player names
            player_1_div = newest_match.find("p", class_="battle_data_name_p1__Ookss")
            player_2_div = newest_match.find("p", class_="battle_data_name_p2__ua7Oo")
            player_1 = player_1_div.find("span", class_="battle_data_name__IPyjF").get_text(strip=True) if player_1_div else None
            player_2 = player_2_div.find("span", class_="battle_data_name__IPyjF").get_text(strip=True) if player_2_div else None

            # Determine the result
            if player_name == player_1:
                result_div = newest_match.find("li", class_="battle_data_player_1__LemvG")
                result = "loss" if result_div and "battle_data_lose__ltUN0" in result_div["class"] else "win"
            elif player_name == player_2:
                result_div = newest_match.find("li", class_="battle_data_player_2__STQb6")
                result = "win" if result_div and "battle_data_win__8Y4Me" in result_div["class"] else "loss"
            else:
                return None, None  # Player not involved in this match

            return result, match_date

    return None, None

# Player details
player_name = "Aman"
last_sent_match_time = None  # To track the last sent match

# Ignore the first match result
print("Fetching the first match to ignore...")
_, last_sent_match_time = get_latest_match(player_name)
if last_sent_match_time:
    print(f"Ignored match date: {last_sent_match_time}")
else:
    print("No match data found to ignore. Starting fresh.")

# Main loop
while True:
    # Fetch the latest match result
    match_result, match_time = get_latest_match(player_name)

    if match_result and match_time != last_sent_match_time:
        # Send the result to Arduino
        ser.write(match_result.encode("utf-8"))
        print(f"Sent '{match_result}' to Arduino.")

        # Wait for a response from Arduino
        command = None
        while not ser.in_waiting:  # Wait until data is available
            time.sleep(0.1)

        command = ser.readline().decode('utf-8').strip()
        print(f"Received command: {command}")

        if command in sounds:
            print(f"Playing sound for: {command}")

            # Stop any currently playing sound
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()

            # Load and play the new sound
            pygame.mixer.music.load(sounds[command])
            pygame.mixer.music.play()

            # Wait until the sound finishes playing
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        else:
            print(f"No sound mapped for command: {command}")

        # Update the last sent match time
        last_sent_match_time = match_time
    else:
        print("No new match found or result unchanged.")

    # Wait before polling again
    time.sleep(10)  # Adjust polling frequency as needed

# Close the serial connection
ser.close()
