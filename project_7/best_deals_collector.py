import joblib
import numpy as np
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import re
from statistics import mean

browser = webdriver.Chrome()
url = f'https://www.nettiauto.com'
browser.get(url)
all_makes = browser.find_elements(By.CSS_SELECTOR, '#srch_id_make')[0].text
browser.close()
all_makes = all_makes.replace('\n', ', ').replace('  ', '').split(', ')
all_makes = all_makes[11:-1]

data_dict = {}
data = pd.DataFrame(data_dict)
browser = webdriver.Chrome()
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

url = f'https://www.nettiauto.com/en/vaihtoautot?new=H&sortCol=price&ord=ASC&id_country[]=73'
browser.get(url)
number_of_pages = browser.find_elements(By.CSS_SELECTOR,
                                        '#pagingData > div > span.navigation_link > a.pageNavigation.dot_block')
number_of_pages = int(number_of_pages[0].text)
print(f'Initiating web-scraping of {number_of_pages}...')
browser.close()

for page in range(1, number_of_pages + 1):

    browser = webdriver.Chrome()
    options.add_argument("--start-maximized")

    url = f'https://www.nettiauto.com/vaihtoautot?page={page}'
    browser.get(url)
    make_list = browser.find_elements(By.CSS_SELECTOR, '[class="make_model_link"]')
    desc_list = browser.find_elements(By.CSS_SELECTOR, '[class="checkLnesFlat for_rent_one_line"]')
    key_char_list = browser.find_elements(By.CSS_SELECTOR, '[class="vehicle_other_info clearfix_nett"]')
    places_list = browser.find_elements(By.CSS_SELECTOR, '[class="gray_text"]')
    sellers_list = browser.find_elements(By.CSS_SELECTOR, '[class="no_wrap gray_text"]')
    price_list = browser.find_elements(By.CSS_SELECTOR, '[class="price_block"]')
    ids_list = browser.find_elements(By.CSS_SELECTOR, '[class="childVifUrl tricky_link"]')

    print(len(make_list), len(desc_list), len(key_char_list), len(places_list), len(sellers_list), len(price_list),
          len(ids_list))

    if len(make_list) == len(desc_list) == len(key_char_list) == len(places_list) == len(sellers_list) == len(
            price_list) == len(ids_list):
        makes = []
        descs = []
        key_chars = []
        places = []
        sellers = []
        prices = []
        ids = []

        for val in range(len(make_list)):
            makes.append(make_list[val].text)
            descs.append(desc_list[val].text)
            key_chars.append(key_char_list[val].text.replace('\n', ' | '))
            places.append(places_list[val].text)
            sellers.append(sellers_list[val].text)
            prices.append(price_list[val].text)
            ids.append(ids_list[val].get_attribute('href'))

    else:
        print('Error! Number of values in columns is different!')
        continue

    data_dict['make'] = makes
    data_dict['desc'] = descs
    data_dict['key_char'] = key_chars
    data_dict['town'] = places
    data_dict['seller'] = sellers
    data_dict['price'] = prices
    data_dict['id'] = ids

    data_new = pd.DataFrame(data_dict)
    data = pd.concat([data, data_new])
    data.to_csv('/Users/egor/Documents/data_science_course/project_7/data/data_new24.csv')
    print(f'Page {page} out of {number_of_pages} completed')
    browser.close()

data = pd.read_csv('/Users/egor/Documents/data_science_course/project_7/data/data_new24.csv')


def get_engine_volume(sample_string):
    pattern = r'\((.*?)\)'
    values_in_brackets = re.findall(pattern, sample_string)
    # for some cars engine volume is not indicated (for example electric cars)
    # i'll tag them with -1
    if len(values_in_brackets) == 0:
        return -1
    elif len(values_in_brackets) == 1:
        return values_in_brackets[0]
    # in case if string has several values in brackets
    else:
        return 'Error'


# applying function to "make" feature and creating "engine_vol" column
data['engine_vol'] = data['make'].apply(lambda x: get_engine_volume(x))


def extract_make_name(sample_string, make_list):
    for make in make_list:
        if make in sample_string:
            return make
    return None  # Return None if no matching make is found


