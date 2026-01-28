import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MaxNLocator

# ------------------ Page config ------------------
st.set_page_config(page_title="World Bank WDI Dashboard", layout="wide")
st.title("🌍 World Bank Development Indicators (1960–2022)")

# ------------------ Load data safely ------------------
try:
    df = pd.read_csv("world_bank_development_indicators.csv")
except FileNotFoundError:
    st.error("world_bank_development_indicators.csv not found!")
    st.stop()

# 1. Clean column names (matches your logic)
df.columns = df.columns.str.strip().str.replace('%','pct').str.replace(' ','_')

# 2. FIX: Calculate missing GDP per capita
if 'GDP_current_US' in df.columns and 'population' in df.columns:
    df['GDP_per_capita'] = df['GDP_current_US'] / df['population']

# 3. Clean 'date' and 'year'
df['year'] = pd.to_datetime(df['date'], errors='coerce').dt.year
df = df.dropna(subset=['year'])
df['year'] = df['year'].astype(int)

# ------------------ Sidebar filters ------------------
st.sidebar.header("Filters")
countries = st.sidebar.multiselect("Select Countries", options=df['country'].unique(), default=['United States', 'China', 'India', 'Germany'])
year_range = st.sidebar.slider("Select Year Range", int(df['year'].min()), int(df['year'].max()), (1990, 2022))

filtered_df = df[(df['country'].isin(countries)) & (df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]

def five_year_ticks(ax):
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=10))
    plt.xticks(rotation=45)

# ------------------ Questions (Corrected Naming) ------------------
question = st.sidebar.selectbox("Choose Question", [
    "Q1 Global GDP", "Q2 Wealth vs Health", "Q3 CO₂ Emitters", "Q4 Renewable Energy",
    "Q5 Electricity Access", "Q6 Education & HCI", "Q7 Birth & Death Rates",
    "Q8 Internet Divide", "Q9 Governance & Stability", "Q10 Land Use",
    "Q11 Military Spending", "Q12 Inflation", "Q13 Health Spending", 
    "Q14 Safety & Wealth", "Q15 R&D & GDP"
])

# Q1: Global GDP
if question == "Q1 Global GDP":
    gdp = filtered_df.groupby('year')['GDP_current_US'].sum().reset_index()
    st.line_chart(gdp.set_index('year'))

# Q2: Wealth vs Health (Fixed: life_expectancy_at_birth)
elif question == "Q2 Wealth vs Health":
    data = filtered_df.dropna(subset=['GDP_per_capita', 'life_expectancy_at_birth'])
    if not data.empty:
        latest_yr = data['year'].max()
        fig, ax = plt.subplots()
        sns.scatterplot(data=data[data['year'] == latest_yr], x='GDP_per_capita', y='life_expectancy_at_birth', hue='country', ax=ax)
        ax.set_title(f"GDP per Capita vs Life Expectancy ({latest_yr})")
        st.pyplot(fig)
    else: st.warning("No data found for these filters.")

# Q4: Renewable Energy (Fixed: Typo 'renewvable')
elif question == "Q4 Renewable Energy":
    fig, ax = plt.subplots()
    sns.lineplot(data=filtered_df, x='year', y='renewvable_energy_consumptionpct', hue='country', ax=ax)
    five_year_ticks(ax)
    st.pyplot(fig)

# Q6: Education & HCI (Fixed: lowercase names)
elif question == "Q6 Education & HCI":
    # Note: 'mean_years_schooling' isn't in your CSV, using 'government_expenditure_on_educationpct'
    fig, ax = plt.subplots()
    sns.scatterplot(data=filtered_df, x='government_expenditure_on_educationpct', y='human_capital_index', hue='country', ax=ax)
    st.pyplot(fig)

# Q9: Governance (Fixed: spelling 'goverment')
elif question == "Q9 Governance & Stability":
    fig, ax = plt.subplots()
    sns.scatterplot(data=filtered_df, x='goverment_effectiveness_estimate', y='political_stability_estimate', hue='country', ax=ax)
    st.pyplot(fig)

# Q11: Military (Fixed: military_expenditurepct)
elif question == "Q11 Military Spending":
    fig, ax = plt.subplots()
    sns.lineplot(data=filtered_df, x='year', y='military_expenditurepct', hue='country', ax=ax)
    st.pyplot(fig)

# Q12: Inflation (Fixed: inflation_annualpct)
elif question == "Q12 Inflation":
    fig, ax = plt.subplots()
    sns.lineplot(data=filtered_df, x='year', y='inflation_annualpct', hue='country', ax=ax)
    st.pyplot(fig)

# Q15: R&D (Fixed: research_and_development_expenditurepct)
elif question == "Q15 R&D & GDP":
    fig, ax = plt.subplots()
    sns.scatterplot(data=filtered_df, x='research_and_development_expenditurepct', y='GDP_per_capita', hue='country', ax=ax)
    st.pyplot(fig)
