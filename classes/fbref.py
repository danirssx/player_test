import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ScraperFC as sfc
from bs4 import BeautifulSoup
import traceback
import re

# class where I will save all the data


class FBRef:

    #########
    # METHODS

    # Filter only the positions that I need
    def contains_pos(self, cell_value, pos_list):
        if not pd.notna(cell_value):
            return False

        return any(pos in cell_value for pos in pos_list)

    # Plot the text in the matplotlib graph
    def text_plot(self, x, y, labels, color, distance=0.07):
        for x_val, y_val, name in zip(x, y, labels):
            plt.text(x_val + distance, y_val, name, fontsize=8,
                     animated=True, ha='left', color=color, alpha=0.8)

    # Reset Multi-Index
    def reset_multi_index(self, dataset, rename=True, start_index=0, drop=True, level=0, avoid=[-1]):

        for i in range(start_index, len(dataset)):
            if i not in avoid:
                try:
                    dataset[i].columns = dataset[i].columns.droplevel(level)
                    if drop:
                        dataset[i] = dataset[i].dropna()
                    dataset[i].reset_index(drop=True, inplace=True)

                    # Assign 'Player ID'
                    if rename:
                        dataset[i].rename(
                            columns={'': 'Player ID'}, inplace=True)
                except IndexError:
                    print("There's a missed index")
                    return None

        return dataset

    #########
    # convert the string into integers
    def extract_integers(self, text):
        integers = re.findall(r'\d+', str(text))
        return [int(i) for i in integers]

    ######
    # get Stats:

    def get_stats(self, stats_data):
        # # Scrap stats

        if len(stats_data) == 1:
            stats_data = pd.read_html(str(stats_data[0]))[0]
            stats_data = stats_data[~stats_data.isna().all(axis=1)]
        else:
            stats_data = None

        barata = stats_data.copy()

        # # Necessary provisional
        list_data = [stats_data, barata]
        self.reset_multi_index(list_data, rename=False, drop=False, level=1)

        # Invert names
        team_names = list_data[0].columns

        # Function
        data = {'home': [], 'away': []}
        index_names = ['Possession']

        for i in range(0, len(list_data[0]), 2):
            try:
                # Home data
                data['home'].append(list_data[0][team_names[0]][i])

                # away data
                data['away'].append(list_data[0][team_names[1]][i])

                if i != 0:
                    index_names.append(list_data[0][team_names[0]][i-1])
            except IndexError:
                print("There's a missed index")
                return None

        # Returning into a DataFrame
        df = pd.DataFrame(data, index=index_names).T

        # Reconvert the strings
        df = df.applymap(self.extract_integers)

        return df

    ######
    # get Stats Extra:

    def get_stats_extra(self, stats_data):
        # Scrap extra stats
        final_data = []

        if len(stats_data) == 1:
            for div in stats_data[0].find_all(lambda tag: tag.name == 'div' and not tag.attrs):
                # Structure the data inside
                text = div.get_text(strip=True)
                if text and len(text) < 25:
                    final_data.append(text)
        else:
            final_data = None

        data = {'home': [], 'away': []}
        index_names = []

        for i in range(0, len(final_data), 3):
            # home
            data['home'].append(int(final_data[i]))
            # away
            data['away'].append(int(final_data[i+2]))
            # index-names
            index_names.append(final_data[i+1])

        df = pd.DataFrame(data, index=index_names).T

        return df

    # This get_shots() code belongs to ScraperFC

    def get_general(self, url, home=None, away=None):
        # Get data from match
        scraper = sfc.FBRef()
        response = scraper.requests_get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # # Scrap stats
        # stats_data = soup.find_all('div', {'id': 'team_stats'})

        # Scrap shots
        both_shots = soup.find_all('table', {'id': 'shots_all'})

        # Both
        if len(both_shots) == 1:
            both_shots = pd.read_html(str(both_shots[0]))[0]
            both_shots = both_shots[~both_shots.isna().all(axis=1)]

        else:
            both_shots = None

        # Home
        if home != None:
            home_shots = soup.find_all('table', {'id': f'shots_{home}'})
            if len(home_shots) == 1:
                home_shots = pd.read_html(str(home_shots[0]))[0]
                home_shots = home_shots[~home_shots.isna().all(axis=1)]
            else:
                home_shots = None

        # Away
        if away != None:
            away_shots = soup.find_all('table', {'id': f'shots_{away}'})
            if len(away_shots) == 1:
                away_shots = pd.read_html(str(away_shots[0]))[0]
                away_shots = away_shots[~away_shots.isna().all(axis=1)]
            else:
                away_shots = None

        # Shots data
        surted_data = pd.Series(dtype=object)
        surted_data['Shots'] = pd.Series(
            {'Both': both_shots, 'Home': home_shots, 'Away': away_shots, }).to_frame().T

        # Stats data
        stats_data = soup.find_all('div', {'id': 'team_stats'})

        if len(stats_data) == 1:
            stats_data = self.get_stats(stats_data)
        else:
            stats_data = None

        # Extra
        stats_extra_data = soup.find_all('div', {'id': 'team_stats_extra'})

        if len(stats_extra_data) == 1:
            stats_extra_data = self.get_stats_extra(stats_extra_data)
        else:
            return None

        # Append the Stats
        surted_data['Stats'] = pd.Series(
            {'stats': stats_data, 'extra': stats_extra_data})

        return surted_data

    def get_match(self, url):
        scraper = sfc.FBRef()

        # Get data
        try:
            # Scrape the table
            lg_table = scraper.scrape_match(
                link=url)
        except:
            # Cath and print any exceptions. This allow us to still close the scraper below, even if an exception occurs
            traceback.print_exc()
        finally:
            # It's important to close the scraper when you're done with it. Otherwise, you'll have a bunch of webdrivers open and running
            scraper.close()

        ############################################################

        # Adding values more easy to use
        home_stats = lg_table['Home Player Stats'][0].values[0]
        away_stats = lg_table['Away Player Stats'][0].values[0]

        # Shots
        general_stats = self.get_general(
            url, lg_table['Home Team ID'][0], lg_table['Away Team ID'][0])
        shots_stats = general_stats['Shots'].values[0]

        # Resetting multi-Index
        self.reset_multi_index(home_stats, start_index=1, avoid=[3])
        self.reset_multi_index(away_stats, start_index=1, avoid=[3])
        self.reset_multi_index(shots_stats, rename=False, drop=False)

        ############################################
        # Index Names:
        index_teams = ['Lineups', 'Summary', 'GK', 'Passing',
                       'Pass Types', 'Defensive Actions', 'Possession', 'Miscellaneous']
        index_shots = ['Both', 'Home', 'Away']

        # Grouping the data
        df = pd.Series(dtype=object)
        df['Match'] = pd.DataFrame(lg_table)
        df['Home'] = pd.DataFrame(
            home_stats, index=index_teams, columns=['Home'])
        df['Away'] = pd.DataFrame(
            away_stats, index=index_teams, columns=['Away'])
        df['Shots'] = pd.DataFrame(
            shots_stats, index=index_shots, columns=['Shots'])
        df['Stats'] = pd.DataFrame(general_stats['Stats'], columns=['Stats'])

        return df

    def get_matches(self, data, serie):
        for team, link in zip(data['teams'], data['links']):
            match_stats = self.get_match(link)
            serie[team] = match_stats

        return serie


# Try errors

# dataMap = BotScrap()
# dataMap.get_match(
#     'https://fbref.com/en/matches/2e4383ca/Arsenal-Leeds-United-April-1-2023-Premier-League')
