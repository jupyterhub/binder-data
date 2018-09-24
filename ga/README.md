# Binder Google Analytics data

This folder contains Google Analytics data from the last 6 months for
the service running at `mybinder.org`. It is the total number of users for
the top 5000 repositories that have been run on the site. This includes
the multiple versions (e.g. multiple branches) of the same repository.

## To update this data

Updating this data involves a manual data dump step, followed by a light
munging step. If you have suggestions for how to improve this process, please
recommend something!

To update this data:

### Download the data

1. Ensure that you have Google Analytics access to the `mybinder.org` project.
2. Open the Google Analytics page for `mybinder.org`
3. On the left, click `Behavior --> Site Content --> All Pages`. You should see
   a list of many repositories built on `mybinder.org`.
4. In the top-right, set the dates to a range covering the last 6 months. It
   doesn't have to be exact, just more-or-less correct!
5. Scroll to the bottom. Find the "show rows" drop-down. Set it to the maximum
   possible allowed value (currently it is 5000).
6. Scroll back up. Click on "Export", then "CSV". This will download the data.

### Munge the data

1. Move the downloaded data to the `data` folder in this directory. Rename the
   CSV file to `ga_raw.csv`.
2. Run the script to munge and collect the data. From the root of this repository, run:

   ```
   python ga/update_data.py
   ```
   
3. The result should be an updated `data/ga_clean.csv` file! 
