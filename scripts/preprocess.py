import pandas as pd
import os
import pdfplumber
from tqdm import tqdm

def find_data_path(root_dir="data/raw/cuad/CUAD_v1"):
    """
    Finds the correct path for the CUAD dataset files.
    It checks for both 'CUAD_v1' and direct extraction scenarios.
    Returns the path to the directory containing the files.
    """
    # Path 1: Standard extraction (e.g., data/raw/cuad/CUAD_v1/)
    path1 = os.path.join(root_dir, "CUAD_v1")
    if os.path.exists(path1) and 'master_clauses.csv' in os.listdir(path1):
        print(f"Dataset found in: {path1}")
        return path1

    # Path 2: Direct extraction (e.g., data/raw/cuad/)
    if os.path.exists(root_dir) and 'master_clauses.csv' in os.listdir(root_dir):
        print(f"Dataset found in: {root_dir}")
        return root_dir

    # If neither path is valid
    return None

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a single PDF file, handling potential errors.
    """
    text = ""
    if not os.path.exists(pdf_path):
        # print(f"Warning: PDF file not found at {pdf_path}")
        return text

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {e}")
        return "" # Return empty string if PDF is corrupt or unreadable

def preprocess_text(text):
    """
    Cleans and normalizes text.
    - Replaces multiple whitespace characters with a single space.
    - Removes leading/trailing whitespace.
    """
    text = " ".join(text.split())
    return text.strip()


def load_and_process_cuad():
    """
    Loads the CUAD master CSV, finds contract texts from PDFs,
    and returns a processed DataFrame.
    """
    data_path = find_data_path()
    if data_path is None:
        print("\n!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!")
        print("CUAD dataset not found.")
        print("Please make sure you have successfully run 'python scripts/data_collection.py' first.")
        return None

    csv_path = os.path.join(data_path, "master_clauses.csv")
    df = pd.read_csv(csv_path)

    # The PDF files are in a subfolder named "full_contract_txt"
    contracts_dir = os.path.join(data_path, "full_contract_txt")

    print("\nExtracting text from all contract PDFs... (This may take a while)")
    
    # Use tqdm to show a progress bar
    tqdm.pandas(desc="Processing contracts")
    
    # Create the full path to the PDF and then extract text
    df['pdf_path'] = df['Filename'].apply(lambda f: os.path.join(contracts_dir, f))
    df['contract_text'] = df['pdf_path'].progress_apply(extract_text_from_pdf)

    print("\nCleaning and normalizing contract text...")
    df['cleaned_text'] = df['contract_text'].progress_apply(preprocess_text)
    
    # Save the processed data for faster loading next time
    processed_dir = "data/processed"
    os.makedirs(processed_dir, exist_ok=True)
    output_path = os.path.join(processed_dir, "processed_contracts.csv")
    df.to_csv(output_path, index=False)
    
    print(f"\nPreprocessing complete. Processed data saved to: {output_path}")
    return df


if __name__ == "__main__":
    print("Starting preprocessing...")
    cuad_df = load_and_process_cuad()
    if cuad_df is not None:
        print("\n--- Preprocessing Summary ---")
        print(f"Successfully processed {len(cuad_df)} documents.")
        # Print info on a sample contract
        print("\nExample of processed data (first contract):")
        pd.set_option('display.max_colwidth', 100) # Show more text
        print(cuad_df[['Filename', 'cleaned_text']].head(1))
