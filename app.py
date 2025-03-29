import streamlit as st
import pandas as pd
import plotly.express as px

# Function to format numbers with K for thousands
def format_number(value):
    if value >= 1000:
        return f"{value/1000:,.0f}K"
    return f"{value:,.0f}"

# Load the data (replace with your CSV file path)
# For now, I'll use the sample data you provided, with the new columns
data = {
    "State": ["OYO", "OYO", "OYO", "OYO", "OYO"],
    "LGA": ["LAGELU", "LAGELU", "LAGELU", "LAGELU", "LAGELU"],
    "Ward": ["AJARA/OPEODU", "AJARA/OPEODU", "ARULOGUN EHIN/KELEBE", "AJARA/OPEODU", "LAGELU MARKET/KAJOLA/GBENA"],
    "PU-Name": ["ST. STEPHEN PRIMARY SCHOOL, ALEGONGO", "I.D.C. PRIMARY SCHOOL, OPE ODU", "COURT HALL, OLORUNDA", "I.D.C. PRIMARY SCHOOL, AJARA", "ST. DAVID'S SCHOOL, ABIDIODAN"],
    "Latitude": [7.417565, 7.417565, 7.417565, 7.417565, 7.417565],
    "Longitude": [3.937383, 3.937383, 3.937383, 3.937383, 3.937383],
    "Total_Votes": [501.0, 464.0, 449.0, 273.0, 271.0],
    "GiZ": [1.010275, 1.009426, 1.009102, 1.006207, 1.006183],
    "p_value": [0.078, 0.078, 0.076, 0.078, 0.075],
    "HotCold": ["Not Significant", "Not Significant", "Not Significant", "Not Significant", "Not Significant"],
    "Anomaly": [-1, -1, -1, 1, 1],
    "Anomaly_Label": ["Anomaly", "Anomaly", "Anomaly", "Normal", "Normal"],
    "local_moran_I": [5.482662, 4.953104, 4.738419, 2.219442, 2.190817],
    "z_score": [1.474940, 1.484867, 1.489226, 1.474940, 1.496972],
    "LM_std": [21.785931, 19.681631, 18.828537, 8.818896, 8.705150],
    "GO_abs": [1.010275, 1.009426, 1.009102, 1.006207, 1.006183],
    "IF_indicator": [1, 1, 1, 0, 0],
    "composite_outlier_score": [7.932069, 7.230352, 6.945880, 3.275034, 3.237111],
    "APC": [227, 273, 237, 146, 175],
    "APC_z_score": [3.377687, 4.378068, 3.595161, 1.616147, 2.246822],
    "APC_outlier": ["Outlier", "Outlier", "Outlier", "Normal", "Normal"],
    "LP": [228, 106, 125, 87, 74],
    "LP_z_score": [8.161980, 3.464838, 4.196360, 2.733316, 2.232801],
    "LP_outlier": ["Outlier", "Outlier", "Outlier", "Normal", "Normal"],
    "PDP": [46, 83, 84, 40, 22],
    "PDP_z_score": [0.691558, 2.242578, 2.284497, 0.440041, -0.314509],
    "PDP_outlier": ["Normal", "Normal", "Normal", "Normal", "Normal"],
    "NNPP": [0, 2, 3, 0, 0],
    "NNPP_z_score": [-0.194218, 0.335518, 0.600386, -0.194218, -0.194218],
    "NNPP_outlier": ["Normal", "Normal", "Normal", "Normal", "Normal"],
    "Accredited_Voters": [600, 550, 500, 300, 350],
    "Registered_Voters": [800, 750, 700, 500, 450]
}
#df = pd.DataFrame(data)

df = pd.read_csv("OSUN_geocoded_cleaned_final.csv")

# Set page configuration for a wide layout
st.set_page_config(layout="wide")

# Center the dashboard title with a larger font size using HTML/CSS
st.markdown(
    "<h1 style='text-align: center; color: black; font-size: 48px;'>Osun State Election Votes Dashboard</h1>",
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
# Use st.container to add borders around each visual
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

