import os
import requests
import zipfile
from tqdm import tqdm
import time

def download_cuad_dataset(data_dir="data/raw/cuad"):
    """
    Downloads and extracts the CUAD dataset with enhanced error handling.
    """
    if os.path.exists(data_dir):
        print(f"Directory '{data_dir}' already exists. Please delete it to re-download.")
        # To be safe, let's check if it's empty
        if not os.listdir(data_dir):
             print(f"Directory is empty. Deleting it now.")
             os.rmdir(data_dir)
        else:
            return # Exit if the directory exists and is not empty

    print("Directory does not exist. Proceeding with download.")
    os.makedirs(data_dir, exist_ok=True)


    url = "https://zenodo.org/record/4595826/files/CUAD_v1.zip"
    zip_path = "CUAD_v1.zip"

    try:
        print(f"Attempting to download file from: {url}")
        response = requests.get(url, stream=True, timeout=30) # Added timeout
        response.raise_for_status()  # This will raise an error for bad responses (4xx or 5xx)

    except requests.exceptions.RequestException as e:
        print("\n!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!")
        print(f"A network error occurred: {e}")
        print("This could be a firewall, proxy, or internet connection issue.")
        print("Please check your network settings and try again.")
        return # Stop execution

    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024

    print("Download started...")
    with open(zip_path, "wb") as f, tqdm(
        total=total_size, unit="iB", unit_scale=True, desc="Downloading CUAD_v1.zip"
    ) as bar:
        for data in response.iter_content(block_size):
            bar.update(len(data))
            f.write(data)

    if total_size != 0 and os.path.getsize(zip_path) < total_size:
         print("ERROR: Download did not complete. The downloaded file is smaller than expected.")
         return

    print("\nExtracting CUAD dataset...")
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(data_dir)
        os.remove(zip_path)
        print("CUAD dataset downloaded and extracted successfully.")
    except zipfile.BadZipFile:
        print("\n!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!")
        print("Failed to extract. The downloaded file is not a valid zip file, which suggests the download was corrupted or incomplete.")

if __name__ == "__main__":
    download_cuad_dataset()
