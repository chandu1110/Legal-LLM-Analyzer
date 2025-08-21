from transformers import pipeline
import torch

class LegalAnalyzer:
    def __init__(self, ner_model_path="dslim/bert-base-NER", summarization_model_path="t5-base"):
        """
        Initializes the LegalAnalyzer with pre-trained models.
        """
        print("Loading models... This may take a moment.")
        # Determine device (use GPU if available)
        device = 0 if torch.cuda.is_available() else -1
        
        self.ner_pipeline = pipeline("ner", model=ner_model_path, device=device)
        self.summarizer_pipeline = pipeline("summarization", model=summarization_model_path, device=device)
        print("Models loaded successfully.")


    def extract_clauses(self, text: str, chunk_size: int = 512):
        """
        Extracts named entities from a legal document by chunking it.
        """
        print("Extracting clauses by chunking document...")
        tokens = text.split()
        all_entities = []

        # Process the text in overlapping chunks to maintain context at boundaries
        for i in range(0, len(tokens), chunk_size - 50): # -50 for overlap
            chunk = " ".join(tokens[i:i + chunk_size])
            if not chunk:
                continue

            # Process with the NER pipeline
            chunk_entities = self.ner_pipeline(chunk)
            
            # Sanitize the output to convert numpy types to standard python types
            for entity in chunk_entities:
                sanitized_entity = {
                    # --- FIX: Changed 'entity_group' to 'entity' to match the model's output ---
                    "entity": entity['entity'],
                    "score": float(entity['score']), # Convert numpy.float32 to python float
                    "word": entity['word'],
                    "start": entity['start'],
                    "end": entity['end'],
                }
                all_entities.append(sanitized_entity)

        # Basic merging of entities - a more advanced implementation could improve this
        # For now, we'll just return the unique entities found
        unique_entities = [dict(t) for t in {tuple(d.items()) for d in all_entities}]
        return unique_entities


    def summarize_document(self, text: str, max_chunk_length: int = 1024): # Removed fixed max_summary_length
        """
        Generates a summary of a long legal document by summarizing chunks smartly.
        """
        print(f"Summarizing document by splitting into chunks...")
        
        # Split text into chunks that T5 can handle
        chunks = [text[i:i + max_chunk_length] for i in range(0, len(text), max_chunk_length)]
        full_summary = ""
        
        print(f"Summarizing {len(chunks)} chunks...")
        for i, chunk in enumerate(chunks):
            # --- FIX: Dynamic max_length ---
            # For summarization, a good max_length is often about half the input length.
            # We also set a reasonable floor and ceiling.
            chunk_length = len(chunk.split()) # Get number of words in chunk
            
            # Set max_length to be half the chunk length, but no more than 150 and no less than 20.
            dynamic_max_length = min(max(int(chunk_length / 2), 20), 150) 
            # We also set a minimum length to be smaller.
            dynamic_min_length = min(max(int(chunk_length / 4), 5), 30)

            try:
                # Use the new dynamic lengths in the pipeline call
                summary = self.summarizer_pipeline(
                    chunk, 
                    max_length=dynamic_max_length, 
                    min_length=dynamic_min_length, 
                    do_sample=False
                )
                full_summary += summary[0]['summary_text'] + " "
            except Exception as e:
                print(f"Could not summarize chunk {i+1}. Error: {e}")

        return full_summary.strip()

    def analyze_risk(self, text: str) -> str:
        """
        Performs a simple keyword-based risk analysis.
        """
        risky_keywords = ["terminate", "indemnify", "liability", "breach", "default", "waive", "penalty"]
        text_lower = text.lower()
        risk_score = sum(1 for keyword in risky_keywords if keyword in text_lower)
        
        if risk_score > 3:
            return "High Risk"
        elif risk_score > 0:
            return "Medium Risk"
        else:
            return "Low Risk"