data['car_make'] = data['make'].apply(lambda x: extract_make_name(x, all_makes))


def extract_model_name(sample_string, make_list):
    pattern = r'\s*\(\d+\.\d+\)'
    values_in_brackets = re.findall(pattern, sample_string)
    if len(values_in_brackets) == 1:
        sample_string = sample_string.replace(values_in_brackets[0], '')
    for make in make_list:
        if make in sample_string:
            sample_string = sample_string.replace(make, '').strip()
    return sample_string  # Return None if no matching make is found


data['model'] = data['make'].apply(lambda x: extract_model_name(x, all_makes))
data['make_model'] = data['car_make'] + ' ' + data['model']
data['desc'] = data['desc'].astype(str)
data['roadworthy'] = data['desc'].apply(lambda x: 0 if 'Ei tieliikennekelpoinen' in x else 1)
awd_types = ['awd', '4wd', '4x4', 'xdrive', '4matic', 'quattro', 'all-wheel drive', 'all wheel', 'super select']


def is_awd(sample_string, awd_types):
    sample_string = sample_string.lower()
    for type in awd_types:
        if type in sample_string:
            return 1
    return 0  # Return 0 if no matching type is found


data['awd'] = data['desc'].apply(lambda x: is_awd(x, awd_types))
categories = {
    'sedan': 'Sedan',
    'avant': 'Universal',
    'van': 'Minivan',
    'combi': 'Universal',
    'tourer': 'Universal',
    'wagon': 'Universal',
    'touring': 'Universal',
    'farmari': 'Universal',
    'sportback': 'Hatchback',
    'coupe': 'Coupe',
    'coupé': 'Coupe',
    'hatchback': 'Hatchback',
    'cabriolet': 'Cabriolet',
    'convertible': 'Cabriolet',
    'cabrio': 'Cabriolet',
    'pickup': 'Pickup',
    'spaceback': 'Hatchback',
    'crossover': 'Jeep',
    'estate': 'Universal',
    'sportswagon': 'Universal',
    'shooting': 'Universal',
    'targa': 'Coupe',
    'hardtop': 'Coupe',
    'saloon': 'Sedan',
    'roadster': 'Coupe',
    'spider': 'Coupe',
    'turismo': 'Hatchback',
    'mpv': 'Minivan',
    'fastback': 'Coupe',
    'suv': 'Jeep'
}


def get_category(sample_string, categories):
    sample_string = sample_string.lower().split(' ')
    for word in sample_string:
        if word in categories:
            return categories.get(word)


data['category'] = data['desc'].apply(lambda x: get_category(x, categories))
doors_count = {
    '5-ovinen,': '4/5',
    '5-door': '4/5',
    '5-ovinen': '4/5',
    '#5-ovinen': '4/5',
    '2ov': '2/3',
    '2-door': '2/3',
    '3-door': '2/3',
    '3ov': '2/3',
    '2-ov': '2/3',
    '4ov': '4/5',
    '4-ov': '4/5',
    '4door': '4/5',
    '5-ov,': '4/5',
    'kaksiovinen': '2/3',
    '2d': '2/3',
    '3d': '2/3',
    '4d': '4/5',
    '5d': '4/5'
}


def get_doors(sample_string, doors_count):
    sample_string = sample_string.lower().split(' ')
    for word in sample_string:
        if word in doors_count:
            return doors_count.get(word)


data['doors'] = data['desc'].apply(lambda x: get_doors(x, doors_count))

def extract_horsepower(string):
    string = string.lower()
    pattern = r'(\d+)\s*hv'
    match = re.search(pattern, string)
    if match:
        return int(match.group(1))


data['hp'] = data['desc'].apply(lambda x: extract_horsepower(x))


def extract_power(string):
    string = string.lower()
    pattern = r'(\d+)\s*kw(?!h)'
    match = re.search(pattern, string)
    if match:
        return int(match.group(1))


data['power'] = data['desc'].apply(lambda x: extract_power(x))


def extract_capacity(string):
    string = string.lower()
    pattern = r'(\d+)\s*kwh'
    match = re.search(pattern, string)
    if match:
        return int(match.group(1))


