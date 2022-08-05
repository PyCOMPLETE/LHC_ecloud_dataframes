from ecloud_dataframes import EcloudDataframes

import LHCMeasurementTools.mystyle as ms
import LHCMeasurementTools.LHC_Heatloads as HL

import numpy as np
import matplotlib.pyplot as plt

from matplotlib import rc

fontsize = 16
rc('font', **{'family': 'sans-serif', 'sans-serif': ['arial'], 'size': fontsize})

ecloud_dfs = EcloudDataframes(dataframe_pickle="LHC_ecloud_dataframes_2022.pkl")

df = ecloud_dfs["stable_beams"]
df = df.query("n_bunches_b1 > 600").query("n_bunches_b2 > 600")
total_intensity = df["intensity_b1"] + df["intensity_b2"]
impedance_hl = df["impedance_hl_halfcell"]
sr_hl = df["sr_hl_halfcell"]


plt.close("all")

## Normalized heatload
fig = plt.figure(1, figsize=(6.4*1.9, 4.8*1.5))
fig.patch.set_facecolor('w')
ax = fig.add_subplot(111)

for ii, var in enumerate(HL.heat_loads_plot_sets["AVG_ARC"]):
    colorcurr = ms.colorprog(i_prog=ii, Nplots=8)
    ax.plot(df[var]/total_intensity/1.e-13, '.', ms=10, color=colorcurr, label=var[:3])

ax.set_xlabel("Fill number")
ax.set_ylabel("Normalized heat load [$10^{-13}$ W/p+]")
ax.set_ylim(0, 6)
ax.legend(bbox_to_anchor=(1.1, 1.05),  loc='upper left', prop={'size':14})
fig.subplots_adjust(left=.1, right=.76, hspace=.28, top=.89)
ax.grid()



## Heatload

fig2 = plt.figure(2, figsize=(6.4*1.9, 4.8*1.5))
ax2 = fig2.add_subplot(111)

for ii, var in enumerate(HL.heat_loads_plot_sets["AVG_ARC"]):
    colorcurr = ms.colorprog(i_prog=ii, Nplots=8)
    ax2.plot(df[var], '.', ms=10, color=colorcurr, label=var[:3])

ax2.set_xlabel("Fill number")
ax2.set_ylabel("Heat load [W/hc]")
ax2.set_ylim(0, 210)
ax2.legend(bbox_to_anchor=(1.1, 1.05),  loc='upper left', prop={'size':14})
fig2.subplots_adjust(left=.1, right=.76, hspace=.28, top=.89)
ax2.grid()



### bunch arrows and text


def plot_arrow(start, end, y,  ax, wscale=1):
    mid = (start+end)/2.
    dx = (end-start)/2.
    ax.arrow(mid, y, dx, 0, width=0.05*wscale, head_width=0.15*wscale, head_length=1, length_includes_head=True, fc='k')
    ax.arrow(mid, y, -dx, 0, width=0.05*wscale, head_width=0.15*wscale, head_length=1, length_includes_head=True, fc='k')

tb_labels = ["603b", "987b", "1227b", "1551b", "1935"]
tb_start = [8015, 8029, 8066, 8075, 8085]
tb_end = [8028, 8064, 8073, 8084, 8091]

bpi_labels = ["1x48b", "2x48b", "3x48b", "2x48b", "3x48b", "4x48b"]
bpi_start = [8015, 8026, 8042, 8056, 8061, 8077]
bpi_end = [8024, 8031, 8047, 8060, 8077, 8091]


for start, end, label in zip(tb_start, tb_end, tb_labels):
    plot_arrow(start, end, 1.5, ax, wscale=1)
    ax.text((start+end)/2., 1.2, label, horizontalalignment="center", verticalalignment="center")
    plot_arrow(start, end, 20, ax2, wscale=35)
    ax2.text((start+end)/2., 10, label, horizontalalignment="center", verticalalignment="center")

for start, end, label in zip(bpi_start, bpi_end, bpi_labels):
    plot_arrow(start, end, 5., ax, wscale=1)
    ax.text((start+end)/2., 5.3, label, horizontalalignment="center", verticalalignment="center")
    plot_arrow(start, end, 190, ax2, wscale=35)
    ax2.text((start+end)/2., 200, label, horizontalalignment="center", verticalalignment="center")


fig.savefig("norm_hl_vs_fill.png")
fig2.savefig("hl_vs_fill.png")


plt.show()
