from mplsoccer.pitch import Pitch, add_image
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from PIL import Image
from urllib.request import urlopen



url = ('https://fbref.com/en/share/K4ZLs')
df = pd.read_html(url)[0]
df = df[['Unnamed: 0_level_0', 'Pressures']].copy()  # select a subset of the columns (Squad and pressure columns)
df.columns = df.columns.droplevel()  # drop the top-level of the multi-index

pressure_cols = ['Def 3rd', 'Mid 3rd', 'Att 3rd']
df_total = pd.DataFrame(df[pressure_cols].sum())
df_total.columns = ['total']
df_total = df_total.T
df_total = df_total.divide(df_total.sum(axis=1), axis=0) * 100

df[pressure_cols] = df[pressure_cols].divide(df[pressure_cols].sum(axis=1), axis=0) * 100.
df.sort_values(['Att 3rd', 'Def 3rd'], ascending=[True, False], inplace=True)
# setup a mplsoccer pitch
pitch = Pitch(line_zorder=2, line_color='black', figsize=(16, 9), layout=(4, 5),
              tight_layout=False, constrained_layout=True)

# mplsoccer calculates the binned statistics usually from raw locations, such as pressure events
# for this example we will create a binned statistic dividing the pitch into thirds for one point (0, 0)
# we will fill this in a loop later with each team's statistics from the dataframe
bin_statistic = pitch.bin_statistic([0], [0], statistic='count', bins=(3, 1))


# Plot
fig, axes = pitch.draw()
axes = axes.ravel()
teams = df['Squad'].values
vmin = df[pressure_cols].min().min()  # we normalise the heatmaps with the min / max values
vmax = df[pressure_cols].max().max()
for i, ax in enumerate(axes[:len(teams)]):
    ax.set_title(teams[i], fontsize=20)
    # fill in the bin statistics from df
    bin_statistic['statistic'] = df.loc[df.Squad == teams[i], pressure_cols].values
    heatmap = pitch.heatmap(bin_statistic, ax=ax, cmap='coolwarm', vmin=vmin, vmax=vmax)  # plot the heatmap
    # format and plot labels
    bin_statistic['statistic'] = (pd.DataFrame(bin_statistic['statistic'])
                                  .round(0).astype(np.int32).applymap(lambda x: '{:d}%'.format(x)).values)
    annotate = pitch.label_heatmap(bin_statistic, color='white', fontsize=20, ax=ax, ha='center', va='center')
    # set a black path effect around the labels
    for label in annotate:
        label.set_path_effects([path_effects.Stroke(linewidth=3, foreground='black'), path_effects.Normal()])
axes = axes.reshape(4, 5)
cbar = fig.colorbar(heatmap, ax=axes[:, 4], shrink=0.85)
cbar.ax.tick_params(labelsize=20)
# if its the Bundesliga remove the two spare pitches
if len(teams) == 18:
    for ax in axes[-1, 3:]:
        ax.remove()
title = fig.suptitle('ball touches events %, La Liga, 2020/21', fontsize=20)

# Calculate the percentage point difference from the league average
df[pressure_cols] = df[pressure_cols].values - df_total.values

# plot the percentage point difference
pitch = Pitch(line_zorder=2, line_color='black', figsize=(16, 9), layout=(4, 5),
              tight_layout=False, constrained_layout=True)
fig, axes = pitch.draw()
axes = axes.ravel()
teams = df['Squad'].values
vmin = df[pressure_cols].min().min()
vmax = df[pressure_cols].max().max()
for i, ax in enumerate(axes[:len(teams)]):
    ax.set_title(teams[i], fontsize=20)
    bin_statistic['statistic'] = df.loc[df.Squad == teams[i], pressure_cols].values
    heatmap = pitch.heatmap(bin_statistic, ax=ax, cmap='coolwarm', vmin=vmin, vmax=vmax)
    bin_statistic['statistic'] = (pd.DataFrame(bin_statistic['statistic']).round(0).astype(np.int32))
    annotate = pitch.label_heatmap(bin_statistic, color='white', fontsize=30, ax=ax, ha='center', va='center')
    for label in annotate:
        label.set_path_effects([path_effects.Stroke(linewidth=3, foreground='black'), path_effects.Normal()])
axes = axes.reshape(4, 5)
cbar = fig.colorbar(heatmap, ax=axes[:, 4], shrink=0.85, format='%d')
cbar.ax.tick_params(labelsize=20)
# if its the Bundesliga remove the two spare pitches
if len(teams) == 18:
    for ax in axes[-1, 3:]:
        ax.remove()
title = fig.suptitle('ball touches events, percentage point difference from Premier League average 2020/21',
                     fontsize=20)
plt.show()



