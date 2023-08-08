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
            'home': [],
            'away': [],
            'shots': []
        }

        # Fixing Multi-Index

        home_stats = lg_table['Home Player Stats'][0].values[0]
        away_stats = lg_table['Away Player Stats'][0].values[0]

        for i in range(1, min(len(home_stats), len(away_stats))):

            try:
                # Eliminating the Multi-Index

                # Home-Stats
                home_stats[i].columns = home_stats[i].columns.droplevel(0)
                home_stats[i] = home_stats[i].dropna()
                home_stats[i].reset_index(drop=True, inplace=True)

                # Away-Stats
                away_stats[i].columns = away_stats[i].columns.droplevel(0)
                away_stats[i] = away_stats[i].dropna()
                away_stats[i].reset_index(drop=True, inplace=True)

                # Dropping index
                data['home'].append(home_stats[i])
                data['away'].append(away_stats[i])

            except IndexError:
                print("There's a missed index")
                return None

        return data


# Try errors

# dataMap = BotScrap()
# dataMap.get_match(
#     'https://fbref.com/en/matches/2e4383ca/Arsenal-Leeds-United-April-1-2023-Premier-League')
