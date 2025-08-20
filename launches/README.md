# Binder Traffic data

This folder contains data about traffic for the service running at `mybinder.org`.

The Python script at `scrape_binder_analytics.py` can be run as a Jupyter Notebook or as a Python script like so:

```shell
$ python scrape_binder_analytics.py --days N_DAYS
```

Where N_DAYS is the number of days in history to pull data.

This script is called by the `release.yml` GitHub workflow to publish this data to a single Parquet file for easy reading and analysis.
