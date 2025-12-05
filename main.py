import os
import re
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions


class CineSleuthError(Exception):
    pass


class APIKeyError(CineSleuthError):
    pass


class APIConnectionError(CineSleuthError):
    pass


class APIQuotaError(CineSleuthError):
    pass


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
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise APIKeyError("GEMINI_API_KEY environment variable not set. Please set it in your .env file.")
    return api_key


def configure_api(api_key):
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        raise APIConnectionError(f"Failed to configure API: {e}")


def create_model(model_name='gemini-2.0-flash'):
    try:
        return genai.GenerativeModel(model_name)
    except Exception as e:
        raise APIConnectionError(f"Failed to create model '{model_name}': {e}")


def send_message_safely(chat, prompt):
    try:
        response = chat.send_message(prompt)
        return response
    except google_exceptions.ResourceExhausted:
        raise APIQuotaError("API quota exceeded. Please check your billing at https://aistudio.google.com/")
    except google_exceptions.InvalidArgument as e:
        raise CineSleuthError(f"Invalid request: {e}")
    except google_exceptions.PermissionDenied:
        raise APIKeyError("Invalid API key or permission denied.")
    except google_exceptions.ServiceUnavailable:
        raise APIConnectionError("Gemini API service is currently unavailable. Please try again later.")
    except Exception as e:
        raise APIConnectionError(f"API error: {e}")


def print_banner():
    print("+" + "-"*68 + "+")
    print("|" + " "*23 + "Welcome to Cine-Sleuth!" + " "*22 + "|")
    print("|" + " "*20 + "Your AI-powered movie detector" + " "*18 + "|")
    print("+" + "-"*68 + "+")
    print("""\n
        I will ask up to 20 questions to guess 🙃 the movie you're thinking of🎯.
      """)


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
                    print(summary)
                    break           
                    
                else:
                    print("🤷 Hmm, maybe I need more questions...")
        else:
            print("\n🤔 I couldn't guess your movie. You win this time!")
            final_movie = input("💪 What movie were you thinking of? ")
            prompt = f"""
                        The Movie is {final_movie} and Explain why you cannot get and if the details of movie are
                        not match with {"\n".join([f"Q: {q} A: {a}" for q, a in history])}. Jusity or Complain shortly.
                        """
            final_resp = send_message_safely(chat, prompt)
            print("\nAI Response:", clean_output(final_resp.text))
            print("👋Bye .... Thanks for playing!")

    except APIKeyError as e:
        print(f"❌ API Key Error: {e}")
    except APIQuotaError as e:
        print(f"❌ Quota Error: {e}")
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
