"""COVID-19 population sample simulation for Assignment 2."""
from datetime import date, timedelta
from pathlib import Path
import random
import pandas as pd
import helper
from sim_parameters import TRANSITION_PROBS, HOLDING_TIMES

AGE_GROUPS = ['less_5', '5_to_14', '15_to_24', '25_to_64', 'over_65']
STATES = ['D', 'H', 'I', 'M', 'S']
SIMULATED_FILE = 'a2-covid-simulated-timeseries.csv'
SUMMARY_FILE = 'a2-covid-summary-timeseries.csv'


def _as_date(value):
    return value if isinstance(value, date) else date.fromisoformat(str(value)[:10])


def _choose_next_state(age_group, state):
    transitions = TRANSITION_PROBS[age_group][state]
    return random.choices(list(transitions), weights=list(transitions.values()), k=1)[0]


def _simulate_person(person_id, age_group, country, dates):
    state, previous_state, staying_days, rows = 'H', 'H', 0, []
    for i, day in enumerate(dates):
        if i:
            previous_state = state
            holding_time = max(1, int(HOLDING_TIMES[age_group][state]))
            if staying_days >= holding_time - 1:
                next_state = _choose_next_state(age_group, state)
                if next_state != state:
                    state, staying_days = next_state, 0
                else:
                    staying_days += 1
            else:
                staying_days += 1
        rows.append({
            'person_id': person_id, 'age_group_name': age_group,
            'country': country, 'date': day.isoformat(), 'state': state,
            'staying_days': staying_days, 'prev_state': previous_state
        })
    return rows


def run(countries_csv_name, countries, start_date, end_date, sample_ratio):
    if not countries:
        raise ValueError('Please select at least one country.')
    if float(sample_ratio) <= 0:
        raise ValueError('sample_ratio must be greater than zero.')
    start, end = _as_date(start_date), _as_date(end_date)
    if end < start:
        raise ValueError('end_date must be on or after start_date.')

    base_dir = Path(__file__).resolve().parent
    csv_path = Path(countries_csv_name)
    if not csv_path.is_absolute():
        csv_path = base_dir / csv_path
    country_df = pd.read_csv(csv_path)
    country_df['country'] = country_df['country'].astype(str)
    missing = [c for c in countries if c not in set(country_df['country'])]
    if missing:
        raise ValueError('Unknown country name(s): ' + ', '.join(missing))

    dates = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    rows, person_id = [], 0
    for country in countries:
        info = country_df.loc[country_df['country'] == country].iloc[0]
        total = int(round(float(info['population']) / float(sample_ratio)))
        for age_group in AGE_GROUPS:
            count = int(round(total * float(info[age_group]) / 100.0))
            for _ in range(max(0, count)):
                rows.extend(_simulate_person(person_id, age_group, country, dates))
                person_id += 1

    simulated_df = pd.DataFrame(rows, columns=[
        'person_id', 'age_group_name', 'country', 'date', 'state',
        'staying_days', 'prev_state'
    ])
    simulated_df.to_csv(base_dir / SIMULATED_FILE, index=False)

    full_index = pd.MultiIndex.from_product(
        [[d.isoformat() for d in dates], countries], names=['date', 'country'])
    counts = (simulated_df.groupby(['date', 'country', 'state']).size()
              .unstack(fill_value=0).reindex(columns=STATES, fill_value=0))
    summary_df = counts.reindex(full_index, fill_value=0).reset_index()
    for state in STATES:
        summary_df[state] = summary_df[state].astype(int)
    summary_df = summary_df[['date', 'country', 'D', 'H', 'I', 'M', 'S']]
    summary_df.to_csv(base_dir / SUMMARY_FILE, index=False)
    helper.create_plot(SUMMARY_FILE, list(countries))
    return summary_df


if __name__ == '__main__':
    run('a2-countries.csv', ['Afghanistan', 'Sweden', 'Japan'],
        '2021-04-01', '2022-04-30', 1e6)