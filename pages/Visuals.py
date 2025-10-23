
import streamlit as st               
import pandas as pd                    
import json                           
from pathlib import Path              

st.set_page_config(
    page_title="Visualizations",
    page_icon="📈",
)


# Page title
st.title("Data Visualizations 📈")
st.write("This page displays graphs based on the collected data")

st.divider()
st.header("Load Data")


# Paths to the two files in the project
path_one = Path(__file__).resolve().parent.parent / "data.csv"
path_two = Path(__file__).resolve().parent.parent / "data.json"

# CSV loading


try:
    csv_df = pd.read_csv(path_one)                               # Read the entire CSV into a DataFrame
    if "value" in csv_df.columns:
        csv_df["value"] = pd.to_numeric(csv_df["value"], errors="coerce")  # Ensure numeric -- This che
    if "timestamp" in csv_df.columns:
        csv_df["timestamp"] = pd.to_datetime(csv_df["timestamp"], errors="coerce")  # Ensure datetime -- this also means that instead of error when condition isnt met, then it wont trip out and error.

    st.success(f"Loaded CSV: {path_one.name}  •  rows = {len(csv_df)}") #If everything works out then it prints rows num and shows green success message


    
except FileNotFoundError: #This happens when data.csv doesnt exist already - It CREATES AN EMPTY ONE ALREADY TO FILL IN LATER
    csv_df = pd.DataFrame(columns=["timestamp", "name", "category", "value"])       # Empty placeholder
    st.warning("CSV not found yet — add an entry on the **Survey** page to create data.csv.")

#This happens when data exists but doesnt have rows
    
except pd.errors.EmptyDataError:
    csv_df = pd.DataFrame(columns=["timestamp", "name", "category", "value"])
    st.warning("CSV exists but is empty — submit an entry on the **Survey** page.")

#This catches any other errors
except Exception as e:
    csv_df = pd.DataFrame(columns=["timestamp", "name", "category", "value"])
    st.error(f"Could not read CSV ({type(e).__name__}): {e}")

# This is the Json loading in with erroring mad
try:
    with open(path_two, "r") as f:
        json_obj = json.load(f) #---> This basically reads the words and translates it to python words/language
    st.success(f"Loaded JSON: {path_two.name}")


    
except FileNotFoundError:
    json_obj = None
    st.warning("data.json not found — create it in the project root.") #Happens only if data.json doesnt exist at all

    
except json.JSONDecodeError as e: #Happens if data.json has broken syntax
    json_obj = None
    st.error(f"data.json has invalid JSON (syntax error): {e}")
    
st.divider()
st.header("Graphs")
##


#####


st.subheader("Graph 1 (Static): Targets vs Actuals (JSON snapshot)")
if json_obj:
    
    # This pulls lists safetly and everythign inside
    targets_list = json_obj.get("weekly_targets", [])
    actuals_list = json_obj.get("sample_actuals", [])

    # Convert to DataFrames
    targets_df = pd.DataFrame(targets_list) if targets_list else pd.DataFrame(columns=["label", "target"])
    actuals_df = pd.DataFrame(actuals_list) if actuals_list else pd.DataFrame(columns=["label", "value"])

    # Keep only the columns we need when present
    if not targets_df.empty:
        targets_df = targets_df[["label", "target"]]

        
    if not actuals_df.empty:
        actuals_df = actuals_df[["label", "value"]]

    # Merge by label so each row has: label | target | value
    merged = pd.merge(targets_df, actuals_df, on="label", how="outer").fillna(0)


    plot_df = merged.set_index("label")[["target", "value"]]
    plot_df.columns = ["Target", "Actual"]




    st.bar_chart(plot_df)
    st.caption("Static snapshot comparing Target vs Actual values from data.json.")
else:
    st.info("Cannot build Graph 1 yet because data.json did not load in the **Load Data** step.")






st.subheader("Graph 2 (Dynamic): CSV Time Series with Rolling Average")


if not csv_df.empty and "category" in csv_df.columns and "timestamp" in csv_df.columns:
    # Build category options from the CSV
    categories = sorted([c for c in csv_df["category"].dropna().unique()])



    if "g2_category" not in st.session_state:
        st.session_state.g2_category = categories[0] if categories else None
    if "g2_window" not in st.session_state:
        st.session_state.g2_window = 3

    #This makes the grapgh dynamic
        
    left, right = st.columns(2)
    with left:
        chosen = st.selectbox("Choose a CSV category", options=categories, index=categories.index(st.session_state.g2_category) if st.session_state.g2_category in categories else 0)
        st.session_state.g2_category = chosen
    with right:
        window = st.slider("Rolling average window", min_value=1, max_value=7, value=st.session_state.g2_window, help="Smooths the line by averaging this many points")
        st.session_state.g2_window = window

    # Filter CSV and I got to caluclate avg 
    df_cat = csv_df[csv_df["category"] == st.session_state.g2_category].copy()
    df_cat = df_cat.dropna(subset=["timestamp", "value"]).sort_values("timestamp")
    if not df_cat.empty:
        df_cat["rolling_mean"] = df_cat["value"].rolling(st.session_state.g2_window, min_periods=1).mean()

        # Plot value and rolling_mean against time
        st.line_chart(df_cat.set_index("timestamp")[["value", "rolling_mean"]])
        st.caption(
            f"Dynamic time series for **{st.session_state.g2_category}** "
            f"with a {st.session_state.g2_window}-point rolling average. "
            "Use the dropdown and slider to update the chart."
        )
    else:
        st.info("No rows for that category yet — add entries on the **Survey** page.")
else:
    st.info("Need CSV data with 'timestamp', 'category', and 'value' columns to plot this graph.")

# -----------


st.subheader("Graph 3 (Dynamic): JSON — Pick Items to Compare")
if json_obj:
    # Reuse the merged table shape from Graph 1
    targets_list = json_obj.get("weekly_targets", [])
    actuals_list = json_obj.get("sample_actuals", [])
    targets_df = pd.DataFrame(targets_list) if targets_list else pd.DataFrame(columns=["label", "target"])
    actuals_df = pd.DataFrame(actuals_list) if actuals_list else pd.DataFrame(columns=["label", "value"])
    if not targets_df.empty:
        targets_df = targets_df[["label", "target"]]
    if not actuals_df.empty:
        actuals_df = actuals_df[["label", "value"]]
    merged = pd.merge(targets_df, actuals_df, on="label", how="outer").fillna(0)

    # Build list of all labels and a multiselect widget
    all_labels = list(merged["label"].unique())

    # Use selection in this
    if "g3_labels" not in st.session_state:
        st.session_state.g3_labels = all_labels

    selected = st.multiselect("Choose labels to display", options=all_labels, default=st.session_state.g3_labels)
    st.session_state.g3_labels = selected

    # Filter and plot only selected labels
    filtered = merged[merged["label"].isin(st.session_state.g3_labels)].set_index("label")
    if not filtered.empty:
        display_df = filtered[["target", "value"]]
        display_df.columns = ["Target", "Actual"]
        st.bar_chart(display_df)
        st.caption("Dynamic JSON chart — You can compare graphs by adding and subtracting in the multiselect.")
    else:
        st.info("Select at least one label to visualize.")
else:
    st.info("Cannot build Graph 3 yet because data.json did not load in the **Load Data** step.")
