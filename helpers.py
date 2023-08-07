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

        return lg_table
