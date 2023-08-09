import numpy as np
import pandas as pd
import ScraperFC as sfc
from bs4 import BeautifulSoup
import traceback

# class where I will save all the data


class BotScrap:

    def reset_multi_index(self, dataset, rename=True, start_index=0, drop=True):

        for i in range(start_index, len(dataset)):
            try:
                dataset[i].columns = dataset[i].columns.droplevel(0)
                if drop:
                    dataset[i] = dataset[i].dropna()
                dataset[i].reset_index(drop=True, inplace=True)

                # Assign 'Player ID'
                if rename:
                    dataset[i].rename(columns={'': 'Player ID'}, inplace=True)
            except IndexError:
                print("There's a missed index")
                return None

        return dataset

    ####################
    # This get_shots() code belongs to ScraperFC

    def get_shots(self, url, home=None, away=None):
        # Get data from match
        scraper = sfc.FBRef()
        response = scraper.requests_get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Scrap shots
        both_shots = soup.find_all('table', {'id': 'shots_all'})

        # Both
        if len(both_shots) == 1:
            both_shots = pd.read_html(str(both_shots[0]))[0]
            both_shots = both_shots[~both_shots.isna().all(axis=1)]

        else:
            both_shots: None

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

        surted_data = pd.Series(dtype=object)

        surted_data['Shots'] = pd.Series(
            {'Both': both_shots, 'Home': home_shots, 'Away': away_shots, }).to_frame().T

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
        shots_stats = self.get_shots(
            url, lg_table['Home Team ID'][0], lg_table['Away Team ID'][0])
        shots_stats = shots_stats[0].values[0]

        # Resetting multi-Index
        self.reset_multi_index(home_stats, start_index=1)
        self.reset_multi_index(away_stats, start_index=1)
        self.reset_multi_index(shots_stats, rename=False, drop=False)

        ############################################
        # Grouping the data
        df = pd.Series(dtype=object)
        df['Match'] = pd.DataFrame(lg_table)
        df['Home'] = pd.DataFrame(home_stats)
        df['Away'] = pd.DataFrame(away_stats)
        df['Shots'] = pd.DataFrame(shots_stats)

        return df


# Try errors

# dataMap = BotScrap()
# dataMap.get_match(
#     'https://fbref.com/en/matches/2e4383ca/Arsenal-Leeds-United-April-1-2023-Premier-League')
