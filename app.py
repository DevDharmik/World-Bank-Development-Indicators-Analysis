import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MaxNLocator

# ------------------ Page config ------------------
st.set_page_config(page_title="World Bank WDI Dashboard", layout="wide")
st.title("🌍 World Bank Development Indicators (1960–2022)")
st.markdown("### Research Question Gallery")
st.info("All research questions are displayed below. Expand a section to view the analysis.")

# ------------------ Load and Clean Data ------------------
@st.cache_data
def load_data():
    df = pd.read_csv("world_bank_development_indicators.csv")
    df.columns = df.columns.str.strip().str.replace('%','pct').str.replace(' ','_')
    df['year'] = pd.to_datetime(df['date'], errors='coerce').dt.year
    df = df.dropna(subset=['year'])
    df['year'] = df['year'].astype(int)
    if 'GDP_current_US' in df.columns and 'population' in df.columns:
        df['GDP_per_capita'] = df['GDP_current_US'] / df['population']
    return df

df = load_data()

# ------------------ Main Page Global Filters ------------------
# We place filters at the top of the page since the sidebar is gone
col1, col2 = st.columns([2, 1])
with col1:
    countries = st.multiselect(
        "Select Countries to Compare", 
        options=sorted(df['country'].unique()), 
        default=['United States', 'China', 'India', 'Germany', 'Brazil']
    )
with col2:
    year_range = st.slider("Year Range", int(df['year'].min()), int(df['year'].max()), (1990, 2022))

filtered_df = df[(df['country'].isin(countries)) & (df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]

# Helper for styling
def format_plot(ax, title, xlabel, ylabel):
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=10))
    plt.xticks(rotation=45)
    sns.despine()
    plt.tight_layout()

# ------------------ Question Display ------------------
# We use a dictionary to organize the questions and their configurations
questions = {
    "Q1 Global GDP Growth": ("year", "GDP_current_US", "line"),
    "Q2 Wealth vs. Health": ("GDP_per_capita", "life_expectancy_at_birth", "scatter"),
    "Q3 Top CO₂ Emitters": ("CO2_emisions", "country", "bar"),
    "Q4 Renewable Energy": ("year", "renewvable_energy_consumptionpct", "line"),
    "Q5 Infrastructure": ("rural_population", "access_to_electricitypct", "scatter"),
    "Q6 Education & HCI": ("government_expenditure_on_educationpct", "human_capital_index", "scatter"),
    "Q7 Birth & Death": ("year", ["birth_rate", "death_rate"], "multi_line"),
    "Q8 Digital Divide": ("GDP_per_capita", "individuals_using_internetpct", "scatter"),
    "Q9 Governance": ("control_of_corruption_estimate", "political_stability_estimate", "scatter"),
    "Q10 Land Use": ("year", ["forest_landpct", "agricultural_landpct"], "multi_line"),
    "Q11 Military": ("year", "military_expenditurepct", "line"),
    "Q12 Inflation": ("year", "inflation_annualpct", "line"),
    "Q13 Health Spending": ("government_health_expenditurepct", "life_expectancy_at_birth", "scatter"),
    "Q14 Safety & Wealth": ("GDP_per_capita", "intentional_homicides", "scatter"),
    "Q15 Innovation": ("research_and_development_expenditurepct", "GDP_current_US", "scatter")
}

for q_title, config in questions.items():
    with st.expander(f"📊 {q_title}", expanded=(q_title == "Q1 Global GDP Growth")):
        fig, ax = plt.subplots(figsize=(10, 4))
        x_col, y_col, plot_type = config
        
        if plot_type == "line":
            sns.lineplot(data=filtered_df, x=x_col, y=y_col, hue='country', ax=ax)
            format_plot(ax, q_title, x_col, y_col)
            
        elif plot_type == "scatter":
            sns.scatterplot(data=filtered_df, x=x_col, y=y_col, hue='country', ax=ax)
            if "GDP" in x_col: ax.set_xscale('log')
            format_plot(ax, q_title, x_col, y_col)
            
        elif plot_type == "bar":
            latest_data = df[df[x_col].notna()]
            if not latest_data.empty:
                yr = latest_data['year'].max()
                top_10 = latest_data[latest_data['year'] == yr].nlargest(10, x_col)
                sns.barplot(data=top_10, x=x_col, y=y_col, palette='Reds_r', ax=ax)
                format_plot(ax, f"Top 10 in {yr}", x_col, y_col)
                
        elif plot_type == "multi_line":
            avg_data = filtered_df.groupby('year')[y_col].mean().reset_index()
            for col in y_col:
                ax.plot(avg_data['year'], avg_data[col], label=col)
            ax.legend()
            format_plot(ax, q_title, "Year", "Rate/Percentage")
            
        st.pyplot(fig)
        plt.close(fig)
