# Binder Billing data

This folder contains data about billing for the service running at `mybinder.org`.

The script `update_data.py` will use the `gsutil` utility to download daily
billing data for `mybinder.org`.

## Requirements to download / update the data

To update the data in `data/`, you need these things:

1. The Google cloud [`gsutil` tool](https://cloud.google.com/storage/docs/gsutil).
   In order to access Binder's Google Cloud API.
2. The proper permissions to access the Binder Billing information.

## How to update the data in this repository

In order to update the data in this repository, we'll use the `update_data.py`
script, which will download billing information for days since the last update.
It will only download *new* data, and will not replace *old* data.

This should be done periodically, and updated data pushed as changes to this
repository in order to keep it up-to-date.

To update the billing data, follow these steps:

1. Clone the `binder-data` repository.
2. Change directories into the `billing` folder:

   ```
   cd binder-data/billing
   ```
3. Ensure that you have `gsutil` installed, that your account has access to the
   `mybinder.org` data, and that `gsutil` is configured to point to Binder. You
   can confirm this by running this command:

   ```
   gsutil ls gs://binder-billing/
   ```

   If you see a list of `.csv` files printed, then you are set up properly!
4. Run the script that updates the billing data:

   ```
   python update_data.py
   ```
5. Commit and push the updates to the `binder-data` repository.
6. Optionally, update the visualization in the [Jupyter Notebook for the
   `binder-billing` repository](https://github.com/jupyterhub/binder-billing/blob/master/analyze_data.ipynb).
