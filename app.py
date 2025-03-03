import streamlit as st
import pandas as pd
import re
import io

def validate_data(df):
    errors = []
    
    # Validate Date Column
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    invalid_dates = ~df['DATE'].astype(str).str.match(date_pattern)
    errors.extend([(i, 'DATE', 'Invalid format (YYYY-MM-DD expected)') for i in df.index[invalid_dates]])
    
    # Validate WORKFLOW Column
    workflow_pattern = r'^[a-zA-Z]+$'
    invalid_workflow = df.loc[~df['WORKFLOW'].astype(str).str.match(workflow_pattern), 'WORKFLOW']
    errors.extend([(i, 'WORKFLOW', f"Invalid format ('{workflow}' - only letters, no spaces or special characters)") for i, workflow in invalid_workflow.items()])
    
    # Validate Quantity Column
    invalid_quantity = ~df['QUANTITY'].astype(str).str.match(r'^\d+$')
    errors.extend([(i, 'QUANTITY', 'Invalid format (integer expected)') for i in df.index[invalid_quantity]])
    
    return errors

def main():
    st.title("ALKI PREDICT - CSV Format Validator")
    st.write("Upload a small portion of your CSV file to check formatting before sending the full file.")
    
    uploaded_file = st.file_uploader("Drag and drop a CSV file", type=["csv"])
    
    if uploaded_file is not None:
        try:
            # Try reading the CSV with different delimiters
            for sep in [',', ';']:
                uploaded_file.seek(0)  # Reset file pointer
                df = pd.read_csv(uploaded_file, sep=sep)
                if list(df.columns) == ['DATE', 'WORKFLOW', 'QUANTITY']:
                    break
            else:
                st.error("Incorrect column names. Expected: ['DATE', 'WORKFLOW', 'QUANTITY']")
                return
            
            errors = validate_data(df)
            
            if errors:
                error_df = pd.DataFrame(errors, columns=['Row', 'Column', 'Error'])
                st.error("Errors detected in the file. Please review them below.")
                st.dataframe(error_df)w
                
                # Provide a downloadable error report
                output = io.StringIO()
                error_df.to_csv(output, index=False)
                output.seek(0)
                st.download_button("Download Error Report", output, "error_report.csv", "text/csv")
            else:
                st.success("No errors found. Your file is correctly formatted!")
        
        except Exception as e:
            st.error(f"An error occurred: {e}")
            
if __name__ == "__main__":
    main()