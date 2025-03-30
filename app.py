import streamlit as st
import pandas as pd
import plotly.express as px

# Function to format numbers with K for thousands
def format_number(value):
    if value >= 1000:
        return f"{value/1000:,.0f}K"
    return f"{value:,.0f}"

# Load the data
df = pd.read_csv("OSUN_geocoded_cleaned_final.csv")

# Set page configuration for a wide layout
st.set_page_config(layout="wide")

# Center the dashboard title with a larger font size using HTML/CSS
st.markdown(
    "<h1 style='text-align: center; color: black; font-size: 48px;'>Election Votes Dashboard</h1>",
    unsafe_allow_html=True
)

# Sidebar for filters
st.sidebar.header("Filters")
ward = st.sidebar.multiselect(
    "Select Ward",
    options=df["Ward"].unique(),
    default=df["Ward"].unique()
)

# Filter the data based on user selection
filtered_df = df[df["Ward"].isin(ward)]

# KPI Cards (Top Section)
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    total_votes = filtered_df["Total_Votes"].sum()
    st.metric(label="Total Votes", value=format_number(total_votes))
with col2:
    total_apc = filtered_df["APC"].sum()
    st.metric(label="Total APC Votes", value=format_number(total_apc))
with col3:
    total_lp = filtered_df["LP"].sum()
    st.metric(label="Total LP Votes", value=format_number(total_lp))
with col4:
    total_pdp = filtered_df["PDP"].sum()
    st.metric(label="Total PDP Votes", value=format_number(total_pdp))
with col5:
    total_nnpp = filtered_df["NNPP"].sum()
    st.metric(label="Total NNPP Votes", value=format_number(total_nnpp))

# Prepare data for the bar chart (Votes by Party)
party_votes = filtered_df[["APC", "LP", "PDP", "NNPP"]].sum().reset_index()
party_votes.columns = ["Party", "Votes"]

# Prepare data for the line chart (Total Votes by Ward)
votes_by_ward = filtered_df.groupby("Ward")["Total_Votes"].sum().reset_index()

# Prepare data for the pie chart (Accredited_Voters vs Registered_Voters)
voter_comparison = pd.DataFrame({
    "Voter Type": ["Accredited Voters", "Registered Voters"],
    "Count": [filtered_df["Accredited_Voters"].sum(), filtered_df["Registered_Voters"].sum()]
})

# Main Visualizations (Bar, Line, Pie, and Map)
col6, col7, col8 = st.columns(3)

with col6:
    with st.container(border=True):
        st.subheader("Votes by Party")
        fig1 = px.bar(
            party_votes,
            x="Party",
            y="Votes",
            color="Party",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig1, use_container_width=True)

with col7:
    with st.container(border=True):
        st.subheader("Total Votes by Ward")
        fig2 = px.line(
            votes_by_ward,
            x="Ward",
            y="Total_Votes",
            markers=True,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig2, use_container_width=True)

with col8:
    with st.container(border=True):
        st.subheader("Accredited vs Registered Voters")
        fig3 = px.pie(
            voter_comparison,
            names="Voter Type",
            values="Count",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig3, use_container_width=True)

# Map Visualization using Latitude and Longitude
with st.container(border=True):
    st.subheader("Polling Units Map (Colored by Anomaly)")
    fig4 = px.scatter_mapbox(
        filtered_df,
        lat="Latitude",
        lon="Longitude",
        size="Total_Votes",
        color="Anomaly_Label",
        hover_name="PU-Name",
        hover_data=["Total_Votes", "Anomaly_Label"],
        color_discrete_sequence=px.colors.qualitative.Pastel,
        zoom=10
    )
    fig4.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig4, use_container_width=True)

# Display Outliers Filtered by LGA
with st.container(border=True):
    st.subheader("Outliers by LGA")
    lga_filter = st.selectbox("Select LGA", options=df["LGA"].unique())
    lga_filtered_df = filtered_df[filtered_df["LGA"] == lga_filter]

    # Create a DataFrame for outliers
    outlier_columns = ["PU-Name", "APC_outlier", "LP_outlier", "PDP_outlier", "NNPP_outlier"]
    outlier_df = lga_filtered_df[outlier_columns]

    # Filter to show only rows where at least one party has an "Outlier" label
    outlier_df = outlier_df[
        (outlier_df["APC_outlier"] == "Outlier") |
        (outlier_df["LP_outlier"] == "Outlier") |
        (outlier_df["PDP_outlier"] == "Outlier") |
        (outlier_df["NNPP_outlier"] == "Outlier")
    ]

    if not outlier_df.empty:
        st.dataframe(outlier_df)
    else:
        st.write("No outliers found for the selected LGA.")

# New Visualization: Consistent Outliers by LGA
with st.container(border=True):
    st.subheader("Consistent Outliers by LGA")
    
    # Define consistent outliers based on multiple criteria
    # 1. Anomaly_Label is "Anomaly"
    # 2. IF_indicator is 1
    # 3. composite_outlier_score is above the 75th percentile
    score_threshold = filtered_df["composite_outlier_score"].quantile(0.75)
    consistent_outliers = filtered_df[
        (filtered_df["Anomaly_Label"] == "Anomaly") &
        (filtered_df["IF_indicator"] == 1) &
        (filtered_df["composite_outlier_score"] >= score_threshold)
    ]

    # Count consistent outliers by LGA
    if not consistent_outliers.empty:
        consistent_outliers_by_lga = consistent_outliers.groupby("LGA").size().reset_index(name="Count")
        fig5 = px.bar(
            consistent_outliers_by_lga,
            x="LGA",
            y="Count",
            color="LGA",
            title="Number of Consistent Outliers by LGA",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.write("No consistent outliers found based on the selected criteria.")