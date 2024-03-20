import requests
from bs4 import BeautifulSoup
import csv
from tqdm import tqdm  # Import tqdm for the progress bar

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Initial URL without the page number
base_url = 'https://prosettings.net/games/cs2/'
max_pages = 35
# Initialize the page number
page_num = 1

# Create a list to store the player information
player_info_list = []
for page_num in tqdm(range(1, max_pages + 1), desc='Processing Pages'):
    if page_num == 1:
        url = base_url  # First page
    else:
        url = f'{base_url}page/{page_num}/'  # Subsequent pages
    
    response = requests.get(url, headers=headers)
    
    # Break the loop if the page is not found
    if response.status_code != 200:
        break
    
    page_content = response.content
    soup = BeautifulSoup(page_content, 'html.parser')
    
    player_divs = soup.find_all('div', class_='player_heading-wrapper')
    
    # Break if no player divs found on the page
    if not player_divs:
        break
    
    for player_div in player_divs:
        player_name = player_div.find('h4').find('a').text
        player_link = player_div.find('h4').find('a')['href'] + '#cs2'  # Add #cs2 to the player's URL

        player_response = requests.get(player_link, headers=headers)

        if player_response.status_code == 200:
            player_page_content = player_response.content
            player_soup = BeautifulSoup(player_page_content, 'html.parser')

            last_updated = player_soup.find('div', class_='last_updated').find('time').text

            table_rows = player_soup.find_all('tr', class_=["format-text", "format-date_picker", "format-country", "format-text"])
            player_info = {'Player Name': player_name, 'Last Updated': last_updated}

            for row in table_rows:
                key = row.find('th').text.strip()
                value = row.find('td').text.strip()
                player_info[key] = value

            h3_elements = player_soup.find_all('h3')

            for h3_element in h3_elements:
                if h3_element.text.strip() == 'Mouse':
                    mouse_model = h3_element.find_next('h4').text
                    player_info['Mouse Model'] = mouse_model

                    mouse_dpi = h3_element.find_next('tr', class_='field-dpi').find('td').text
                    player_info['Mouse DPI'] = mouse_dpi

                    mouse_sensitivity = h3_element.find_next('tr', class_='field-sensitivity').find('td').text
                    player_info['Mouse Sensitivity'] = mouse_sensitivity

                    break
            else:
                player_info['Mouse Model'] = 'N/A'
                player_info['Mouse DPI'] = 'N/A'
                player_info['Mouse Sensitivity'] = 'N/A'

            desired_fields = ['Player Name', 'Last Updated', 'Name', 'Birthday', 'Country', 'Team', 'Mouse Model', 'Mouse DPI', 'Mouse Sensitivity']
            filtered_player_info = {key: player_info[key] for key in desired_fields if key in player_info}
            player_info_list.append(filtered_player_info)

        else:
            print('Failed to retrieve content for player:', player_name, 'Status code:', player_response.status_code)

    page_num += 1  # Increment to fetch the next page

# After collecting all data, write to CSV
with open('player_info.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = desired_fields
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for player_info in player_info_list:
        writer.writerow(player_info)