data['capacity'] = data['desc'].apply(lambda x: extract_capacity(x))


def organize_key_char(sample_string):
    sample_list = sample_string.split('|')
    for i in range(len(sample_list)):
        sample_list[i] = sample_list[i].strip()
    return sample_list


data['key_char'] = data['key_char'].apply(lambda x: organize_key_char(x))
fuel_type = ['Bensiini', 'Diesel', 'Hybridi (bensiini/sähkö)', 'Hybridi (diesel/sähkö)', 'Sähkö', 'Kaasu',
             'E85/bensiini', 'Ei saatavilla']
gearbox_type = ['Automaatti', 'Manuaali']

data['year'] = data['key_char'].apply(lambda x: x[0].strip())
data['year'] = data['year'].astype(int)
curr_time = datetime.datetime.now()
data['age'] = data['year'].apply(lambda x: curr_time.year - x)
data['age'] = data['age'].apply(lambda x: 0 if x == -1 else x)


def extract_mileage(sample_list):
    if 'km' in sample_list[1]:
        return sample_list[1].strip()[:-2].replace(' ', '')
    else:
        '-1'


data['mileage'] = data['key_char'].apply(lambda x: extract_mileage(x))
fuel_type = ['Bensiini', 'Diesel', 'Hybridi (bensiini/sähkö)', 'Hybridi (diesel/sähkö)', 'Sähkö', 'Kaasu',
             'E85/bensiini', 'Ei saatavilla']
gearbox_type = ['Automaatti', 'Manuaali']


def get_type(sample_list, types):
    for type in types:
        if type in sample_list:
            return type


data['fuel_type'] = data['key_char'].apply(lambda x: get_type(x, fuel_type))
data['gearbox_type'] = data['key_char'].apply(lambda x: get_type(x, gearbox_type))
car_dealers = ['J. Rinta-Jouppi', 'Autokeskus Oy', 'Autolle.com', 'Suursavonauto.fi', 'Wetteri', 'AC Auto-Center',
               'Rinta-Joupin Autoliike', 'Hedin Automotive', 'LänsiAuto', 'Kamux', 'K-auto', 'Saka Finland Oy',
               'Secto Vaihtoautot', 'Autotalo', 'Auto-Suni', 'Nelipyörä', 'Ford Store', 'Hedin Automotive', 'Automaa',
               'Bavaria', 'Toyota', 'Omax', 'ALD Carmarket', 'Delta Auto', 'Pörhö', 'Veho', 'Bilar99e', 'Autosalpa',
               'Vaihtokaara', 'Auto-Kilta', 'Autodeal', 'Keskusautohalli Oy', 'Helkama-Auto', 'MB-mobile', 'XBIL',
               'Autoverkkokauppa.fi', 'Kupen auto', 'KymppiPlus', 'Menoauto', 'Vaihtoautomaa', 'ALD Carmarket',
               'MS-auto', 'Euro Auto', 'Tojo-Auto', 'Porsche Center', 'Levorannan Autoliike', 'SCC - Sports Car Center',
               'Ajanvaunu Oy', 'Auto-Kehä Oy', 'Auto-Eekoo']


def group_seller(sample_string, car_dealers):
    sample_string = sample_string.lower()
    for dealer in list(map(str.lower, car_dealers)):
        x = sample_string.replace(dealer, '')
        if (len(x) != len(sample_string)):
            return dealer.lower()
    return sample_string


data['car_seller'] = data['seller'].apply(lambda x: group_seller(x, car_dealers))
data['car_seller'] = data['car_seller'].astype(str)
data['car_seller'] = data['car_seller'].apply(lambda x: x.lower())
data['price'] = data['price'].apply(lambda x: x.split('\n'))
data['car_price'] = data['price'].apply(lambda x: x[0].replace('€', '').replace(' ', ''))

def extract_deal(sample_list):
    try:
        if '(' in sample_list[1]:
            return sample_list[1].replace('(', '').replace(')', '').strip()
        else:
            return None
    except IndexError:
        return None


