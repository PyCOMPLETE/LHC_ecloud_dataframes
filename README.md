# LHC_ecloud_dataframes

To update dataframes:

```
$ cd ../LHC_followup_download_scripts
$ ./download_all.sh
$ cd ../LHC_ecloud_dataframes
$ python 000_update_dataframes.py
```

To plot (normalized) heat load vs fill:

```
$ python 001_plot_normhl_vs_fill.py
```
