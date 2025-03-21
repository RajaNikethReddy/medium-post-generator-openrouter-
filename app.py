import os
import requests
import json
from typing import List, Optional
from dotenv import load_dotenv

class GPTBot:
    def __init__(self, system_prompt: str = None):
        # Load environment variables
        load_dotenv()
        
        # Set default system prompt if none provided
        default_prompt = """You are a helpful AI assistant. You provide clear, accurate, and helpful responses.
        When working with documents, you analyze them carefully and provide insights based on their content.
        If you're unsure about something, you acknowledge the uncertainty."""
        
        self.system_prompt = system_prompt if system_prompt else default_prompt
        
        # Initialize messages (system prompt goes in messages)
        self.messages = [{"role": "system", "content": self.system_prompt}]
        self.loaded_documents = {}
        
        # OpenRouter configuration
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.getenv('YOUR_SITE_URL', 'https://yoursite.com'),  # Replace with your actual site
            "X-Title": os.getenv('YOUR_SITE_NAME', 'Your Site Name'),  # Replace with your actual site name
        }
        
    def load_document(self, file_path: str) -> bool:
        """Load a document from file system."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                filename = os.path.basename(file_path)
                content = file.read()
                self.loaded_documents[filename] = content
                
                # Add document context to messages
                self.messages.append({
                    "role": "user",
                    "content": f"I'm sharing a document with you. Filename: {filename}\nContent: {content}"
                })
                self.messages.append({
                    "role": "assistant",
                    "content": f"I've received the document '{filename}' and will consider its contents in our conversation."
                })
                return True
        except Exception as e:
            print(f"Error loading document: {e}")
            return False
            
    def generate_response(self, user_input: str) -> str:
        """Generate response using OpenRouter API."""
        try:
            # Add user message to history
            self.messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Create the payload for OpenRouter
            payload = {
                "model": "google/gemini-2.0-flash-lite-preview-02-05:free",  # Using the Gemini model from your example
                "messages": self.messages,
                "max_tokens": 8024
            }
            
            # Make the API request
            response = requests.post(
                url=self.api_url,
                headers=self.headers,
                data=json.dumps(payload)
            )
            
            # Process the response
            response_data = response.json()
            response_text = response_data['choices'][0]['message']['content']
            
            # Add assistant's response to history
            self.messages.append({
                "role": "assistant",
                "content": response_text
            })
            
            return response_text
        except Exception as e:
            return f"Error generating response: {e}"
            
    def chat(self):
        """Main chat loop."""
        print("GPTBot: Hello! I'm ready to help. You can:")
        print("- Chat normally")
        print("- Type 'load file: <path>' to load a document")
        print("- Type 'exit' to end the conversation")
        print("- Type 'system prompt: <new prompt>' to update the system prompt")
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'exit':
                break
                
            if user_input.lower().startswith('load file:'):
                file_path = user_input[10:].strip()
                if self.load_document(file_path):
                    print(f"GPTBot: Successfully loaded {os.path.basename(file_path)}")
                continue
            
            if user_input.lower().startswith('system prompt:'):
                new_prompt = user_input[13:].strip()
                self.system_prompt = new_prompt
                # Reset messages with new system prompt
                self.messages = [{"role": "system", "content": self.system_prompt}]
                print("GPTBot: System prompt updated. Conversation history cleared.")
                continue
                
            response = self.generate_response(user_input)
            print(f"\nGPTBot: {response}")

if __name__ == "__main__":
    custom_prompt = """Here's the corrected version with proper grammar and clarity: 
---
You're John, who writes Medium posts on Medium, and I want you to act as an assistant to John. Your task is to adapt John's writing style based on the Medium articles I provide. 
### Key Characteristics of John's Writing: 
- John is widely known for his simple and easy-to-understand writing style. 
- His writing has a smooth flow, making it highly engaging. 
- Once a reader starts his article, they won't stop until they finish it. 
### What You Should NOT Do: 
- Do not hallucinate or create different structures that deviate from John's style. 
- Do not use complex, salesy words or overused AI-generated phrases like *"delve,"* *"kickoff,"* *"picture this:"* and so on. 
### What You Should Do: 
- Understand and replicate John's writing style. 
- Write Medium posts in the **first person**, documenting what John is working on rather than portraying him as an expert. 
- Use simple, everyday language instead of technical jargon. 
### Understanding the Psychology Behind Medium Posts: 
- The posts should feel like personal experiences rather than tutorials. 
- Come up with a strong **title** and an engaging **tone**, as they are crucial for attracting readers. 
I will provide examples of John's Medium posts in the [draft].
    """
    
    bot = GPTBot(system_prompt=custom_prompt)
    # Or use default prompt: bot = GPTBot()
    bot.chat()