data['deal'] = data['price'].apply(lambda x: extract_deal(x))
data = data.drop(columns=['Unnamed: 0', 'make', 'desc', 'key_char', 'price', 'seller'])
data = data.dropna(subset=['mileage', 'make_model'])
to_be_deleted = set()

no_make_model = data[(data['model'] == 'Muu malli') | (data['car_make'] == 'Muu merkki')].index
to_be_deleted.update(no_make_model)
to_be_deleted.update(data[data['roadworthy'] == 0].index)
nan_gearbox = data[data['gearbox_type'].isna()]
automaatti_index = nan_gearbox[(nan_gearbox['fuel_type'] == 'Hybridi (bensiini/sähkö)') | (
            nan_gearbox['fuel_type'] == 'Hybridi (diesel/sähkö)') | (nan_gearbox['fuel_type'] == 'Sähkö')].index
data.loc[automaatti_index, 'gearbox_type'] = 'Automaatti'
data_automaatti_index = data[
    (data['fuel_type'] == 'Hybridi (bensiini/sähkö)') | (data['fuel_type'] == 'Hybridi (diesel/sähkö)') | (
                data['fuel_type'] == 'Sähkö')].index
data.loc[data_automaatti_index, 'gearbox_type'] = 'Automaatti'
to_be_deleted.update(data[data['gearbox_type'].isna()].index)
tax_free_cars = data[(data['deal'] == 'Tax free') | (data['deal'] == 'Tax free, sis. ALV') | (
            data['deal'] == 'Tax free, ALV väh.kelp.')].index
to_be_deleted.update(tax_free_cars)
to_be_deleted.update(data[data['car_price'] == 'Eihinnoiteltu'].index)
data = data.drop(index=to_be_deleted)
data = data.drop(columns=['roadworthy', 'deal'])
data['car_price'] = data['car_price'].astype(int)
data['make_model'] = data['make_model'].apply(lambda x: x.lower())

cars = pd.read_csv('/Users/egor/Documents/data_science_course/project_7/data/characteristics.csv', index_col=0)
cars = cars[['manufacturer', 'model', 'category', 'year', 'gear_box_type', 'doors']]
cars['make_model'] = cars['manufacturer'] + ' ' + cars['model']
cars['make_model'] = cars['make_model'].astype(str).apply(lambda x: x.lower())
cars['gear_box_type'] = cars['gear_box_type'].apply(
    lambda x: {'Automatic': 'Automaatti', 'Tiptronic': 'Automaatti', 'Manual': 'Manuaali',
               'Variator': 'Automaatti'}.get(x)
)
cars = cars.drop(columns=['manufacturer', 'model'])
cars = cars.dropna()

cars_hp = pd.read_csv('/Users/egor/Documents/data_science_course/project_7/data/autoscout24-germany-dataset.csv')
cars_hp['make_model'] = cars_hp['make'] + ' ' + cars_hp['model']
cars_hp['make_model'] = cars_hp['make_model'].astype(str).apply(lambda x: x.lower())
cars_hp = cars_hp.drop(columns=['make', 'model', 'mileage', 'offerType', 'price'])

fuel_dict = {
    'Gasoline': 'Bensiini',
    'Electric/Gasoline': 'Hybridi (bensiini/sähkö)',
    'Electric': 'Sähkö',
    'LPG': 'Kaasu',
    'CNG': 'Kaasu',
    'Electric/Diesel': 'Hybridi (diesel/sähkö)',
    'Others': np.nan,
    '-/- (Fuel)': np.nan,
    'Ethanol': 'E85/bensiini',
    'Hydrogen': np.nan
}

cars_hp['fuel'] = cars_hp['fuel'].apply(lambda x: fuel_dict.get(x, x))

gear_dict = {
    'Manual': 'Manuaali',
    'Automatic': 'Automaatti',
    'Semi-automatic': np.nan
}

cars_hp['gear'] = cars_hp['gear'].apply(lambda x: gear_dict.get(x, x))
cars_hp = cars_hp.dropna()
cars_hp_grouped_year = cars_hp.groupby(by=['make_model', 'year', 'gear', 'fuel'], as_index=False)['hp'].agg(
    pd.Series.mode)
