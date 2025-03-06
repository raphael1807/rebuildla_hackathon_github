import gradio as gr
import os
from mistral_agent import PhoenixAssistant

# Initialize the Phoenix Assistant
assistant = PhoenixAssistant()

def respond(message, history):
    """Process user message and return assistant response"""