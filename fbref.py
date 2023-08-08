import numpy as np
import pandas as pd
import ScraperFC as sfc
import traceback

# class where I will save all the data


class BotScrap:

    def reset_multi_index(self, dataset):
        for i in range(1, len(dataset)):
            try:
                dataset[i].columns = dataset[i].columns.droplevel(0)
                dataset[i] = dataset[i].dropna()
                dataset[i].reset_index(drop=True, inplace=True)
                dataset[i].rename(columns={'': 'Player ID'})
            except IndexError:
                print("There's a missed index")
                return None

        return dataset

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

        data = {
            'home': '',
            'away': '',
            'shots': ''
        }

        # Adding values more easy to use
        home_stats = lg_table['Home Player Stats'][0].values[0]
        away_stats = lg_table['Away Player Stats'][0].values[0]

        # Resetting multi-Index
        self.reset_multi_index(home_stats)
        self.reset_multi_index(away_stats)

        # Transferring data to 'data'
        data['home'] = home_stats
        data['away'] = away_stats

        return data


# Try errors

# dataMap = BotScrap()
# dataMap.get_match(
#     'https://fbref.com/en/matches/2e4383ca/Arsenal-Leeds-United-April-1-2023-Premier-League')
