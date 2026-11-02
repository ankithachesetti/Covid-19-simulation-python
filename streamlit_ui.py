"""Streamlit interface for the COVID-19 simulation assignment."""
from pathlib import Path
import pandas as pd
import streamlit as st
import assignment2

BASE_DIR = Path(__file__).resolve().parent
COUNTRIES_FILE = BASE_DIR / 'a2-countries.csv'
PLOT_FILE = BASE_DIR / 'a2-covid-simulation.png'

st.set_page_config(page_title='Covid-19 Population Simulation', layout='wide')
st.title('Covid-19 Population Simulation')

countries_df = pd.read_csv(COUNTRIES_FILE)
country_options = countries_df['country'].dropna().astype(str).tolist()

sample_ratio = st.number_input(
    'Sample Ratio', min_value=1.0, value=1_000_000.0, step=100_000.0, format='%.2f'
)
start_date = st.date_input('Start Date', value=pd.Timestamp('2021-04-01').date())
end_date = st.date_input('End Date', value=pd.Timestamp('2022-04-30').date())
selected_countries = st.multiselect(
    'Select Countries', options=country_options, default=['Afghanistan', 'Sweden', 'Argentina']
)

if st.button('Run'):
    if not selected_countries:
        st.error('Please select at least one country.')
    elif end_date < start_date:
        st.error('End Date must be on or after Start Date.')
    else:
        try:
            with st.spinner('Running simulation...'):
                assignment2.run(
                    countries_csv_name=str(COUNTRIES_FILE),
                    countries=selected_countries,
                    sample_ratio=sample_ratio,
                    start_date=start_date,
                    end_date=end_date,
                )
            st.success(
                f'Running with the following settings: Sample Ratio: {sample_ratio} '
                f'Start Date: {start_date} End Date: {end_date} Countries: {selected_countries}'
            )
            if PLOT_FILE.exists():
                st.image(str(PLOT_FILE), caption='COVID-19 simulation results', use_container_width=True)
            st.download_button(
                'Download simulated time series CSV',
                data=(BASE_DIR / 'a2-covid-simulated-timeseries.csv').read_bytes(),
                file_name='a2-covid-simulated-timeseries.csv',
                mime='text/csv',
            )
            st.download_button(
                'Download summary time series CSV',
                data=(BASE_DIR / 'a2-covid-summary-timeseries.csv').read_bytes(),
                file_name='a2-covid-summary-timeseries.csv',
                mime='text/csv',
            )
        except Exception as exc:
            st.error(f'Simulation failed: {exc}')

elif PLOT_FILE.exists():
    st.image(str(PLOT_FILE), caption='Latest COVID-19 simulation results', use_container_width=True)
