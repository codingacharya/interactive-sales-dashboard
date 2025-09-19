import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("sales_data.csv", parse_dates=["Date"])

df = load_data()

st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("📊 Interactive Sales Dashboard")

# Sidebar Filters
st.sidebar.header("Filters")
regions = st.sidebar.multiselect("Select Region(s)", options=df["Region"].unique(), default=df["Region"].unique())
countries = st.sidebar.multiselect("Select Country(s)", options=df["Country"].unique(), default=df["Country"].unique())
categories = st.sidebar.multiselect("Select Product Category", options=df["ProductCategory"].unique(), default=df["ProductCategory"].unique())
date_range = st.sidebar.date_input("Select Date Range", [df["Date"].min(), df["Date"].max()])

# Apply filters (fix datetime vs date issue)
start_date = pd.to_datetime(date_range[0])
end_date = pd.to_datetime(date_range[1])

df_filtered = df[
    (df["Region"].isin(regions)) &
    (df["Country"].isin(countries)) &
    (df["ProductCategory"].isin(categories)) &
    (df["Date"].between(start_date, end_date))
]

# KPIs
total_sales = df_filtered["TotalSales"].sum()
total_units = df_filtered["UnitsSold"].sum()
avg_price = df_filtered["UnitPrice"].mean()

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("💰 Total Sales", f"${total_sales:,.0f}")
kpi2.metric("📦 Units Sold", f"{total_units:,}")
kpi3.metric("🏷️ Avg Price", f"${avg_price:,.2f}")

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Drill-Down", "📈 Trends", "📊 Aggregations", "📌 Insights", "📄 Data"])

# --- Tab 1: Drill-Down ---
with tab1:
    st.subheader("🔎 Sales Drill-Down")
    level = st.radio("Select Drill Level", ["Region", "Country", "ProductCategory", "Product"], horizontal=True)

    fig = px.bar(
        df_filtered.groupby(level, as_index=False)["TotalSales"].sum(),
        x=level,
        y="TotalSales",
        text="TotalSales",
        title=f"Total Sales by {level}",
        hover_data=["TotalSales"]
    )
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 2: Trends ---
with tab2:
    st.subheader("📈 Sales Over Time")
    time_agg = st.selectbox("Aggregate By", ["Day", "Month"], index=1)

    df_time = df_filtered.copy()
    if time_agg == "Month":
        df_time["Period"] = df_time["Date"].dt.to_period("M").dt.to_timestamp()
    else:
        df_time["Period"] = df_time["Date"]

    fig2 = px.line(
        df_time.groupby("Period", as_index=False)["TotalSales"].sum(),
        x="Period",
        y="TotalSales",
        markers=True,
        title=f"Total Sales Over Time ({time_agg})"
    )
    st.plotly_chart(fig2, use_container_width=True)

# --- Tab 3: Aggregations ---
with tab3:
    st.subheader("📊 Aggregation Views")
    agg_dim = st.selectbox("Aggregate Sales By", ["Region", "Country", "ProductCategory", "Product"])

    fig3 = px.pie(
        df_filtered.groupby(agg_dim, as_index=False)["TotalSales"].sum(),
        names=agg_dim,
        values="TotalSales",
        title=f"Sales Distribution by {agg_dim}"
    )
    st.plotly_chart(fig3, use_container_width=True)

# --- Tab 4: Insights (Top N, Correlation, Map) ---
with tab4:
    st.subheader("📌 Insights")

    # Top N Products
    top_n = st.slider("Show Top N Products by Sales", 1, 10, 5)
    top_products = (df_filtered.groupby("Product")["TotalSales"].sum()
                    .sort_values(ascending=False).head(top_n))
    st.bar_chart(top_products)

    # Correlation Heatmap
    st.write("### 🔥 Correlation Heatmap")
    corr = df_filtered[["UnitsSold", "UnitPrice", "TotalSales"]].corr()
    fig_corr, ax = plt.subplots()
    sns.heatmap(corr, annot=True, cmap="Blues", ax=ax)
    st.pyplot(fig_corr)

    # Map Visualization
    st.write("### 🌍 Sales by Country")
    fig_map = px.choropleth(df_filtered,
                            locations="Country",
                            locationmode="country names",
                            color="TotalSales",
                            hover_name="Country",
                            title="Sales by Country")
    st.plotly_chart(fig_map, use_container_width=True)

# --- Tab 5: Data + Export ---
with tab5:
    st.subheader("📄 Filtered Data")
    st.dataframe(df_filtered)

    # Export CSV
    csv = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Filtered Data (CSV)", csv, "filtered_sales.csv", "text/csv")
