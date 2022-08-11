from ecloud_dataframes import EcloudDataframes

import LHCMeasurementTools.mystyle as ms
import LHCMeasurementTools.LHC_Heatloads as HL

import numpy as np
import matplotlib.pyplot as plt

from matplotlib import rc

fontsize = 16
rc('font', **{'family': 'sans-serif', 'sans-serif': ['arial'], 'size': fontsize})

ecloud_dfs = EcloudDataframes(dataframe_pickle="LHC_ecloud_dataframes_2022.pkl")

df = ecloud_dfs["end_of_squeeze"]
title = "End of Squeeze"
#df = ecloud_dfs["stable_beams"]
df = df.query("n_bunches_b1 > 600").query("n_bunches_b2 > 600")
total_intensity = df["intensity_b1"] + df["intensity_b2"]
# impedance_hl = df["impedance_hl_halfcell"]
# sr_hl = df["sr_hl_halfcell"]

plt.close("all")

## Normalized heatload
#fig = plt.figure(1, figsize=(6.4*1.9, 4.8*1.5))
fig0, (ax00, ax01, ax02) = plt.subplots(3, 1, figsize=(6.4*1.9, 4.8*1.5), gridspec_kw={'height_ratios': [1, 1, 2]}, sharex=True)
fig0.patch.set_facecolor('w')

for ii, var in enumerate(HL.heat_loads_plot_sets["AVG_ARC"]):
    colorcurr = ms.colorprog(i_prog=ii, Nplots=8)
    ax02.plot(df[var]/total_intensity/1.e-13, '.', ms=10, color=colorcurr, label=var[:3])

ax02.set_xlabel("Fill number")
ax02.set_ylabel("Normalized\n heat load [$10^{-13}$ W/p+]")
ax02.set_ylim(0, 6)
ax02.legend(bbox_to_anchor=(1.1, 1.05),  loc='upper left', prop={'size':14})
fig0.subplots_adjust(left=.1, right=.76, hspace=.28, top=.95)
ax02.grid()



## Heatload
fig1, (ax10, ax11, ax12) = plt.subplots(3, 1, figsize=(6.4*1.9, 4.8*1.5), gridspec_kw={'height_ratios': [1, 1, 2]}, sharex=True)
fig1.patch.set_facecolor('w')

for ii, var in enumerate(HL.heat_loads_plot_sets["AVG_ARC"]):
    colorcurr = ms.colorprog(i_prog=ii, Nplots=8)
    ax12.plot(df[var], '.', ms=10, color=colorcurr, label=var[:3])

ax12.set_xlabel("Fill number")
ax12.set_ylabel("Heat load [W/hc]")
ax12.set_ylim(0, 230)
ax12.legend(bbox_to_anchor=(1.1, 1.05),  loc='upper left', prop={'size':14})
fig1.subplots_adjust(left=.1, right=.76, hspace=.28, top=.95)
ax12.grid()


for axt in [ax02, ax12]:
    axt.set_title(title)

### plot intensities
for axt in [ax00, ax10]:
    axt.plot(df["bunch_intensity_b1_mean"]/1.e11, ".", ms=10, color='b', label="Beam 1", zorder=2)
    axt.plot(df["bunch_intensity_b2_mean"]/1.e11, ".", ms=10, color='r', label="Beam 2", zorder=1)
    axt.set_ylabel("Bunch\n intensity [10$^{11}$p+]")
    axt.grid(1)
    axt.legend(bbox_to_anchor=(1.1, -0.8),  loc='upper left', prop={'size':14})
for axt in [ax01, ax11]:
    axt.plot(df["n_bunches_b1"], ".", ms=10, color="b", zorder=2)
    axt.plot(df["n_bunches_b2"], ".", ms=10, color="r", zorder=1)
    axt.set_ylabel("Bunches")
    axt.set_ylim(600,3000)
    axt.grid(1)


# ### bunch arrows and text
# def plot_arrow(start, end, y,  ax, wscale=1):
#     mid = (start+end)/2.
#     dx = (end-start)/2.
#     ax.arrow(mid, y, dx, 0, width=0.05*wscale, head_width=0.15*wscale, head_length=1, length_includes_head=True, fc='k')
#     ax.arrow(mid, y, -dx, 0, width=0.05*wscale, head_width=0.15*wscale, head_length=1, length_includes_head=True, fc='k')
# 
# tb_labels = ["603b", "987b", "1227b", "1551b", "1935"]
# tb_start = [8015, 8029, 8066, 8075, 8085]
# tb_end = [8028, 8064, 8073, 8084, 8100]
# 
# bpi_labels = ["1x48b", "2x48b", "3x48b", "2x48b", "3x48b", "4x48b"]
# bpi_start = [8015, 8026, 8042, 8056, 8061, 8077]
# bpi_end = [8024, 8031, 8047, 8060, 8077, 8100]
# 
# 
# for start, end, label in zip(tb_start, tb_end, tb_labels):
#     plot_arrow(start, end, 1.5, ax, wscale=1)
#     ax.text((start+end)/2., 1.2, label, horizontalalignment="center", verticalalignment="center")
#     plot_arrow(start, end, 20, ax2, wscale=35)
#     ax2.text((start+end)/2., 10, label, horizontalalignment="center", verticalalignment="center")
# 
# for start, end, label in zip(bpi_start, bpi_end, bpi_labels):
#     plot_arrow(start, end, 5., ax, wscale=1)
#     ax.text((start+end)/2., 5.3, label, horizontalalignment="center", verticalalignment="center")
#     plot_arrow(start, end, 205, ax2, wscale=35)
#     ax2.text((start+end)/2., 215, label, horizontalalignment="center", verticalalignment="center")

fig0.savefig("norm_hl_vs_fill.png")
fig1.savefig("hl_vs_fill.png")
plt.show()