cars_hp_grouped = cars_hp.groupby(by=['make_model', 'gear', 'fuel'], as_index=False)['hp'].agg(pd.Series.mode)
# %%
data_grouped_year = data.groupby(by=['make_model', 'car_make', 'year', 'gearbox_type', 'fuel_type'], as_index=False)[
    'engine_vol'].count()
data_grouped = data.groupby(by=['make_model', 'gearbox_type', 'fuel_type'], as_index=False)['engine_vol'].count()
# %%
data_joined_year = pd.merge(
    data_grouped_year,
    cars_hp_grouped_year,
    how='left',
    left_on=['make_model', 'year', 'fuel_type', 'gearbox_type'],
    right_on=['make_model', 'year', 'fuel', 'gear']
)

data_joined = pd.merge(
    data_joined_year,
    cars_hp_grouped,
    how='left',
    left_on=['make_model', 'fuel_type', 'gearbox_type'],
    right_on=['make_model', 'fuel', 'gear']
)

data_joined['hp'] = np.where(data_joined['hp_x'].notna(), data_joined['hp_x'], data_joined['hp_y'])
data_joined['hp'] = data_joined['hp'].apply(lambda x: x if isinstance(x, float) else mean(x))
data_joined = data_joined.drop(columns=['engine_vol', 'gear_x', 'gear_y', 'fuel_x', 'fuel_y', 'hp_x', 'hp_y'])

data_joined_make = data_joined.groupby(by='car_make')['hp'].mean()

data_joined = pd.merge(
    data_joined,
    data_joined_make,
    how='left',
    on='car_make'
)

data_joined['hp'] = np.where(data_joined['hp_x'].notna(), data_joined['hp_x'], data_joined['hp_y'])
data_joined = data_joined.drop(columns=['car_make', 'hp_x', 'hp_y'])

data = pd.merge(
    data,
    data_joined,
    how='left',
    on=['make_model', 'year', 'gearbox_type', 'fuel_type']
)
data['hp_x'] = np.where(data['hp_x'].notna(), data['hp_x'], data['power'] / 0.73549875)
data['hp_x'] = np.where(data['hp_x'] > 59, data['hp_x'], data['hp_y'])
data = data.drop(columns=['hp_y', 'power'])
data = data.rename(columns={'hp_x': 'hp'})

hp_grouped = data.groupby(by=['engine_vol', 'year', 'fuel_type', 'gearbox_type'], as_index=False)['hp'].mean()
hp_grouped['hp'] = hp_grouped['hp'].apply(lambda x: x if isinstance(x, float) else np.nan if len(x) == 0 else mean(x))

data = pd.merge(
    data,
    hp_grouped,
    how='left',
    on=['engine_vol', 'year', 'fuel_type', 'gearbox_type']
)
data['hp_x'] = np.where(data['hp_x'].notna(), data['hp_x'], data['hp_y'])
data = data.drop(columns=['hp_y'])
data = data.rename(columns={'hp_x': 'hp'})

hp_grouped_no_year = data.groupby(by=['engine_vol', 'fuel_type'], as_index=False)['hp'].mean()

data = pd.merge(
    data,
    hp_grouped_no_year,
    how='left',
    on=['engine_vol', 'fuel_type']
)
data['hp_x'] = np.where(data['hp_x'].notna(), data['hp_x'], data['hp_y'])
data = data.drop(columns=['hp_y'])
data = data.rename(columns={'hp_x': 'hp'})

data['hp'] = data['hp'].fillna(data['hp'].mean())

cars_categories = cars.groupby(by=['make_model'], as_index=False)[['doors', 'category']].agg(pd.Series.mode)

cars_categories['doors'] = cars_categories['doors'].apply(
    lambda x: x.replace(' ', '') if isinstance(x, str) else x.tolist()[0].replace(' ', '')
)

cars_categories['category'] = cars_categories['category'].apply(lambda x: x if isinstance(x, str) else x.tolist()[0])

data = pd.merge(
    data,
    cars_categories,
    how='left',
    on='make_model'
)

data['category_x'] = np.where(data['category_x'].notna(), data['category_x'], data['category_y'])

