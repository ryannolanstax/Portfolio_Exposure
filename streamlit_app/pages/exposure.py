import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Upload files
apps_file = st.file_uploader("Upload APPS file", type=["xlsx"])
mcc_file = st.file_uploader("Upload MCC Sheet", type=["xlsx"])

# Month selection
month_selected = st.selectbox("Select the month", [
    "January", "February", "March", "April", "May", "June", "July"
])

if apps_file is not None and mcc_file is not None:
    # Read files
    df = pd.read_excel(apps_file)
    mcc_df = pd.read_excel(mcc_file)

    # Rename columns for join (if needed)
    if 'MCC' not in df.columns:
        if 'MCC Code' in df.columns:
            df.rename(columns={'MCC Code': 'MCC'}, inplace=True)

    # Merge on MCC
    df = df.merge(mcc_df, how='left', on='MCC')

    # Ensure 'Date Opened' is datetime
    df['Date Opened'] = pd.to_datetime(df['Date Opened'], errors='coerce')

    # Filter for selected month
    df['month'] = df['Date Opened'].dt.month_name()
    df_filtered = df[df['month'] == month_selected]

    # Calculate days_processing
    def calculate_days(row):
        if pd.isnull(row['Date Opened']):
            return None
        if row['Date Opened'].year < 2024:
            return 273
        else:
            return 273 - (row['Date Opened'] - pd.Timestamp('2024-01-01')).days

    df_filtered['days_processing'] = df_filtered.apply(calculate_days, axis=1)

    # Show filtered data
    st.dataframe(df_filtered)

    # --- Visualization using seaborn ---
    st.subheader("Days Processing by MCC Description")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=df_filtered,
        x="days_processing",
        y="MCC Description",
        errorbar=None,
        ax=ax
    )
    ax.set_title("Days Processing by MCC Description")
    ax.set_xlabel("Days Processing")
    ax.set_ylabel("MCC Description")
    st.pyplot(fig)
