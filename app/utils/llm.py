import requests
import logging

def process_with_llm(data):
    # URL del LLM (Hugging Face API endpoint)
    llm_url = "https://api-inference.huggingface.co/models/gpt2"  # Example model

    # Your Hugging Face API token
    api_token = "your_huggingface_api_token"

    # Asegúrate de que los datos sean un formato adecuado para el LLM
    llm_data = {
        "inputs": data  # Enviar la tabla de transcripciones
    }

    headers = {
        "Authorization": f"Bearer {api_token}"
    }

    try:
        # Enviar los datos al LLM
        response = requests.post(llm_url, headers=headers, json=llm_data)
        response.raise_for_status()  # Raise an HTTPError for bad responses
    except requests.exceptions.RequestException as e:
        logging.error(f"Error al procesar con LLM: {e}")
        return {'error': str(e)}

    llm_response = response.json()

    # Custom logic for Rorschach analysis
    analysis = perform_rorschach_analysis(llm_response)
    return analysis

def perform_rorschach_analysis(llm_response):
    # Custom logic to analyze the LLM response for Rorschach analysis
    analysis = {}
    for lamina, transcription in llm_response.items():
        # Example logic: Count the number of positive and negative words
        positive_words = ["happy", "joy", "love"]
        negative_words = ["sad", "anger", "hate"]
        positive_count = sum(word in transcription for word in positive_words)
        negative_count = sum(word in transcription for word in negative_words)
        analysis[lamina] = {
            "positive_count": positive_count,
            "negative_count": negative_count,
            "analysis": "Positive" if positive_count > negative_count else "Negative"
        }
    return analysis
