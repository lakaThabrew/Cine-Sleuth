import os
import re
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from datetime import datetime

class CineSleuthError(Exception):
    pass
class APIKeyError(CineSleuthError):
    pass
class APIConnectionError(CineSleuthError):
    pass
class APIQuotaError(CineSleuthError):
    pass
class AllKeysExhaustedError(CineSleuthError):
    pass

# Global API key manager
class APIKeyManager:  
    def __init__(self):
        self.keys = []
        self.current_index = 0
        self.exhausted_keys = set()
    
    def load_keys(self):
        load_dotenv()
        No_of_keys = int(os.getenv("NO_of_keys", 1))
        primary_key = os.getenv("GEMINI_API_KEY")
        if primary_key:
            self.keys.append(("GEMINI_API_KEY", primary_key))
        
        # Load backup keys (GEMINI_API_KEY_2, GEMINI_API_KEY_3, etc.)
        for i in range(2, No_of_keys + 1):
            key = os.getenv(f"GEMINI_API_KEY_{i}")
            if key:
                self.keys.append((f"GEMINI_API_KEY_{i}", key))
        
        if not self.keys:
            raise APIKeyError("No API keys found. Please set GEMINI_API_KEY in your .env file.")
        
        print(f"🔑 Loaded {len(self.keys)} API key(s)")
        return self.get_current_key()
    
    def get_current_key(self):
        if self.current_index >= len(self.keys):
            raise AllKeysExhaustedError("All API keys have been exhausted. Please add more keys or wait for quota reset.")
        return self.keys[self.current_index][1]
    
    def get_current_key_name(self):
        if self.current_index >= len(self.keys):
            return None
        return self.keys[self.current_index][0]
    
    def mark_current_exhausted(self):
        if self.current_index < len(self.keys):
            key_name = self.keys[self.current_index][0]
            self.exhausted_keys.add(key_name)
            print(f"⚠️ API key '{key_name}' quota exceeded.")
        
        self.current_index += 1
        
        if self.current_index < len(self.keys):
            new_key_name = self.keys[self.current_index][0]
            print(f"🔄 Switching to backup key: {new_key_name}")
            return self.get_current_key()
        else:
            raise AllKeysExhaustedError("All API keys have been exhausted. Please add more keys or wait for quota reset.")
    
    def has_more_keys(self):
        return self.current_index < len(self.keys) - 1
    
    def reset(self):
        self.current_index = 0
        self.exhausted_keys.clear()


# Global instance
api_key_manager = APIKeyManager()

def clean_output(text):
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def get_yes_no_input(prompt="Please answer 'yes' or 'no' (or type 'exit' to quit): "):
    while True:
        try:
            answer = input(prompt).strip().lower()
            if answer in ['yes', 'no', 'exit']:
                return answer
            print("Please answer 'yes', 'no', or 'exit'.")
        except EOFError:
            return 'exit'
        except KeyboardInterrupt:
            print("\n")
            return 'exit'

def load_api_key():
    return api_key_manager.load_keys()

def configure_api(api_key):
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        raise APIConnectionError(f"Failed to configure API: {e}")

def reconfigure_with_next_key():
    new_key = api_key_manager.mark_current_exhausted()
    configure_api(new_key)
    return new_key

def create_model(model_name='gemini-2.0-flash'):
    try:
        return genai.GenerativeModel(model_name)
    except Exception as e:
        raise APIConnectionError(f"Failed to create model '{model_name}': {e}")

def send_message_safely(chat, prompt, model=None):
    max_retries = len(api_key_manager.keys)
    
    for attempt in range(max_retries):
        try:
            response = chat.send_message(prompt)
            return response
        except google_exceptions.ResourceExhausted:
            if api_key_manager.has_more_keys():
                try:
                    reconfigure_with_next_key()
                    if model:
                        new_model = create_model(model.model_name if hasattr(model, 'model_name') else 'gemini-2.0-flash')
                        new_chat = new_model.start_chat(history=chat.history)
                        return send_message_safely(new_chat, prompt, new_model)
                    continue
                except AllKeysExhaustedError:
                    raise APIQuotaError("All API keys exhausted. Please add more keys to your .env file or wait for quota reset.")
            else:
                raise APIQuotaError("API quota exceeded on all keys. Please add more keys or wait for quota reset.")
        except google_exceptions.InvalidArgument as e:
            raise CineSleuthError(f"Invalid request: {e}")
        except google_exceptions.PermissionDenied:
            raise APIKeyError("Invalid API key or permission denied.")
        except google_exceptions.ServiceUnavailable:
            raise APIConnectionError("Gemini API service is currently unavailable. Please try again later.")
        except Exception as e:
            raise APIConnectionError(f"API error: {e}")
    
    raise APIQuotaError("All API keys exhausted after retries.")