data['doors_x'] = np.where(data['doors_x'].notna(), data['doors_x'], data['doors_y'])

data = data.drop(columns=['category_y', 'doors_y'])
data = data.rename(columns={'category_x': 'category', 'doors_x': 'doors'})

category_door = cars.groupby(by=['category'], as_index=False)['doors'].agg(pd.Series.mode)
category_door['doors'] = category_door['doors'].apply(
    lambda x: x.replace(' ', ''))

door_category = cars.groupby(by=['doors'], as_index=False)['category'].agg(pd.Series.mode)
door_category['doors'] = door_category['doors'].apply(
    lambda x: x.replace(' ', ''))

data = pd.merge(
    data,
    category_door,
    how='left',
    on='category'
)

data['doors_x'] = np.where(data['doors_x'].notna(), data['doors_x'], data['doors_y'])

data = data.drop(columns=['doors_y'])
data = data.rename(columns={'doors_x': 'doors'})

data = pd.merge(
    data,
    door_category,
    how='left',
    on='doors'
)

data['category_x'] = np.where(data['category_x'].notna(), data['category_x'], data['category_y'])

data = data.drop(columns=['category_y'])
data = data.rename(columns={'category_x': 'category'})

data = pd.merge(
    data,
    category_door,
    how='left',
    on='category'
)

data['doors_x'] = np.where(data['doors_x'].notna(), data['doors_x'], data['doors_y'])

data = data.drop(columns=['doors_y'])
data = data.rename(columns={'doors_x': 'doors'})
# %%
data['engine_vol'] = data['engine_vol'].astype(float)
# %%
main_data = pd.read_csv('/Users/egor/Documents/data_science_course/project_7/data/data_clean.csv', index_col=0)
car_companies = main_data[main_data['is_company'] == 1].groupby(by='car_seller')['town'].count().index
main_data = main_data[[
    'engine_vol', 'make_model', 'awd', 'category',
    'doors', 'hp', 'capacity', 'fuel_type',
    'price_category', 'gearbox_type']]
md_grouped = main_data.groupby(by=['make_model', 'fuel_type', 'engine_vol'], as_index=False).agg(pd.Series.mode)

data = pd.merge(
    data,
    md_grouped,
    how='left',
    on=['make_model', 'engine_vol', 'fuel_type']
)

data['awd_x'] = np.where(data['awd_x'].notna(), data['awd_x'], data['awd_y'])
data['category_x'] = np.where(data['category_x'].notna(), data['category_x'], data['category_y'])
data['doors_x'] = np.where(data['doors_x'].notna(), data['doors_x'], data['doors_y'])
data['hp_x'] = np.where(data['hp_x'].notna(), data['hp_x'], data['hp_y'])
data['capacity_x'] = np.where(data['capacity_x'].notna(), data['capacity_x'], data['capacity_y'])
data['gearbox_type_x'] = np.where(data['gearbox_type_x'].notna(), data['gearbox_type_x'], data['gearbox_type_y'])

data = data.drop(columns=['awd_y', 'doors_y', 'category_y', 'hp_y', 'capacity_y', 'gearbox_type_y'])
data = data.rename(columns={
    'doors_x': 'doors',
    'awd_x': 'awd',
    'category_x': 'category',
    'hp_x': 'hp',
    'capacity_x': 'capacity',
    'gearbox_type_x': 'gearbox_type'
})


def get_hp_cat(hp_value):
    if hp_value < 100:
        return 'low (less 100)'
    elif hp_value < 170:
        return 'medium (less 170)'
    elif hp_value < 270:
        return 'high (less 270)'
    else:
        return 'max (more 270)'


data['hp_cat'] = data['hp'].apply(get_hp_cat)
company_tags = [' oy', 'tmi ', '.fi', 't:mi ', ' ky', '.com', ' ab', 'oy ', ' oü']


def is_company(sample_string, car_companies, company_tags):
    if sample_string in car_companies:
        return 1
    else:
        for tag in company_tags:
            if tag in sample_string:
                return 1
        return 0


data['is_company'] = data['car_seller'].apply(lambda x: is_company(x, car_companies, company_tags))

