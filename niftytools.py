import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from matplotlib.colors import LinearSegmentedColormap
import time
import pdb
import os
from newsapi import NewsApiClient

class Nifty50Tracker:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        self._initialize_session()

    def _initialize_session(self):
        try:
            self.session.get('https://www.nseindia.com/', timeout=5)
        except Exception as e:
            print(f"Session init error: {e}")
    
    def fetch(self,url):
        while True:
            try:
                response = self.session.get(url,
                    timeout=10
                )
                response.raise_for_status()
                yield response.json()
            except Exception as e:
                print(f"Data fetch error: {e}")
                yield None
            time.sleep(15)
    def fii_dii(self):
        url = 'https://www.nseindia.com/api/fiidiiTradeReact'
        return self.fetch(url)
    def data_generator(self):
        url = 'https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050'
        return self.fetch(url)


    def index_data(self):
        gen = self.data_generator()
        return next(gen)

    def fiidii_flow(self):
        fiidii = self.fii_dii()
        return next(fiidii)


if __name__ == "__main__":
    res = Nifty50Tracker()
    res1 = res.fiidii_flow()
    print(res1)
    res1 = res.index_data()
    print(res1)
