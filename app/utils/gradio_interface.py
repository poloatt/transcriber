import gradio as gr

def greet(name):
    return "Hello " + name + "!!"

def process_transcriptions(transcriptions):
    # Custom logic to process transcriptions
    return {lamina: f"Processed {text}" for lamina, text in transcriptions.items()}

demo = gr.Interface(fn=process_transcriptions, inputs="json", outputs="json")
demo.launch()