import pandas as pd
import os

# Read in the raw data
print("Loading and munging data...")
path = os.path.dirname(__file__)
data = pd.read_csv(os.path.join(path, 'data', 'ga_raw.csv'), skiprows=5)[['Page', 'Pageviews', 'Unique Pageviews']]
data = data.dropna(subset=['Page'])

# Remove trailing date information
day_index = data.query('Page == "Day Index"').index
data = data.loc[:day_index[0]].iloc[:-1]
data = data.query('Page != "/"')

# Separate org/repo/ref
info = {'org': [], 'repo': [], 'ref': [], 'index': []}
for ii, vals in data['Page'].map(lambda a: a.strip('/v2/gh/').split('?')[0].split('/')).items():
    if len(vals) != 3:
        continue
    org, repo, ref = vals
    info['org'].append(org)
    info['repo'].append(repo)
    info['ref'].append(ref)
    info['index'].append(ii)

data_new = pd.DataFrame(info).set_index('index')

# Merge into a new df
data = pd.merge(data, data_new, left_index=True, right_index=True).drop('Page', axis=1)
data = data.rename(columns={"Pageviews": "pageviews", "Unique Pageviews": "unique_pageviews"})
data = data[['org', 'repo', 'ref', 'pageviews', 'unique_pageviews']]

# Save to disk
print('Saving...')
data.to_csv(os.path.join(path, 'data', 'ga_clean.csv'))