# This creates the page for users to input data.
# The collected data should be appended to the 'data.csv' file.

import streamlit as st
import pandas as pd
import os # The 'os' module is used for file system operations (e.g. checking if a file exists).

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Survey",
    page_icon="📝",
)

# PAGE TITLE AND USER DIRECTIONS
st.title("Data Collection Survey 📝")
st.write("Please fill out the form below to add your data to the dataset.")

# THIS GOES OVER CONDITIONS ON PART 1 ------ ######################################################

st.divider()
st.subheader("Add a new entry")

with st.form("entry_form", clear_on_submit=True):
    name = st.text_input("Enter a name (optional)", value="")
    category = st.text_input("Enter a category:")
    value = st.number_input("Enter a corresponding value:", min_value=0.0, step=1.0, format="%.2f")
    submitted = st.form_submit_button("Submit Data")

if submitted:
    from datetime import datetime
    # basic validation
    cat = category.strip()
    if not cat:
        st.error("Please enter a category.")
        #Create one new row of data as a small table (DataFrame).
    else:
        new_row = pd.DataFrame([{
            # current date/time
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            # name or “anonymous” if blank
            "name": (name or "anonymous").strip(),
            # category and numeric value
            "category": cat,
            "value": float(value)
        }])

        # Append to data.csv (or create it if it doesn't exist yet)
        #Try to open the existing CSV; if it doesn't exist yet, create a new one.

        try:
            existing = pd.read_csv("data.csv")
            # Combine old data + new data
            df = pd.concat([existing, new_row], ignore_index=True)
        except FileNotFoundError:
            # If the file doesn't exist, just use the new row(This is why using try/except method here is ideal)
            df = new_row
            
        #Easy
            
        df.to_csv("data.csv", index=False)
        st.success("✅ Your entry has been saved to data.csv!")
        st.write(f"You entered: **Category**: {cat}, **Value**: {value}")

#####################################################################################################################



#DATA DISPLAY
        
# This section shows the current contents of the CSV file, which helps in debugging.
st.divider() # Adds a horizontal line for visual separation.
st.header("Current Data in CSV")

# Check if the CSV file exists and is not empty before trying to read it.
if os.path.exists('data.csv') and os.path.getsize('data.csv') > 0:
    # Read the CSV file into a pandas DataFrame.
    current_data_df = pd.read_csv('data.csv')
    # Display the DataFrame as a table.
    st.dataframe(current_data_df)
else:
    st.warning("The 'data.csv' file is empty or does not exist yet.")
