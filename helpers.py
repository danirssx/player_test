import numpy as np
import pandas as pd
import ScraperFC as sfc
import traceback

# class where I will save all the data


class BotScrap:

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

        try:
            lg_table['Home Player Stats'][0].values[0][1].columns = lg_table['Home Player Stats'][0].values[0][1].columns.droplevel(
                0)
            lg_table['Home Player Stats'][0].values[0][1] = lg_table['Home Player Stats'][0].values[0][1].dropna()
            print(lg_table['Home Player Stats'][0].values[0][1])

        except IndexError:
            return None

        return lg_table


# Try errors

# dataMap = BotScrap()
# dataMap.get_match(
#     'https://fbref.com/en/matches/2e4383ca/Arsenal-Leeds-United-April-1-2023-Premier-League')
