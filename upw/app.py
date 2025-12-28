import streamlit as st
import pandas as pd
from upw.pdf_parser import PDFParser
import tempfile
import os

st.set_page_config(page_title="Bank Statement Parser", layout="wide")

st.title("Bank Statement PDF Parser")
st.markdown("""
Upload a bank statement PDF to extract metadata and transaction tables.
**Note:** This is a generic parser. Results may vary depending on the PDF layout.
""")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Save uploaded file to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    st.info(f"Processing {uploaded_file.name}...")
    
    parser = PDFParser()
    result = parser.parse(tmp_file_path)
    
    # Clean up temp file
    os.remove(tmp_file_path)
    
    if result:
        st.success("Parsing complete!")
        
        # Display Metadata
        st.subheader("Extracted Metadata")
        if result["metadata"]:
            st.json(result["metadata"])
        else:
            st.warning("No specific metadata found.")
            
        # Display Tables
        st.subheader("Extracted Tables")
        if result["tables"]:
            for i, df in enumerate(result["tables"]):
                st.write(f"### Table {i+1}")
                st.dataframe(df)
                
                # CSV Download
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"Download Table {i+1} as CSV",
                    data=csv,
                    file_name=f"table_{i+1}.csv",
                    mime="text/csv",
                )
        else:
            st.warning("No tables found in the PDF.")
            
    else:
        st.error("Failed to parse the PDF.")
