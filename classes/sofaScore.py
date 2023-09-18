import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import pytz
from datetime import datetime
import re


class sofaScore:

    ########
    # FUNCTIONS TO INTERACT WITH THE API

    def current_timezone(self):
        current_datetime = datetime.now()

        # Convert the datetime to GMT/UTC timezone
        gmt_timezone = pytz.timezone('GMT')
        current_datetime_utc = gmt_timezone.localize(current_datetime)

        # Format the datetime
        formatted_datetime = current_datetime_utc.strftime(
            '%a, %d %b %Y %H:%M:%S %Z')

        return formatted_datetime

    def get_code(self, link):
        # Get the URL
        url_name = link
        match = re.search(r'\d+$', url_name)

        # Extract the URL code:
        if match:
            last_number = match.group()
            print(last_number)
        else:
            print('No number found in the URL')

        return last_number

    # Clean Coords:
    def clean_coords(self, extra, name, rotate=True):
        dataframes = [item for item in extra[name]
                      if isinstance(item, pd.DataFrame)]

        if not dataframes:
            return extra

        res = pd.concat(dataframes, ignore_index=True)

        if (rotate):
            res = pd.DataFrame(abs(res[['x', 'y']]-100))

        res.columns = [f'x_{name}', f'y_{name}']
        df = extra.drop(name, axis=1)
        df = df.join(res)

        return df

        ########
        # CLEANING DATA

        # Cleaning event info:

    def get_event(self, json):
        event = pd.DataFrame(json)

        # Cleaning event
        data = {
            'homeTeam': [],
            'homeScore': [],
            'awayTeam': [],
            'awayScore': [],
            'tournament': [],
            'venue': [],
        }

        # Iterate data:

        data['homeTeam'].append(pd.DataFrame([event['event']['homeTeam']]))
        data['homeScore'].append(pd.DataFrame([event['event']['homeScore']]))
        data['awayTeam'].append(pd.DataFrame([event['event']['awayTeam']]))
        data['awayScore'].append(pd.DataFrame([event['event']['awayScore']]))
        data['tournament'].append(pd.DataFrame([event['event']['tournament']]))
        data['venue'].append(pd.DataFrame([event['event']['venue']]))

        df = pd.DataFrame(data)

        return df

        # Cleaning Shots

    def get_shotmap(self, json):
        shots = pd.DataFrame(json)

        # Data to iterate:
        data = {
            'player': [],
            'shortName': [],
            'shotType': [],
            'isHome': [],
            'bodyPart': [],
            'xG': [],
            'minute': [],
            'addedTime': [],
            'start': [],
            'block': [],
            'end': [],
            'goal': [],
            'position': [],
        }

        # Transform all data:
        # OVERALL
        for i in range(len(shots)-1):
            # Systematic data:
            # NAMES
            player_one = pd.DataFrame(shots['shotmap'][i])
            # Appending data
            data['player'].append(player_one['player']['name'])
            # Short name
            data['shortName'].append(player_one['player']['shortName'])
            # Position
            data['position'].append(player_one['player']['position'])
            # isHome
            data['isHome'].append(player_one['isHome']['name'])
            # ShotType
            data['shotType'].append(player_one['shotType']['name'])
            # bodyPart
            data['bodyPart'].append(player_one['bodyPart']['name'])
            # xG
            if 'xg' in player_one.columns:
                data['xG'].append(player_one['xg']['name'])
            else:
                data['xG'].append(pd.NA)
            # Minute
            data['minute'].append(player_one['time']['name'])
            # Added-time
            if 'addedTime' in player_one.columns:
                data['addedTime'].append(player_one['addedTime']['name'])
            else:
                data['addedTime'].append(pd.NA)

            # Scrap inside of it
            # Start
            start = pd.DataFrame(player_one['draw']['start'], index=[0])
            data['start'].append(start)

            # block
            if 'block' in player_one['draw'].index:
                block = pd.DataFrame(player_one['draw']['block'], index=[0])
                data['block'].append(block)
            else:
                data['block'].append(pd.NA)

            # endpoint
            endPoint = pd.DataFrame(player_one['draw']['end'], index=[0])
            data['end'].append(endPoint)

            # goal
            goal = pd.DataFrame(player_one['draw']['goal'], index=[0])
            data['goal'].append(goal)

        # Cleaning into a Panda Dataframe:
        df_shots = pd.DataFrame(data).iloc[::-1].reset_index(drop=True)

        # Clean Coords:
        # START
        # res_start = pd.concat(df_shots['start'].tolist(), ignore_index=True)
        # res_start.columns = ['x_start', 'y_start']
        # df_shots = df_shots.drop('start', axis=1)
        # df_shots = df_shots.join(res_start)

        df_shots = self.clean_coords(df_shots, 'start')
        df_shots = self.clean_coords(df_shots, 'block')
        df_shots = self.clean_coords(df_shots, 'end')
        df_shots = self.clean_coords(df_shots, 'goal')

        return df_shots

    # Cleaning Players

        # FUNCTION OF TIMESTAP:
    def get_birth(self, timestap):
        date_of_birth = datetime.fromtimestamp(timestap)
        formatted_date = date_of_birth.strftime('%Y-%m-%d')

        return formatted_date

    # FUNCTION CONVERT PLAYER INFO:

    def convert_player(self, data):
        player = pd.DataFrame([data])
        player['dateOfBirthTimestamp'] = self.get_birth(
            player['dateOfBirthTimestamp'][0])

        return player

    def get_bestPlayers(self, json):
        players = pd.DataFrame(json)

        # Transform data:
        # HOME
        # Home
        players['bestHomeTeamPlayer']['player'] = self.convert_player(
            players['bestHomeTeamPlayer']['player'])
        # Away
        players['bestAwayTeamPlayer']['player'] = self.convert_player(
            players['bestAwayTeamPlayer']['player'])

        return players

    ######
    # GETTING GRAPH

    def get_graph(self, json):
        graph = pd.DataFrame(json)

        # data to iterate:
        data = {
            'min': [],
            'value': [],
            'periodTime': [],
            'periodCount': [],
        }

        # Iterate data:

        for i in range(len(graph)-1):
            all_data = graph.iloc[i, :]
            grab_point = pd.DataFrame([graph['graphPoints'][i]])
            # APPEND DATA:
            # Minute
            data['min'].append(grab_point['minute'][0])
            # Value
            data['value'].append(grab_point['value'][0])
            # period Time
            data['periodTime'].append(all_data['periodTime'])
            # Period Count
            data['periodCount'].append(all_data['periodCount'])

        # Recopile into a Pandas

        df = pd.DataFrame(data)

        return df

    ########
    # EXECUTION FUNCTIONS

    def get_match(self, link):
        code_match = self.get_code(link)

        # set the header:
        headers = {
            'authority': 'api.sofascore.com',
            'accept': '*/*',
            'accept-language': 'es,es-ES;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'max-age=0',
            'if-none-match': 'W/"e22c025662"',
            'origin': 'https://www.sofascore.com',
            'referer': 'https://www.sofascore.com/',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.62',
        }

        # Set timezone to the correct one:
        headers['If-Modified-Since'] = self.current_timezone()

        # Event info
        response_event = requests.get(
            f'https://api.sofascore.com/api/v1/event/{code_match}', headers=headers)

        if response_event.status_code == 200:
            event = response_event.json()
            df_event = self.get_event(event)
        else:
            None

        # Shotmap
        response_shots = requests.get(
            f'https://api.sofascore.com/api/v1/event/{code_match}/shotmap', headers=headers)

        if response_shots.status_code == 200:
            shots = response_shots.json()
            df_shots = self.get_shotmap(shots)
        else:
            None

        # Best two players:
        response_players = requests.get(
            f'https://api.sofascore.com/api/v1/event/{code_match}/best-players', headers=headers)

        if response_players.status_code == 200:
            players = response_players.json()
            df_players = self.get_bestPlayers(players)
        else:
            None

        # Graph
        response_graph = requests.get(
            f'https://api.sofascore.com/api/v1/event/{code_match}/graph', headers=headers)

        if response_graph.status_code == 200:
            graph = response_graph.json()
            df_graph = self.get_graph(graph)
        else:
            None

        # Transpile into a Series:
        df = pd.Series(dtype=object)
        df['Event'] = df_event
        df['Shotmap'] = df_shots
        df['Best_Players'] = df_players
        df['Graph'] = df_graph

        return df


# def get_
