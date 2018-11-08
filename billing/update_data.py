import subprocess
import pandas as pd
from glob import glob
import json
import os.path as op

this_dir = op.dirname(__file__)

def download_data():
    print('Updating data...')
    data = subprocess.check_output(['gsutil', 'ls', 'gs://binder-billing/']).decode()

    # Pull date information
    data = data.split()
    dates = [ii.split('report-')[-1].replace('.csv', '') for ii in data]
    data = pd.DataFrame([data, dates], index=['path', 'date']).T
    data.loc[:, 'date'] = pd.to_datetime(data['date'])

    # Select files we want to update with
    proc_data = pd.read_json(op.join(this_dir, 'data', 'proc', 'data.json'), orient='split')
    proc_data.loc[:, 'date'] = pd.to_datetime(proc_data['date'])
    date_start = pd.to_datetime(proc_data['date'].unique()[-2])  # Overlap by a day to make sure we don't miss data
    print('...with {} days'.format((pd.datetime.today() - date_start).days))
    date_start = '{:%Y/%m/%d}'.format(date_start)
    use_data = data.query('date >= @date_start')

    # Download the files
    for ipath in use_data['path'].values:
        billing = subprocess.check_output(['gsutil', 'cp', ipath, op.join(this_dir, 'data', 'raw')])

def munge_data():
    print('Munging data...')
    # Pull raw data into one dataframe
    files = glob(op.join(this_dir, 'data', 'raw', 'report*'))
    data = []
    for this_file in files:
        data.append(pd.read_csv(this_file))
    data = pd.concat(data)

    # Rename columns and only keep data (rows/cols) we want
    data.loc[:, 'Start Time'] = pd.to_datetime(data['Start Time'])
    data['date'] = data['Start Time'].map(lambda a: "{:%x}".format(a)).apply(pd.to_datetime)

    keep_cols =  {'Project ID': 'project_id',
                  'date': 'date',
                  'Cost': 'cost',
                  'Line Item': 'line_item',
                  'Description': 'description'}

    use_projects = ['binder-prod', 'binder-staging']
    data = data.rename(columns=keep_cols)[list(keep_cols.values())]
    data = data.query("project_id in @use_projects")

    # Pulling metadata
    data.loc[:, 'line_item'] = data['line_item'].str.replace('com.google.cloud/services/', '')
    data.loc[:, 'category'] = data['line_item'].map(lambda a: a.split('/')[0])
    data.loc[:, 'line_item'] = data['line_item'].map(lambda a: '/'.join(a.split('/')[1:]))

    # Save to JSON
    data.to_json(op.join(this_dir, "data", "proc", "data.json"), orient='split')

if __name__ == '__main__':
    download_data()
    munge_data()
    print('Done!')