def print_banner():
    print("+" + "-"*68 + "+")
    print("|" + " "*23 + "Welcome to Cine-Sleuth!" + " "*22 + "|")
    print("|" + " "*20 + "Your AI-powered movie detector" + " "*18 + "|")
    print("+" + "-"*68 + "+")
    print("""\nI will ask up to 20 questions to guess 🙃 the movie you're thinking of🎯.
      """)

def write_history(movie, history):
    with open("G:/Projects/CineSleuth/logs/log.txt",'a') as f:
        summary = "\n".join([f"Q: {q} A: {a}" for q, a in history])
        f.write(f"{movie} => \n{summary}")

def writeDate():
    with open("G:/Projects/CineSleuth/logs/log.txt",'a') as f:
        now = datetime.now()
        formatted = now.strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"Date and Time: {formatted}\n")

def main():
    try:
        api_key = load_api_key()
        configure_api(api_key)
        print_banner()

        user_input = input("Type 'start' to begin or 'exit' to quit: ").strip().lower()
        if user_input == 'exit':
            print("👋 Goodbye!")
            return

        model = create_model('gemini-2.0-flash')
        history = []  

        max_questions = 20
        chat = model.start_chat(history=[])
        writeDate()
        for i in range(1, max_questions + 1):
            summary = "\n".join([f"Q: {q} A: {a}" for q, a in history])
            
            prompt = f"""
                        You are a movie-detective AI playing a guessing game. 
                        The user is thinking of a movie.
                        Previous Q&A so far:
                        {summary if summary else 'None'}, and you have only 20 questions in total. You must guess the movie within these questions.
                        Mostly focus the last Q&A in history to narrow down.

                        Ask ONE question to narrow down the movie about its 
                            genre, 
                            Time Period / Release Year, 
                            actors
                            actresses, 
                            director,
                            whether Franchise vs Standalone,
                            Setting,
                            Main Character whether male or female lead,
                            Plot elements,
                            Famous scenes,
                            themes & Tone,
                            Cinematography style,
                            Popularity
                            and plots etc. Output only the question.
                    """
            
            response = send_message_safely(chat, prompt)
            question = clean_output(response.text)
            print(f"\nAI Question {i}: {question}")
            
            answer = input("Your Answer (yes/no or type 'exit' to quit): ").strip().lower()
            if answer == 'exit':
                print("Thanks for playing!")
                break

            history.append((question, answer))
            
            guess_prompt = f"""
                                Based on the following Q&A:
                                {summary if summary else 'None'}. Guess the movie the user is thinking of based on the provided information. 
                                Mostly focus on the last Q&A in history to narrow down and guess the movie.
                                If not confident, say 'I need more questions'. Output only the movie title or the phrase.
                            """
            
            guess_resp = send_message_safely(chat, guess_prompt)
            guess = clean_output(guess_resp.text)
            
            if "need more questions" not in guess.lower():
                print("\nI think your movie:", guess)
                confirm = get_yes_no_input("\nIs this correct? (yes/no): ")
                if confirm == 'yes':
                    print("🎉 I guessed it! Thanks for playing!")
                    print("👋Bye .... Thanks for playing!")
                    history.append(("Final Guess", guess))
                    write_history(guess, history)
                    break           
                    
                else:
                    print("🤷 Hmm, maybe I need more questions...")
        else:
            print("\n🤔 I couldn't guess your movie. You win this time!")
            history.append(("Final Guess", "Could not guess"))
            final_movie = input("💪 What movie were you thinking of? ")
            prompt = f"""
                        The Movie is {final_movie} and Explain why you cannot get and if the details of movie are
                        not match with {"\n".join([f"Q: {q} A: {a}" for q, a in history])}. Jusity or Complain shortly.
                        """
            final_resp = send_message_safely(chat, prompt)
            print("\nAI Response:", clean_output(final_resp.text))
            history.append(("Final Movie", final_movie))
            history.append(("AI Response", clean_output(final_resp.text)))
            print("👋Bye .... Thanks for playing!")
            write_history(final_movie, history)

    except APIKeyError as e:
        print(f"❌ API Key Error: {e}")
    except APIQuotaError as e:
        print(f"❌ Quota Error: {e}")
    except AllKeysExhaustedError as e:
        print(f"❌ All Keys Exhausted: {e}")
    except APIConnectionError as e:
        print(f"❌ Connection Error: {e}")
    except CineSleuthError as e:
        print(f"❌ Error: {e}")
    except KeyboardInterrupt:
        print("\n👋 Game interrupted. Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
