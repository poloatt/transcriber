import logging
import warnings
from transformers import pipeline

# Silence the specific FutureWarning from huggingface_hub
warnings.filterwarnings('ignore', category=FutureWarning, 
                       message='`resume_download` is deprecated')

# Initialize the Hugging Face pipeline for emotion analysis
emotion_analysis_pipeline = pipeline("text-classification", 
                                  model="finiteautomata/beto-emotion-analysis",
                                  use_auth_token=False)

def process_with_llm(data):
    # Ensure that data is in the correct format (text for emotion analysis)
    texts = [f"Lámina {i+1}: {response}" for i, response in enumerate(data.values())]

    try:
        # Log the request data for debugging
        logging.debug(f"Sending texts to LLM: {texts}")

        # Use the pipeline to analyze the texts
        llm_response = emotion_analysis_pipeline(texts)

        # Log the response for debugging
        logging.debug(f"LLM response: {llm_response}")
    except Exception as e:
        logging.error(f"Error processing with LLM: {e}")
        return {'error': str(e)}

    # Custom logic for Rorschach analysis based on emotion analysis results
    analysis = perform_rorschach_analysis(llm_response)
    return analysis


def perform_rorschach_analysis(llm_response):
    # Custom logic to analyze the LLM response for Rorschach analysis
    analysis = {}
    
    # Loop through the response to analyze each transcription
    for i, result in enumerate(llm_response):
        lamina = f"Lámina {i+1}"
        # Example logic to check the emotion label (adjust to fit your model's output)
        emotions = result.get("label", "")  # Replace with your model's actual label field
        analysis[lamina] = {
            "emotion": emotions,  # Store detected emotion for the transcription
            "analysis": "Positive" if "joy" in emotions else "Negative"  # Example categorization
        }
    
    return analysis
