import logging
import sys
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Python path: {sys.path}")
logger.debug(f"Current working directory: {os.getcwd()}")

try:
    from transformers import pipeline
    logger.debug("Successfully imported transformers")
except ImportError as e:
    logger.error(f"Error importing transformers: {e}")
    logger.error(f"Python executable: {sys.executable}")
    logger.error(f"Python version: {sys.version}")
    raise ImportError("Please ensure transformers is installed in your environment")

# Initialize the Hugging Face pipeline for emotion analysis
emotion_analysis_pipeline = pipeline("text-classification", model="finiteautomata/beto-emotion-analysis")

def process_with_llm(data):
    # Ensure that data is in the correct format (text for emotion analysis)
    texts = [f"Lámina {i+1}: {response}" for i, response in enumerate(data.values())]

    try:
        # Log the request data for debugging
        logger.debug(f"Sending texts to LLM: {texts}")

        # Use the pipeline to analyze the texts
        llm_response = emotion_analysis_pipeline(texts)

        # Log the response for debugging
        logger.debug(f"LLM response: {llm_response}")
    except Exception as e:
        logger.error(f"Error processing with LLM: {e}")
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
