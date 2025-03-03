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
    
    # Validate WORKFLOW Column (allowing only letters and underscores)
    workflow_pattern = r'^[a-zA-Z_]+$'
    invalid_workflow = df.loc[~df['WORKFLOW'].astype(str).str.match(workflow_pattern), 'WORKFLOW']
    errors.extend([(i, 'WORKFLOW', f"Invalid format ('{workflow}' - only letters and underscores allowed, no spaces or special characters)") for i, workflow in invalid_workflow.items()])
    
    # Validate Quantity Column
    invalid_quantity = ~df['QUANTITY'].astype(str).str.match(r'^\d+$')
    errors.extend([(i, 'QUANTITY', 'Invalid format (integer expected)') for i in df.index[invalid_quantity]])
    
    return errors

def main():
    st.title("Alki Predict - CSV Format Validator")
    st.write("Upload a small portion of your CSV file to check formatting before sending the full file.")
    
    # Display data compliance rules
    st.subheader("Data Compliance Rules")
    st.write("""
    To ensure your CSV file meets Alki's data format requirements, please follow these rules:
    - **DATE**: Must be in `YYYY-MM-DD` format (e.g., 2025-03-03).
    - **WORKFLOW**: Must contain only uppercase/lowercase letters and underscores (`_`). Spaces and special characters are not allowed.
    - **QUANTITY**: Must be an integer (whole number). Decimal values are not accepted.
    - The CSV file should have exactly **three columns** with headers: `DATE`, `WORKFLOW`, and `QUANTITY`.
    - Allowed delimiters: `,` or `;`.
    """)

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
                st.dataframe(error_df)
                
                # Provide a downloadable error report
                output = io.BytesIO()
                error_df.to_csv(output, index=False, encoding='utf-8')
                output.seek(0)
                st.download_button("Download Error Report", output, "error_report.csv", "text/csv")
            else:
                st.success("No errors found. Your file is correctly formatted!")
        
        except Exception as e:
            st.error(f"An error occurred: {e}")
            
if __name__ == "__main__":
    main()
