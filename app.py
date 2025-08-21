import streamlit as st
import requests

# Set a title for the app
st.title("📄 Open-Source Legal LLM Analyzer")

# --- UI Setup ---
st.info(
    "This tool uses open-source language models to analyze legal documents. "
    "Upload a document, and it will perform risk analysis, summarization, and clause extraction."
)

st.sidebar.header("How to Use")
st.sidebar.write("1. **Upload a document** in .txt format.")
st.sidebar.write("2. Click the **Analyze Document** button.")
st.sidebar.write(
    "3. **Wait for the analysis.** This can take several minutes for long documents, "
    "as the AI models are running on a CPU."
)
st.sidebar.warning(
    "**Note:** This is a demonstration tool. Do not upload sensitive or confidential documents."
)


# File uploader widget
uploaded_file = st.file_uploader("Upload your legal document (.txt file)", type=["txt"])

# --- Main Logic ---
if uploaded_file is not None:
    # Read the text from the uploaded file
    try:
        document_text = uploaded_file.read().decode("utf-8")
        st.text_area("Document Content", document_text, height=250)
    except Exception as e:
        st.error(f"Error reading or decoding the file: {e}")
        document_text = None

    if document_text and st.button("Analyze Document"):
        # Display a spinner while the analysis is in progress
        with st.spinner("Analyzing document... Please wait. This can take several minutes for large files..."):
            try:
                # --- FIX: Added a long timeout to prevent the 'Read timed out' error ---
                # Sets a 10-minute (600 seconds) timeout for the request
                response = requests.post(
                    "http://127.0.0.1:8000/analyze",
                    json={"text": document_text},
                    timeout=600
                )

                # Check if the request was successful
                if response.status_code == 200:
                    results = response.json()
                    st.success("Analysis Complete!")

                    # Display the results in a structured way
                    st.subheader("Risk Assessment")
                    risk = results.get("risk_assessment", "Not available")
                    if risk == "High Risk":
                        st.error(f"**{risk}**")
                    elif risk == "Medium Risk":
                        st.warning(f"**{risk}**")
                    else:
                        st.success(f"**{risk}**")

                    st.subheader("Executive Summary")
                    st.write(results.get("summary", "Summary could not be generated."))

                    st.subheader("Extracted Clauses & Entities")
                    st.write("The model identified the following entities in the document:")
                    # Displaying entities in a more readable format
                    entities = results.get("extracted_clauses", [])
                    if entities:
                        st.table(entities)
                    else:
                        st.write("No specific entities were extracted.")

                else:
                    # Show a user-friendly error if the server returned a non-200 status
                    st.error(f"Analysis failed. The server responded with status code: {response.status_code}")
                    st.json(response.text) # Show the server's error message

            except requests.exceptions.Timeout:
                st.error(
                    "Analysis timed out. The document is too long for the server to process "
                    "within the time limit (10 minutes). Try a smaller document or a faster model."
                )
            except requests.exceptions.RequestException as e:
                # Catch other potential connection errors (e.g., server not running)
                st.error(f"Failed to connect to the analysis server: {e}")