import streamlit as st
import pandas as pd
import os

# Set page configuration
st.set_page_config(
    page_title="Data Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

# Add a title
st.title("Data Analysis Dashboard")

# Add custom CSS to make the font smaller in text areas
st.markdown(
    """
    <style>
    textarea {
        font-size: 12px !important;
        line-height: 1.1 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Function to get unique values from a column
def get_unique_values(column):
    return sorted(column.dropna().unique())

# Function to create an expandable section for each column
def create_column_section(column_name, unique_values):
    with st.expander(f"📊 {column_name}"):
        # Combine all unique values into a single string, one per line
        values_text = "\n".join(str(value) for value in unique_values)
        st.text_area(
            label="Copy all values below:",
            value=values_text,
            height=max(68, 20 * len(unique_values)),  # Dynamically size the box, min 68px
            key=f"{column_name}_all_values"
        )

# Main function
def main():
    # Get the path to the CSV files (always works regardless of where script is run from)
    csv_dir = os.path.join(os.path.dirname(__file__), "..", "Output CSVs")
    csv_dir = os.path.abspath(csv_dir)
    
    # Get list of CSV files
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
    
    if not csv_files:
        st.error("No CSV files found in the Output CSVs directory!")
        return
    
    # Create a dropdown to select the CSV file
    selected_file = st.selectbox(
        "Select a CSV file to analyze:",
        sorted(csv_files, key=lambda x: x.lower())  # sort files alphabetically, case-insensitive
    )
    
    # Read the selected CSV file
    df = pd.read_csv(os.path.join(csv_dir, selected_file))
    
    # --- NEW: Bulk search bar for headers ---
    search_input = st.text_area(
        "Bulk header search (comma or newline separated):",
        placeholder="Type header names or keywords here..."
    )
    # Parse search terms
    search_terms = []
    if search_input.strip():
        # Split by comma or newline, strip whitespace, ignore empty
        search_terms = [term.strip().lower() for term in search_input.replace(',', '\n').split('\n') if term.strip()]
    
    # Sort columns alphabetically, ignoring case and leading/trailing spaces
    sorted_columns = sorted(df.columns, key=lambda x: x.strip().lower())
    # If search terms are provided, filter columns
    if search_terms:
        sorted_columns = [
            col for col in sorted_columns
            if any(term in col.strip().lower() for term in search_terms)
        ]
    small_columns = []  # < 300 unique values
    large_columns = []  # >= 300 unique values
    for column in sorted_columns:
        unique_values = get_unique_values(df[column])
        if len(unique_values) < 300:
            small_columns.append((column, unique_values))
        else:
            large_columns.append((column, unique_values))

    tab1, tab2 = st.tabs(["Copy-Paste Friendly (<300 unique values)", "Large Columns (300+ unique values)"])

    with tab1:
        if not small_columns:
            st.info("No columns with less than 300 unique values.")
        for column, unique_values in small_columns:
            create_column_section(column, unique_values)

    with tab2:
        if not large_columns:
            st.info("No columns with 300 or more unique values.")
        for column, unique_values in large_columns:
            with st.expander(f"📊 {column} ({len(unique_values)} unique values)"):
                st.write(f"Too many unique values to display for easy copy-paste. Total: {len(unique_values)}.")

if __name__ == "__main__":
    main() 