import os
import pandas as pd
from typing import List, Dict, Optional
from src.pdf_processor import PDFProcessor
from src.metadata_fetcher import MetadataFetcher
from src.endnote_writer import EndNoteWriter

class LibraryGenerator:
    """
    Main controller class for generating EndNote libraries from PDFs.
    """

    def __init__(self, email: str = "agent@example.com"):
        self.pdf_processor = PDFProcessor()
        self.metadata_fetcher = MetadataFetcher(email)
        self.endnote_writer = EndNoteWriter()
        self.results_df = pd.DataFrame()

    def process_directory(self, folder_path: str) -> pd.DataFrame:
        """
        Scans a directory for PDFs, fetches metadata, and returns a DataFrame.
        """
        print(f"Scanning directory: {folder_path}...")
        
        # 1. Find DOIs
        file_doi_map = self.pdf_processor.process_directory(folder_path)
        
        records = []
        
        print(f"Found {len(file_doi_map)} PDFs. processing...")
        
        for file_path, doi in file_doi_map.items():
            record = {
                'file_path': file_path,
                'doi': doi,
                'title': None,
                'authors': None,
                'year': None,
                'journal': None,
                'status': 'Pending'
            }
            
            if doi:
                print(f"Fetching metadata for DOI: {doi}")
                metadata = self.metadata_fetcher.fetch_metadata(doi)
                if metadata:
                    record.update(metadata)
                    record['status'] = 'Success'
                else:
                    record['status'] = 'Metadata Not Found'
            else:
                record['status'] = 'DOI Not Found'
                
            records.append(record)
            
        self.results_df = pd.DataFrame(records)
        return self.results_df

    def save_library(self, output_path: str):
        """
        Saves the processed records to an EndNote XML file.
        Only saves records where we have at least some metadata or a file.
        """
        if self.results_df.empty:
            print("No records to save.")
            return

        # Convert DF back to list of dicts
        # Sanitize: Replace NaN with None so XML serialier doesn't crash
        df_clean = self.results_df.where(pd.notnull(self.results_df), None)
        records = df_clean.to_dict('records')
        self.endnote_writer.generate_xml(records, output_path)

    def get_summary_table(self) -> pd.DataFrame:
        return self.results_df
