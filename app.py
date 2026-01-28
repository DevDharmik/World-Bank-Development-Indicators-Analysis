import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MaxNLocator

# ------------------ Page config ------------------
st.set_page_config(page_title="World Bank WDI Dashboard", layout="wide")
st.title("🌍 World Bank Development Indicators (1960–2022)")

# ------------------ Load data safely ------------------
@st.cache_data
def load_data():
    try:
        # Load the CSV
        df = pd.read_csv("world_bank_development_indicators.csv")
        
        # 1. Clean column names to be Python-friendly
        # This turns 'renewvable_energy_consumption%' into 'renewvable_energy_consumptionpct'
        df.columns = df.columns.str.strip().str.replace('%','pct').str.replace(' ','_')
        
        # 2. Extract Year
        df['year'] = pd.to_datetime(df['date'], errors='coerce').dt.year
        df = df.dropna(subset=['year'])
        df['year'] = df['year'].astype(int)
        
        # 3. Calculate GDP per capita (Missing in original CSV)
        if 'GDP_current_US' in df.columns and 'population' in df.columns:
            df['GDP_per_capita'] = df['GDP_current_US'] / df['population']
            
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

df = load_data()

# ------------------ Sidebar filters ------------------
st.sidebar.header("Global Filters")
countries = st.sidebar.multiselect(
    "Select Countries", 
    options=sorted(df['country'].unique()), 
    default=['United States', 'China', 'India', 'Germany', 'Brazil']
)

# Sidebar year range
min_year, max_year = int(df['year'].min()), int(df['year'].max())
year_range = st.sidebar.slider("Year Range", min_year, max_year, (1990, max_year))

# Filter dataframe
filtered_df = df[
    (df['country'].isin(countries)) & 
    (df['year'] >= year_range[0]) & 
    (df['year'] <= year_range[1])
]

# Helper for time-series charts
def format_plot(ax, title, xlabel, ylabel):
    ax.set_title(title, fontsize=14, pad=15)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=10))
    plt.xticks(rotation=45)
    sns.despine()

# ------------------ Navigation ------------------
question = st.sidebar.selectbox("Choose a Research Question", [
    "Q1 Global GDP Growth", "Q2 Wealth vs. Health", "Q3 Top CO₂ Emitters", 
    "Q4 Renewable Energy Transition", "Q5 Infrastructure & Electricity", 
    "Q6 Education & Human Capital", "Q7 Birth & Death Rates", 
    "Q8 The Digital Divide", "Q9 Governance & Stability", 
    "Q10 Land Use Change", "Q11 Military Spending", 
    "Q12 Economic Volatility (Inflation)", "Q13 Health Spending Outcomes", 
    "Q14 Safety & Wealth", "Q15 Research & Innovation"
])

st.divider()

# ------------------ Visualization Logic ------------------

if question == "Q1 Global GDP Growth":
    st.subheader("Total Global GDP (Current US$) Over Time")
    # Sum GDP for ALL countries in the dataset to show true global trend
    global_gdp = df.groupby('year')['GDP_current_US'].sum().reset_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=global_gdp, x='year', y='GDP_current_US', marker='o', ax=ax)
    format_plot(ax, "Total Global GDP Evolution", "Year", "GDP (Trillions of US$)")
    st.pyplot(fig)

elif question == "Q2 Wealth vs. Health":
    st.subheader("GDP per Capita vs. Life Expectancy")
    # Use most recent year in selection that has data
    data = filtered_df.dropna(subset=['GDP_per_capita', 'life_expectancy_at_birth'])
    if not data.empty:
        latest = data['year'].max()
        fig, ax = plt.subplots()
        sns.scatterplot(data=data[data['year'] == latest], x='GDP_per_capita', y='life_expectancy_at_birth', hue='country', s=100, ax=ax)
        ax.set_xscale('log')
        format_plot(ax, f"Wealth vs Health in {latest}", "GDP per Capita (Log Scale)", "Life Expectancy")
        st.pyplot(fig)
    else: st.warning("No data available for this selection.")

elif question == "Q3 Top CO₂ Emitters":
    st.subheader("Top 10 CO₂ Emitters (Most Recent Year)")
    latest_co2 = df[df['CO2_emisions'].notna()]
    if not latest_co2.empty:
        yr = latest_co2['year'].max()
        top_10 = latest_co2[latest_co2['year'] == yr].nlargest(10, 'CO2_emisions')
        fig, ax = plt.subplots()
        sns.barplot(data=top_10, x='CO2_emisions', y='country', palette='Reds_r', ax=ax)
        format_plot(ax, f"Top Emitters in {yr}", "CO2 Emissions (kt)", "Country")
        st.pyplot(fig)

elif question == "Q4 Renewable Energy Transition":
    st.subheader("Renewable Energy Consumption Over Time")
    fig, ax = plt.subplots()
    sns.lineplot(data=filtered_df, x='year', y='renewvable_energy_consumptionpct', hue='country', ax=ax)
    format_plot(ax, "Renewable Energy % of Total Consumption", "Year", "% Renewable")
    st.pyplot(fig)

elif question == "Q5 Infrastructure & Electricity":
    st.subheader("Rural Population Share vs. Electricity Access")
    fig, ax = plt.subplots()
    sns.scatterplot(data=filtered_df, x='rural_population', y='access_to_electricitypct', hue='country', ax=ax)
    format_plot(ax, "Impact of Rurality on Infrastructure", "Rural Population", "Access to Electricity (%)")
    st.pyplot(fig)

