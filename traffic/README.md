# Binder Traffic data

This folder contains data about traffic for the service running at `mybinder.org`.


## How to update the per repo and per URL data

1. Visit [Google Analytics](https://analytics.google.com/analytics/web/#/report/content-pages/a101904940w149250546p154152886/_u.dateOption=last30days&explorer-table.plotKeys=%5B%5D&explorer-table.rowCount=5000)
2. Check that the last 30 days of data are shown and that it is no more than 5000 rows
3. Export the data to a CSV
4. Adjust the file name used in `summarize-data.ipynb`
5. Run the `summarize-data.ipynb` notebook to produce the file to commit to
   this repository.
6. Commit the resulting `page-20180820-20180918.csv` and
   `repo-20180820-20180918.csv` files that cover the 30 day period you extracted.

## How to update the visits per day data

1. Visit [Google Analytics - Audience Overview](https://analytics.google.com/analytics/web/#/report/visitors-overview/a101904940w149250546p154152886/_u.date00=20180101&_u.date01=20180918)
2. Update the ending date to today's date
3. Check that the start date is the 1 January 2018
4. Export the data to a CSV
5. Edit the input file name in `daily-data.ipynb` and run it
