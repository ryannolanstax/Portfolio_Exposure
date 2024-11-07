#python3 -m streamlit run apps_exposure/test2.py 


import streamlit as st
import pandas as pd
from datetime import datetime

#new
import altair as alt

# Streamlit App Title
st.title("APPS Exposure & Risk Analysis")

st.write("MCC and Business Models can be found here: https://docs.google.com/spreadsheets/d/1CypTwnuAxxQlFPfLNweo9TYuU9Fv-6WN01kYOYChWEY/edit?gid=0#gid=0")
st.write("Please cleanup Synovous Processing Sheet before uploading, no blank space at the top")

# File Uploads for APPS and MCC Sheets
apps_file = st.file_uploader("Upload APPS Sheet", type=['csv', 'xlsx'])
mcc_file = st.file_uploader("Upload MCC Sheet", type=['csv', 'xlsx'])

# Dropdown for Month Selection
month_selection = st.selectbox("Select Month", ['January', 'February', 'March', 'April', 'May', 'June', 
                                                 'July', 'August', 'September', 'October', 'November', 'December'])

# Convert selected month to days equivalent for calculation
month_days_mapping = {
    'January': 31, 'February': 59, 'March': 90, 'April': 120, 'May': 151,
    'June': 181, 'July': 212, 'August': 243, 'September': 273,
    'October': 304, 'November': 334, 'December': 365
}
days_in_selected_month = month_days_mapping[month_selection]

# Default values
refund_days = 30
chargeback_days = 180

# Days Processing Calculation Function
def calculate_days_processing(date_opened):
    if date_opened.year < 2024:
        return days_in_selected_month
    else:
        days_in_year = (date_opened - datetime(date_opened.year, 1, 1)).days
        return days_in_selected_month - days_in_year

# Processing data when both files are uploaded
if apps_file and mcc_file:
    # Load DataFrames
    apps_df = pd.read_excel(apps_file) if apps_file.name.endswith('.xlsx') else pd.read_csv(apps_file)
    mcc_df = pd.read_excel(mcc_file, sheet_name='MCC Ratings') if mcc_file.name.endswith('.xlsx') else pd.read_csv(mcc_file)

    # Data Filtering and Processing
    apps_df = apps_df[apps_df['Date Closed'].isna()]
    apps_df = apps_df[apps_df['Association'] != 192024]
    apps_df = apps_df[apps_df['YTD Gross Sales Volume'] > 1]
    apps_df['Date Opened'] = pd.to_datetime(apps_df['Date Opened'])
    apps_df['days_processing'] = apps_df['Date Opened'].apply(calculate_days_processing)
    
    # Calculating Refund and Chargeback Rates
    apps_df['refund_rate'] = apps_df['YTD Credit Volume'] / apps_df['YTD Gross Sales Volume']
    apps_df['chargeback_rate'] = apps_df['YTD Chargeback Volume'] / apps_df['YTD Gross Sales Volume']

    # Convert columns for proper merging
    apps_df['MCC'] = apps_df['MCC'].astype(str)
    mcc_df['MCC'] = mcc_df['MCC'].astype(str)
    apps_df['MID'] = apps_df['MID'].astype(str)

    # Merge APPS and MCC DataFrames
    df_merged = apps_df.merge(mcc_df, on='MCC', how='left')

    # Calculating Risk Metrics
    df_merged['refund_risk'] = (df_merged['YTD Volume Card-NOT-Present'] / df_merged['days_processing']) * df_merged['refund_rate'] * refund_days
    df_merged['chargeback_risk'] = (df_merged['YTD Volume Card-NOT-Present'] / df_merged['days_processing']) * df_merged['chargeback_rate'] * chargeback_days
    df_merged['cnp_dd_risk'] = (df_merged['YTD Volume Card-NOT-Present'] / df_merged['days_processing']) * df_merged['CNP']
    df_merged['cp_dd_risk'] = (df_merged['YTD Volume Card-Present'] / df_merged['days_processing']) * df_merged['CP/ACH']
    
    # Total Exposure Calculation
    df_merged['exposure'] = df_merged['refund_risk'] + df_merged['chargeback_risk'] + df_merged['cnp_dd_risk'] + df_merged['cp_dd_risk']
    total_exposure = df_merged['exposure'].sum()
    max_exposure = df_merged['exposure'].max()

    # Display results
    st.write("Total Exposure: $", f"{total_exposure:,.2f}")
    st.write("Max Exposure: $", f"{max_exposure:,.2f}")


    def categorize_exposure(value):
        if value < 100000:
            return 'under_100k'
        elif 100000 <= value < 500000:
            return 'Range_100k_500k'
        else:
            return 'Range_Over_500k'

    df_merged['exposure_category'] = df_merged['exposure'].apply(categorize_exposure)

    # Step 2: Group by category and count merchants
    exposure_counts = df_merged.groupby('exposure_category').size().reset_index(name='number_of_merchants')

    # Step 3: Plot using Altair
    chart = alt.Chart(exposure_counts).mark_bar().encode(
        x=alt.X('exposure_category', title='Exposure Threshold'),
        y=alt.Y('number_of_merchants', title='Total Merchants'),
        tooltip=['number_of_merchants']
    ).properties(
        title='Exposure Count by Threshold Level'
    )

    # Step 4: Display in Streamlit
    st.altair_chart(chart, use_container_width=True)

    # Save processed file
    st.write("Download the processed data:")
    df_merged.to_excel("APPS_Exposure.xlsx", index=False)
    st.download_button(
        label="Download APPS Exposure Data",
        data=open("APPS_Exposure.xlsx", "rb").read(),
        file_name="APPS_Exposure.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