elif question == "Q6 Education & Human Capital":
    st.subheader("Education Spending vs. Human Capital Index")
    fig, ax = plt.subplots()
    sns.scatterplot(data=filtered_df, x='government_expenditure_on_educationpct', y='human_capital_index', hue='country', ax=ax)
    format_plot(ax, "Investment in Education vs Outcomes", "Gov. Education Spending (% of GDP)", "Human Capital Index")
    st.pyplot(fig)

elif question == "Q7 Birth & Death Rates":
    st.subheader("Average Global Birth vs. Death Rates")
    # Show trend for selected countries
    avg_rates = filtered_df.groupby('year')[['birth_rate', 'death_rate']].mean().reset_index()
    fig, ax = plt.subplots()
    plt.plot(avg_rates['year'], avg_rates['birth_rate'], label='Birth Rate', color='blue')
    plt.plot(avg_rates['year'], avg_rates['death_rate'], label='Death Rate', color='red')
    plt.legend()
    format_plot(ax, "Demographic Transition", "Year", "Rate per 1,000 People")
    st.pyplot(fig)

elif question == "Q8 The Digital Divide":
    st.subheader("Internet Penetration vs. Economic Level")
    fig, ax = plt.subplots()
    sns.scatterplot(data=filtered_df, x='GDP_per_capita', y='individuals_using_internetpct', hue='country', ax=ax)
    ax.set_xscale('log')
    format_plot(ax, "The Link Between Wealth and Internet Access", "GDP per Capita (Log)", "Internet Usage (%)")
    st.pyplot(fig)

elif question == "Q9 Governance & Stability":
    st.subheader("Corruption Control vs. Political Stability")
    fig, ax = plt.subplots()
    sns.scatterplot(data=filtered_df, x='control_of_corruption_estimate', y='political_stability_estimate', hue='country', ax=ax)
    format_plot(ax, "Governance Quality", "Control of Corruption", "Political Stability")
    st.pyplot(fig)

elif question == "Q10 Land Use Change":
    st.subheader("Agricultural vs. Forest Land Evolution")
    land_data = filtered_df.groupby('year')[['forest_landpct', 'agricultural_landpct']].mean().reset_index()
    fig, ax = plt.subplots()
    plt.plot(land_data['year'], land_data['forest_landpct'], label='Forest %', color='green')
    plt.plot(land_data['year'], land_data['agricultural_landpct'], label='Agri %', color='orange')
    plt.legend()
    format_plot(ax, "Global Land Use Trend", "Year", "% of Land Area")
    st.pyplot(fig)

elif question == "Q11 Military Spending":
    st.subheader("Military Expenditure (% of GDP)")
    fig, ax = plt.subplots()
    sns.lineplot(data=filtered_df, x='year', y='military_expenditurepct', hue='country', ax=ax)
    format_plot(ax, "Defense Spending Trends", "Year", "% of GDP")
    st.pyplot(fig)

elif question == "Q12 Economic Volatility (Inflation)":
    st.subheader("Annual Inflation Rates")
    fig, ax = plt.subplots()
    sns.lineplot(data=filtered_df, x='year', y='inflation_annualpct', hue='country', ax=ax)
    format_plot(ax, "Consumer Price Inflation", "Year", "% Annual")
    st.pyplot(fig)

elif question == "Q13 Health Spending Outcomes":
    st.subheader("Health Spending vs. Life Expectancy")
    fig, ax = plt.subplots()
    sns.scatterplot(data=filtered_df, x='government_health_expenditurepct', y='life_expectancy_at_birth', hue='country', ax=ax)
    format_plot(ax, "Health Investment Efficiency", "Health Spending (% of GDP)", "Life Expectancy")
    st.pyplot(fig)

elif question == "Q14 Safety & Wealth":
    st.subheader("Homicide Rates vs. GDP")
    fig, ax = plt.subplots()
    sns.scatterplot(data=filtered_df, x='GDP_per_capita', y='intentional_homicides', hue='country', ax=ax)
    ax.set_xscale('log')
    format_plot(ax, "Safety and Economic Development", "GDP per Capita (Log)", "Homicides per 100k")
    st.pyplot(fig)

elif question == "Q15 Research & Innovation":
    st.subheader("R&D Investment vs. National GDP")
    fig, ax = plt.subplots()
    sns.scatterplot(data=filtered_df, x='research_and_development_expenditurepct', y='GDP_current_US', hue='country', ax=ax)
    ax.set_yscale('log')
    format_plot(ax, "Innovation vs Economic Size", "R&D Spending (% of GDP)", "Total GDP (Log Scale)")
    st.pyplot(fig)

# ------------------ Key Insights Footer ------------------
with st.expander("📌 Summary of Insights"):
    st.markdown("""
    - **Economic Growth:** Global GDP shows a consistent upward trajectory, though specific countries experience volatility.
    - **Climate:** CO2 emissions are highly concentrated in the top 10 emitting nations.
    - **Infrastructure:** A strong negative correlation exists between rural population size and electricity access in developing nations.
    - **Health & Wealth:** Life expectancy strongly correlates with GDP per capita, but the relationship follows a logarithmic curve (diminishing returns).
    """)