population = pd.read_excel(
    '/Users/egor/Documents/data_science_course/project_7/data/001_11lj_2023m08_20231024-194749.xlsx')
population = population.dropna(
    subset=['Unnamed: 1', 'Unnamed: 2']).reset_index(drop=True).drop(
    columns='Preliminary population structure by Month, Area and Information').rename(
    columns={'Unnamed: 1': 'town', 'Unnamed: 2': 'population'})

population['population'] = population['population'].astype(int)

data = pd.merge(
    data,
    population,
    how='left',
    on='town'
)

data['population'] = data['population'].fillna(data['population'].median())


def get_city_cat(population):
    if population <= 6000:
        return 'Very small (0-6k)'
    elif population <= 20000:
        return 'Small (6k-20k)'
    elif population <= 50000:
        return 'Medium (20-50k)'
    elif population <= 100000:
        return 'Big (50-100k)'
    else:
        return 'Biggest (more 100k)'


data['town_category'] = data['population'].apply(get_city_cat)

for i in data.columns[data.isna().any()]:
    data[i] = data[i].fillna(data[i].mode()[0])

data['mileage'] = data['mileage'].astype(int)
data['awd'] = data['awd'].astype(int)
data['hp'] = data['hp'].astype(int)
data['capacity'] = data['capacity'].astype(int)
data['manual_gearbox'] = data['gearbox_type'].apply(lambda x: 1 if x == 'Manuaali' else 0)
data = data.drop(columns=['year', 'gearbox_type'])

data['category'] = data['category'].apply(lambda x: x[0] if type(x) is np.ndarray else x)
data['doors'] = data['doors'].apply(lambda x: x[0] if type(x) is np.ndarray else x)

data = data.dropna()
data = data.drop_duplicates()
data.reset_index(drop=True)

data.to_csv('/Users/egor/Documents/data_science_course/project_7/data/data_new24_clean.csv')

ohe_mdl = joblib.load('/Users/egor/Documents/data_science_course/project_7/models/ohe_mdl.joblib')
scaler = joblib.load('/Users/egor/Documents/data_science_course/project_7/models/scaler.joblib')
xgb_reg_gs = joblib.load('/Users/egor/Documents/data_science_course/project_7/models/xgb_reg_gs.joblib')

data_mdl = data[[
    'make_model',
    'engine_vol',
    'awd',
    'category',
    'hp',
    'capacity',
    'age',
    'mileage',
    'fuel_type',
    'manual_gearbox',
    'hp_cat',
    'price_category',
    'town_category',
    'is_company',
    'car_price'
]].reset_index(drop=True)

numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
data_mdl_num_cols = list(data_mdl.select_dtypes(include=numerics).columns)
data_mdl_cat_cols = list(data_mdl.select_dtypes(exclude=numerics).columns)

data_mdl_ohe = ohe_mdl.transform(data_mdl[data_mdl_cat_cols])
data_mdl_ohe = pd.DataFrame(data_mdl_ohe, columns=ohe_mdl.get_feature_names_out(input_features=data_mdl_cat_cols))

data_mdl = data_mdl.drop(list(data_mdl_cat_cols), axis=1)
data_mdl = pd.concat([data_mdl, data_mdl_ohe], axis=1)
data_mdl.shape

X = data_mdl.drop(columns=['car_price'])
y = data_mdl['car_price']

data_mdl_num_cols.remove('car_price')
X[data_mdl_num_cols] = scaler.transform(X[data_mdl_num_cols])

cols_when_model_builds = xgb_reg_gs.get_booster().feature_names
X = X[cols_when_model_builds]

y_pred = xgb_reg_gs.predict(X)
data['y_pred'] = y_pred
data['price_diff'] = data['y_pred'] - data['car_price']
data['profit_%'] = data['price_diff'] / data['car_price'] * 100
result = data[(data['price_diff'] > 1000) & (data['age'] < 15)]
result = result[['make_model', 'id', 'car_price', 'y_pred', 'profit_%']]
result = result.transpose()
result.to_json('/Users/egor/Documents/data_science_course/project_7/data/result.json')
