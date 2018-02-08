# Binder Data

A place to store data for Binder. Analysis / description / etc should be done in other
repositories so that we can decouple data and code to analyze it!

## How to update the data in this repository

Currently, the only way to update the data contained in the repository is to:

* Clone the repository
* Make sure you have `gsutil` access to the binder billing data
* Run the script that updates the data (for billing, it is in `billing/update_data.py`)
* Push the updates

We should work on improving this process (see [this issue](https://github.com/jupyterhub/mybinder.org-deploy/issues/345)).
