import random
from time import sleep

import requests, logging
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
class DataScrapper:

    def __init__(self, years=None):
        year_range = years if years is not None else range(2005, 2022) # move to default config (import from constants)
        self.urls = list()
        for year in year_range:
            self.urls.append(
                f'https://datosmacro.expansion.com/energia/precios-gasolina-diesel-calefaccion/espana?anio={year}')
    def __load_page_content(self, url):
        page = requests.get(url)
        year = url[-1:-4] # year is the last 4 chars from url
        soup = BeautifulSoup(page.text, 'lxml')
        self.table1 = soup.find('table', id='tb1_1313')
        if self.table1 is None:
            logging.error(f'Year {year} has a different DOM/HTML structure! Content not loaded')
        self.headers = []
        for i in self.table1.find_all('th'):
            title = i.text
            self.headers.append(title)
    def __clean_df(self, df):
        ## process df
        feat_type_map = {col: ('datetime64' if col == 'Fecha' else 'float64') for col in self.headers}
        df['Fecha'] = pd.to_datetime(df['Fecha'].astype(str), dayfirst=True)
        return df.astype(feat_type_map)
    def __create_df(self):
        mydata = pd.DataFrame(columns=self.headers)
        # Create a for loop to fill mydata
        for j in self.table1.find_all('tr')[1:]:
            row_data = j.find_all('td')
            row = [i.text for i in row_data]
            cleaned_row = [cell.replace('\xa0€', '').replace(",", ".") for cell in row]  # get only the price, in Euros
            length = len(mydata)
            if len(cleaned_row) == mydata.shape[1]:
                mydata.loc[length] = cleaned_row
        return self.__clean_df(mydata)
    def __call__(self):
        list_of_yearly_df = list()
        for url in self.urls:
            self.__load_page_content(url)
            list_of_yearly_df.append(self.__create_df())
            sleep(random.uniform(0.2, 2))
        return pd.concat(list_of_yearly_df)

#test = DataScrapper()
#test().to_csv('../../data/2005-2022.csv', index=False)
df = pd.read_csv('../../data/2005-2022.csv')
df.plot('Fecha', 'Diesel')
plt.show()
print()