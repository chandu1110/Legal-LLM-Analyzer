# Legal Document Analysis LLM

This project develops an open-source-based Large Language Model (LLM) for the automated analysis of legal documents. The goal is to provide a robust, scalable, and modular solution for tasks such as clause extraction, summarization, and risk assessment, generating actionable insights for legal professionals.

## Key Features

  * **Clause Extraction:** Uses a fine-tuned Named Entity Recognition (NER) model to identify and extract critical clauses from legal documents.
  * **Document Summarization:** Provides concise, accurate summaries of lengthy legal texts.
  * **Risk Analysis:** Classifies clauses based on a risk score, helping to flag ambiguous or potentially high-risk provisions.
  * **Open-Source First:** Built entirely using open-source tools and resources, including Hugging Face models and libraries.
  * **Scalable Architecture:** Designed with modularity in mind, allowing for easy integration of new features or models.

## Project Structure

```
legal_llm_project/
├── data/
│   ├── processed/          # Cleaned and labeled data
│   │   └── processed_contracts.csv
│   └── raw/                # Raw, unprocessed datasets
│       └── cuad/           # CUAD dataset will be downloaded here
├── scripts/
│   ├── data_collection.py  # Script for downloading the CUAD dataset
│   ├── preprocess.py       # Script for data cleaning and labeling
│   └── train.py            # Script for fine-tuning the LLM
├── src/
│   ├── __pycache__/
│   ├── app.py              # Streamlit user interface
│   ├── main.py             # FastAPI application
│   └── models.py           # Model loading and inference logic
├── tests/
│   └── test_api.py         # Test cases for the FastAPI
├── .gitignore
├── README.md
└── requirements.txt
```

## Data

The foundation of our Legal Document Analysis LLM is a high-quality, specialized legal dataset. We use the **CUAD (Contract Understanding Atticus Dataset)**, a widely recognized open-source dataset for legal NLP tasks.

### About the CUAD Dataset

The CUAD dataset is a collection of over **500 commercial contracts** that have been manually annotated by legal experts. These annotations are specifically designed for **clause extraction** and **named entity recognition (NER)**, making it an ideal resource for our model's fine-tuning.

### Data Acquisition

To ensure reproducibility and ease of setup, our project includes a script to automatically download and prepare the CUAD dataset. The dataset is sourced from its official public repository. The provided script `scripts/data_collection.py` handles the entire process:

1.  **Downloads** the `CUAD_v1.zip` file from the Zenodo repository (`https://zenodo.org/record/4595826/files/CUAD_v1.zip`).
2.  **Verifies** the download integrity to prevent issues with incomplete or corrupted files.
3.  **Extracts** the contents into the `data/raw/cuad` directory.
4.  **Cleans up** the downloaded zip file after successful extraction.

#### Running the Data Download Script

To get started, simply run the following command from the project's root directory:

```bash
python scripts/data_collection.py
```

This will automatically create the necessary directory structure and download the dataset, preparing it for the data cleaning and preprocessing stages.

## Getting Started

### Prerequisites

  * Python 3.8+
  * `pip` package manager

### Installation

1.  Clone the repository:
    ```sh
    git clone https://github.com/your-username/legal-llm-project.git
    cd legal-llm-project
    ```
2.  Create a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3.  Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

### Data Preparation

After downloading the raw data, you need to preprocess and label it for model training. The `scripts/preprocess.py` file is responsible for this step.

  * **Cleaning:** It will handle text extraction from PDFs, normalization, and anonymization of sensitive data.
  * **Labeling:** It will format the data appropriately for NER, summarization, and classification tasks.
  * Run the preprocessing script:
    ```bash
    python scripts/preprocess.py
    ```
    This will generate the `data/processed/processed_contracts.csv` file, which is ready for model training.

### Model Training

Fine-tuning is performed on pre-trained models from the Hugging Face Hub. The `scripts/train.py` file handles the training pipeline.

  * **Models:** We will use **LegalBERT** for NER and risk classification, and a fine-tuned **T5** model for summarization.
  * **Training:**
      * Execute the training script: `python scripts/train.py`.
      * This script will load the processed data and fine-tune the selected models for each task. The trained models will be saved in the `data/models` directory.

### Deployment

The trained model can be served via a REST API and a user-friendly UI.

  * **API (FastAPI):**

      * Navigate to the `src` directory.
      * Run the FastAPI server: `uvicorn main:app --reload`
      * The API documentation will be available at `http://127.0.0.1:8000/docs`.

  * **User Interface (Streamlit):**

      * Navigate to the `src` directory.
      * Launch the Streamlit app: `streamlit run app.py`
      * This will open a local web page in your browser where you can upload a legal document and see the analysis results.

## Evaluation

The model's performance is evaluated using standard metrics.

  * **NER:** Precision, Recall, F1-Score.
  * **Summarization:** ROUGE scores.
  * **Classification:** Accuracy, F1-Score.

Refer to the `tests/` directory for the evaluation scripts.

## Challenges & Future Improvements

  * **Data Scarcity:** Access to a diverse range of high-quality, labeled legal documents remains a significant challenge.
  * **Domain-Specific Nuances:** Legal language is highly contextual. The model's accuracy can be improved by training on more granular, domain-specific data.
  * **Future Work:**
      * Expand multilingual support to include more languages.
      * Add support for more complex document types (e.g., litigation documents, patents).
      * Implement an active learning pipeline to continuously improve the model with new data.

## License

This project is licensed under the MIT License.
