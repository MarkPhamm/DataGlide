import streamlit as st
from mitosheet.streamlit.v1 import spreadsheet
import pandas as pd
import openpyxl
import io
import pygwalker as pyg
from pygwalker.api.streamlit import StreamlitRenderer

st.set_page_config(
    page_title="DataGlide",
    initial_sidebar_state="expanded",
    layout= "wide",
    menu_items={
        'Get Help': 'https://docs.trymito.io/',
        'Report a bug': "https://docs.trymito.io/",
        'About': "# This is a Streamlit - MitoSheet App that let you manipulate Pandas Dataframe with an Excel Interface"
    }
)
st.title('Python Script Generator Demo')

st.markdown("""
This app allows you to **manipulate any data** through an intuitive Excel interface and **outputs the corresponding Python scripts** as you go. After importing your data, interact with the spreadsheet as if you’re using Excel, and the app will record your transformation steps, generating the corresponding Python code.

To use the app, follow these steps:
1. Import your data into Streamlit  
2. Use Mitosheet to manipulate and clean the data based on the prompts  
3. Once you're done, download the cleaned data as a CSV file and view the Python scripts for each step
4. Use PyGWalker visualization tools for EDA, as if you are using Tableau

This app is a demo of the Mitosheet library. Learn more [here](https://trymito.io).
""")

@st.cache_data
def load_file(uploaded_file, sep=None, selected_sheet=None):
    file_type = uploaded_file.name.split('.')[-1].lower()

    if file_type == 'csv':
        df = pd.read_csv(uploaded_file)
    elif file_type == 'txt':
        df = pd.read_csv(uploaded_file, sep=sep) if sep else None
        if df is None:
            st.warning("Please provide a valid separator for the TXT file.")
    elif file_type == 'xlsx':
        # Load the Excel file without specifying the sheet
        xls = pd.ExcelFile(uploaded_file, engine='openpyxl')
        df = pd.read_excel(xls, sheet_name=selected_sheet) if selected_sheet else None
    elif file_type == 'parquet':
        df = pd.read_parquet(uploaded_file)
    else:
        df = None
        st.warning(f"Unsupported file format for {uploaded_file.name}. Please upload CSV, TXT, XLSX, or Parquet.")
    
    return df

st.header("Upload files to use MitoSheet")

# File uploader that allows multiple file uploads
uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)

# Check if files have been uploaded
if uploaded_files:
    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith('.xlsx'):
            # Get the sheet names for Excel files
            xls = pd.ExcelFile(uploaded_file, engine='openpyxl')
            sheet_names = xls.sheet_names
            
            # Let the user select a sheet name
            selected_sheet = st.selectbox("Select a sheet name", sheet_names)
        else:
            selected_sheet = None
            
        # Handle separator for TXT files
        if uploaded_file.name.endswith('.txt'):
            sep = st.text_input("Enter the separator for the TXT file (e.g., ',' or '|')", ',')
        else:
            sep = None
        
        # Load the file with the selected options
        df = load_file(uploaded_file, sep=sep, selected_sheet=selected_sheet)
        
        if df is not None:
            # Call the function spreadsheet() if it exists and process the df
            new_dfs, code = spreadsheet(df)
            
            st.write(f"Code Generated")
            st.code(code)

            # Check if new_dfs is a dictionary and process accordingly
            if isinstance(new_dfs, dict):
                st.write(f"Output Dataframe")
                for key, df_temp in new_dfs.items():
                    # st.write(f"DataFrame: {key}")
                    # st.write(df_temp)
                    
                    # Create a button to download the DataFrame as CSV
                    csv = df_temp.to_csv(index=False)
                    st.download_button(
                        label=f"Download {key} as CSV",
                        data=csv,
                        file_name=f'{key}.csv',
                        mime='text/csv'
                    )
            
            # Convert Timestamp columns to string before passing to PyGWalker
            if df_temp.select_dtypes(include=['datetime64']).any().any():
                df_temp = df_temp.copy()
                for col in df_temp.select_dtypes(include=['datetime64']).columns:
                    df_temp[col] = df_temp[col].astype(str)

            # Use PyGwalker for visualization
            st.write("### Visualization:")
            pyg_app = StreamlitRenderer(df_temp)
            pyg_app.explorer()

        else:
            st.info("Interact with the spreadsheet to see code output")
else:
    st.info("Awaiting file upload. Supported formats: CSV, TXT, XLSX, Parquet.")