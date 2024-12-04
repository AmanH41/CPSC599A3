import requests
from bs4 import BeautifulSoup
import json

def get_latest_match(player_name, last_sent_match_time):
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

            # Skip if the match is not new
            if match_date and match_date != last_sent_match_time:
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
                    return None, last_sent_match_time  # Player not involved in this match

                print(f"Date: {match_date}, Player 1: {player_1}, Player 2: {player_2}, Result: {result}")
                return result, match_date

    return None, last_sent_match_time
