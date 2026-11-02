import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md
from pathlib import Path
import os

OUTPUT_NAME = 'a2-covid-simulation.png'
def get_filepath(filename):
    '''
    Returns full file path 
    '''
    source_path = Path(__file__).resolve()
    source_dir = source_path.parent
    filepath = os.path.join(source_dir,filename)
    return filepath

def save_plot(fig, filename):
    filepath = get_filepath(filename)    
    fig.savefig(filepath,dpi=300)

def read_dataset(filename):

    filepath = get_filepath(filename)

    df = pd.read_csv(filepath, sep=',', header= 0)

    return df

def create_plot(summary_csv, countries):
    """Create one stacked daily time-series chart for each selected country."""
    states_timeseries_df = read_dataset(summary_csv)
    states_timeseries_df = states_timeseries_df[['country', 'date', 'H', 'I', 'S', 'M', 'D']].copy()
    states_timeseries_df['date'] = pd.to_datetime(states_timeseries_df['date'])

    countries_num = len(countries)
    if countries_num == 0:
        raise ValueError('At least one country is required to create the plot.')

    fig, axes = plt.subplots(countries_num, 1, figsize=(16, 5 * countries_num), squeeze=False)
    state_cols = ['H', 'I', 'S', 'M', 'D']
    state_labels = ['Healthy', 'Infected (without symptoms)',
                    'Infected (with symptoms)', 'Immune', 'Deceased']
    state_colors = ['green', 'darkorange', 'indianred', 'lightseagreen', 'slategray']

    for i, country in enumerate(countries):
        ax = axes[i, 0]
        country_df = (states_timeseries_df[states_timeseries_df['country'] == country]
                      .sort_values('date').reset_index(drop=True))
        if country_df.empty:
            ax.set_title(f'Covid Infection Status in {country} (no data)')
            continue

        # Use ordinal positions for daily bars, then put month labels at the
        # actual positions of the first day of each month. This avoids the
        # previous bug where only the first 13 bars received tick positions.
        x_positions = list(range(len(country_df)))
        country_df[state_cols].plot(
            kind='bar', stacked=True, width=1.0, color=state_colors,
            ax=ax, legend=False, position=0
        )
        month_starts = country_df['date'].dt.to_period('M').ne(
            country_df['date'].dt.to_period('M').shift()
        )
        tick_positions = country_df.index[month_starts].tolist()
        tick_labels = country_df.loc[month_starts, 'date'].dt.strftime('%b %Y').tolist()
        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels, rotation=30, ha='right')
        ax.set_title(f'Covid Infection Status in {country}')
        ax.set_xlabel('Date')
        ax.set_ylabel('Number of sampled people')
        ax.legend(state_labels, loc='upper left')
        ax.grid(axis='y', alpha=0.2)

    fig.tight_layout()
    save_plot(fig, OUTPUT_NAME)
    plt.close(fig)
    print('Plotting Done!')
