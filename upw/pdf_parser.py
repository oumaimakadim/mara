import pdfplumber
import pandas as pd
import re

class PDFParser:
    def __init__(self):
        pass

    def parse(self, file_path):
        """
        Parses the PDF file and extracts metadata and tables.
        
        Args:
            file_path (str): Path to the PDF file.
            
        Returns:
            dict: A dictionary containing 'metadata' (dict) and 'tables' (list of DataFrames).
        """
        result = {
            "metadata": {},
            "tables": []
        }
        
        try:
            with pdfplumber.open(file_path) as pdf:
                # 1. Extract Metadata (Generic approach)
                # We'll try to get some basic info from the first page
                if len(pdf.pages) > 0:
                    first_page_text = pdf.pages[0].extract_text()
                    result["metadata"] = self._extract_metadata_from_text(first_page_text)
                
                # 2. Extract Tables
                # We will iterate through all pages and extract tables
                for page in pdf.pages:
                    extracted_tables = page.extract_tables()
                    for table in extracted_tables:
                        # Convert to DataFrame
                        # We assume the first row is the header, but we'll clean it up
                        if table:
                            df = pd.DataFrame(table[1:], columns=table[0])
                            # Basic cleaning: remove empty rows/cols if needed
                            df = df.dropna(how='all').dropna(axis=1, how='all')
                            result["tables"].append(df)
                            
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return None
            
        return result

    def _extract_metadata_from_text(self, text):
        """
        Extracts metadata from text using regex or simple parsing.
        This is a placeholder/generic implementation.
        """
        metadata = {}
        if not text:
            return metadata
            
        # Example: Try to find something that looks like a date
        date_match = re.search(r'\d{2}[/-]\d{2}[/-]\d{4}', text)
        if date_match:
            metadata['Date'] = date_match.group(0)
            
        # Example: Try to find something that looks like an account number
        # (Generic pattern, might need adjustment)
        acc_match = re.search(r'Account\s*No\.?\s*[:#]?\s*(\d+)', text, re.IGNORECASE)
        if acc_match:
            metadata['Account Number'] = acc_match.group(1)
            
        # Just store the first few lines as "Header Info" if nothing else found
        lines = text.split('\n')
        if lines:
            metadata['Header Title'] = lines[0].strip()
            
        return metadata
