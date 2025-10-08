import subprocess
import json
import requests
import streamlit as st
from typing import List, Dict, Any

class OllamaManager:
    def __init__(self, host="http://localhost:11434"):
        self.host = host
        self.available_models = []
        self.current_model = "llama2"  # Default model
        self.is_available = False
        self.check_ollama_availability()
    
    def check_ollama_availability(self) -> bool:
        """Check if Ollama is running and get available models"""
        try:
            response = requests.get(f"{self.host}/api/tags")
            if response.status_code == 200:
                self.is_available = True
                data = response.json()
                self.available_models = [model['name'] for model in data.get('models', [])]
                st.success(f"✅ Ollama is running! Available models: {len(self.available_models)}")
                return True
            else:
                st.warning("⚠️ Ollama is not responding properly")
                return False
        except Exception as e:
            st.warning(f"⚠️ Ollama is not available: {e}")
            self.is_available = False
            return False
    
    def pull_model(self, model_name: str) -> bool:
        """Pull a model if not available"""
        try:
            if model_name in self.available_models:
                st.info(f"✅ Model '{model_name}' is already available")
                return True
            
            st.info(f"🔄 Pulling model '{model_name}'... This may take a while.")
            
            # Use subprocess to run ollama pull command
            result = subprocess.run(
                ["ollama", "pull", model_name],
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode == 0:
                st.success(f"✅ Successfully pulled model '{model_name}'")
                self.available_models.append(model_name)
                return True
            else:
                st.error(f"❌ Failed to pull model: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            st.error("❌ Model pull timed out. Please try again.")
            return False
        except Exception as e:
            st.error(f"❌ Error pulling model: {e}")
            return False
    
    def generate_response(self, prompt: str, model: str = None, system_prompt: str = None, 
                         max_tokens: int = 500, temperature: float = 0.7) -> str:
        """Generate response using Ollama"""
        if not self.is_available:
            return "Ollama is not available. Please make sure Ollama is running."
        
        model_to_use = model or self.current_model
        
        if model_to_use not in self.available_models:
            return f"Model '{model_to_use}' is not available. Available models: {', '.join(self.available_models)}"
        
        try:
            payload = {
                "model": model_to_use,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature,
                    "top_p": 0.9,
                    "stop": ["</s>", "assistant:", "user:"]
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def chat_completion(self, messages: List[Dict[str, str]], model: str = None) -> str:
        """Chat completion with conversation history"""
        if not self.is_available:
            return "Ollama is not available."
        
        model_to_use = model or self.current_model
        
        try:
            payload = {
                "model": model_to_use,
                "messages": messages,
                "stream": False
            }
            
            response = requests.post(
                f"{self.host}/api/chat",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['message']['content'].strip()
            else:
                return f"Error: {response.status_code}"
                
        except Exception as e:
            return f"Error in chat completion: {str(e)}"
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return self.available_models

# Example usage and test
def test_ollama():
    """Test function to verify Ollama setup"""
    manager = OllamaManager()
    
    if manager.is_available:
        st.write("### Available Models:")
        for model in manager.available_models:
            st.write(f"- {model}")
        
        # Test generation
        test_prompt = "Hello, how are you?"
        response = manager.generate_response(test_prompt)
        st.write("### Test Response:")
        st.write(response)
    else:
        st.error("Ollama is not available. Please make sure it's installed and running.")

if __name__ == "__main__":
    test_ollama()