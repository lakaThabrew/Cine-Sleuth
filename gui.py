"""
CineSleuth GUI - A graphical interface for the movie guessing game
Imports core functionality from main.py
"""
import os
import tkinter as tk
from tkinter import messagebox, scrolledtext
from datetime import datetime
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
import threading

from main import (
    APIKeyManager,
    clean_output,
    CineSleuthError,
    APIKeyError,
    APIConnectionError,
    APIQuotaError,
    AllKeysExhaustedError,
)

class CineSleuthGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 CineSleuth - Movie Guessing Game")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        self.bg_color = "#1a1a2e"
        self.fg_color = "#eaeaea"
        self.accent_color = "#e94560"
        self.secondary_color = "#16213e"
        self.button_color = "#0f3460"
        
        self.root.configure(bg=self.bg_color)
        
        self.api_key_manager = APIKeyManager()
        self.model = None
        self.chat = None
        self.history = []
        self.question_count = 0
        self.max_questions = 20
        self.game_active = False
        
        self.setup_ui()
        self.initialize_api()
    
    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="🎬 CineSleuth",
            font=("Helvetica", 28, "bold"),
            fg=self.accent_color,
            bg=self.bg_color
        )
        title_label.pack(pady=(0, 5))
        
        subtitle_label = tk.Label(
            main_frame,
            text="Your AI-powered movie detector",
            font=("Helvetica", 12),
            fg=self.fg_color,
            bg=self.bg_color
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Status bar
        self.status_frame = tk.Frame(main_frame, bg=self.secondary_color)
        self.status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Status: Ready",
            font=("Helvetica", 10),
            fg=self.fg_color,
            bg=self.secondary_color,
            padx=10,
            pady=5
        )
        self.status_label.pack(side=tk.LEFT)
        
        self.question_label = tk.Label(
            self.status_frame,
            text="Questions: 0/20",
            font=("Helvetica", 10),
            fg=self.fg_color,
            bg=self.secondary_color,
            padx=10,
            pady=5
        )
        self.question_label.pack(side=tk.RIGHT)
        
        # Chat display area
        chat_frame = tk.Frame(main_frame, bg=self.secondary_color)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Helvetica", 11),
            bg=self.secondary_color,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT,
            padx=15,
            pady=15,
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for different message types
        self.chat_display.tag_configure("ai", foreground="#00d4ff")
        self.chat_display.tag_configure("user", foreground="#00ff88")
        self.chat_display.tag_configure("system", foreground="#ffaa00")
        self.chat_display.tag_configure("error", foreground="#ff4444")
        self.chat_display.tag_configure("success", foreground="#00ff00")
        
        # Input frame
        input_frame = tk.Frame(main_frame, bg=self.bg_color)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Answer input field
        self.answer_entry = tk.Entry(
            input_frame,
            font=("Helvetica", 12),
            bg=self.secondary_color,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT,
            state=tk.DISABLED
        )
        self.answer_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10), ipady=10)
        self.answer_entry.bind("<Return>", lambda e: self.submit_answer())
        
        # Send button
        self.send_btn = tk.Button(
            input_frame,
            text="Send",
            font=("Helvetica", 12, "bold"),
            bg="#28a745",
            fg="white",
            activebackground="#218838",
            activeforeground="white",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.submit_answer,
            state=tk.DISABLED
        )
        self.send_btn.pack(side=tk.RIGHT)
        
        # Control buttons frame
        control_frame = tk.Frame(main_frame, bg=self.bg_color)
        control_frame.pack(fill=tk.X)
        
        self.start_btn = tk.Button(
            control_frame,
            text="🎮 Start Game",
            font=("Helvetica", 12, "bold"),
            bg=self.accent_color,
            fg="white",
            activebackground="#d63850",
            activeforeground="white",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.start_game
        )
        self.start_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        
        self.reset_btn = tk.Button(
            control_frame,
            text="🔄 Reset",
            font=("Helvetica", 12, "bold"),
            bg=self.button_color,
            fg="white",
            activebackground="#0d2d4d",
            activeforeground="white",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.reset_game
        )
        self.reset_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))
    
    def initialize_api(self):
        try:
            api_key = self.api_key_manager.load_keys()
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            self.add_message(f"✅ Loaded {len(self.api_key_manager.keys)} API key(s)", "system")
            self.update_status("Ready to play!")

        except Exception as e:
            self.add_message(f"❌ Failed to initialize API: {e}", "error")
            self.update_status("API Error")
            self.start_btn.config(state=tk.DISABLED)
    
    def add_message(self, message, msg_type="system"):
        self.chat_display.config(state=tk.NORMAL)
        
        if msg_type == "ai":
            prefix = "🤖 AI: "
        elif msg_type == "user":
            prefix = "👤 You: "
        elif msg_type == "error":
            prefix = "❌ "
        elif msg_type == "success":
            prefix = "🎉 "
        else:
            prefix = "ℹ️ "
        
        self.chat_display.insert(tk.END, prefix + message + "\n\n", msg_type)
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def update_status(self, status):
        self.status_label.config(text=f"Status: {status}")
    
    def update_question_count(self):
        self.question_label.config(text=f"Questions: {self.question_count}/{self.max_questions}")
    
    def start_game(self):
        self.reset_game()
        self.game_active = True
        self.chat = self.model.start_chat(history=[])
        
        self.start_btn.config(state=tk.DISABLED)
        self.answer_entry.config(state=tk.NORMAL)
        self.send_btn.config(state=tk.NORMAL)
        self.answer_entry.focus()
        
        self.add_message("Think of a movie and I'll try to guess it in 20 questions!", "system")
        self.update_status("Game in progress...")
        
        # Ask first question
        self.ask_question()
    
    def reset_game(self):
        self.history = []
        self.question_count = 0
        self.game_active = False
        self.chat = None
        
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        self.start_btn.config(state=tk.NORMAL)
        self.answer_entry.config(state=tk.DISABLED)
        self.answer_entry.delete(0, tk.END)
        self.send_btn.config(state=tk.DISABLED)
        
        self.update_status("Ready")
        self.update_question_count()
        
        self.add_message("Welcome to CineSleuth! Click 'Start Game' to begin.", "system")
    
    def ask_question(self):
        if not self.game_active:
            return
        
        self.question_count += 1
        self.update_question_count()
        self.update_status("AI is thinking...")
        self.answer_entry.config(state=tk.DISABLED)
        self.send_btn.config(state=tk.DISABLED)
        
        # Run in thread to avoid freezing UI
        threading.Thread(target=self._ask_question_thread, daemon=True).start()
    
    def _ask_question_thread(self):
        try:
            summary = "\n".join([f"Q: {q} A: {a}" for q, a in self.history])

            prompt = f"""
                        You are a movie-detective AI playing a guessing game. 
                        The user is thinking of a movie.
                        Previous Q&A so far:
                        {summary if summary else 'None'}, and you have only 20 questions in total. 
                        You have {self.max_questions - self.question_count + 1} questions remaining. 
                        You must guess the movie within these questions.
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
            
            response = self.chat.send_message(prompt)
            question = clean_output(response.text)
            
            # Update UI in main thread
            self.root.after(0, lambda: self._display_question(question))
            
        except google_exceptions.ResourceExhausted:
            if self.api_key_manager.has_more_keys():
                new_key = self.api_key_manager.mark_current_exhausted()
                genai.configure(api_key=new_key)
                self.root.after(0, lambda: self.add_message("🔄 Switched to backup API key", "system"))
                self._ask_question_thread()
            else:
                self.root.after(0, lambda: self.add_message("API quota exceeded on all keys!", "error"))
                self.root.after(0, self.end_game)
        except Exception as e:
            self.root.after(0, lambda: self.add_message(f"Error: {e}", "error"))
            self.root.after(0, self.end_game)
    
    def _display_question(self, question):
        self.current_question = question
        self.add_message(f"Question {self.question_count}: {question}", "ai")
        self.update_status("Waiting for your answer...")
        self.answer_entry.config(state=tk.NORMAL)
        self.send_btn.config(state=tk.NORMAL)
        self.answer_entry.focus()
    
    def submit_answer(self):
        """Submit the answer from the input field"""
        answer = self.answer_entry.get().strip()
        if not answer:
            return
        
        self.answer_entry.delete(0, tk.END)
        self.answer_question(answer)
    
    def answer_question(self, answer):
        if not self.game_active:
            return
        
        self.add_message(answer, "user")
        self.history.append((self.current_question, answer))
        
        self.answer_entry.config(state=tk.DISABLED)
        self.send_btn.config(state=tk.DISABLED)
        self.update_status("AI is analyzing...")
        
        # Check for guess
        threading.Thread(target=lambda: self._try_guess(answer), daemon=True).start()
    
    def _try_guess(self, last_answer):
        try:
            summary = "\n".join([f"Q: {q} A: {a}" for q, a in self.history])
    
            guess_prompt = f"""
                                Based on the following Q&A:
                                {summary if summary else 'None'}. Guess the movie the user is thinking of based on the provided information. 
                                Mostly focus on the last Q&A in history to narrow down and guess the movie.
                                If not confident, say 'I need more questions'. Output only the movie title or the phrase.
                            """
            
            guess_resp = self.chat.send_message(guess_prompt)
            guess = clean_output(guess_resp.text)
            
            if "need more questions" not in guess.lower():
                self.root.after(0, lambda: self._show_guess(guess))
            else:
                if self.question_count >= self.max_questions:
                    self.root.after(0, self._game_over_no_guess)
                else:
                    self.root.after(0, self.ask_question)
                    
        except Exception as e:
            self.root.after(0, lambda: self.add_message(f"Error: {e}", "error"))
    
    def _show_guess(self, guess):
        self.add_message(f"I think your movie is: {guess}", "ai")
        
        result = messagebox.askyesno(
            "Is this correct?",
            f"🎬 My guess is:\n\n{guess}\n\nIs this the movie you were thinking of?"
        )
        
        if result:
            self.add_message("🎉 I guessed it! Thanks for playing!", "success")
            self.save_history(guess, won=True)
            self.end_game()
        else:
            self.add_message("🤔 Hmm, let me ask more questions...", "system")
            if self.question_count >= self.max_questions:
                self._game_over_no_guess()
            else:
                self.ask_question()
    
    def _game_over_no_guess(self):
        self.add_message("😅 I couldn't guess your movie. You win!", "system")
        
        # Ask what the movie was
        movie = self._ask_for_movie()
        if movie:
            self.add_message(f"The movie was: {movie}", "user")
            self.save_history(movie, won=False)
        
        self.end_game()
    
    def _ask_for_movie(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("What was the movie?")
        dialog.geometry("400x150")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.root)
        dialog.grab_set()
        
        result = [None]
        
        tk.Label(
            dialog,
            text="What movie were you thinking of?",
            font=("Helvetica", 12),
            fg=self.fg_color,
            bg=self.bg_color
        ).pack(pady=20)
        
        entry = tk.Entry(dialog, font=("Helvetica", 12), width=30)
        entry.pack(pady=10)
        entry.focus()
        
        def submit():
            result[0] = entry.get()
            dialog.destroy()
        
        tk.Button(
            dialog,
            text="Submit",
            command=submit,
            bg=self.accent_color,
            fg="white",
            font=("Helvetica", 11, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=5
        ).pack(pady=10)
        
        entry.bind("<Return>", lambda e: submit())
        
        self.root.wait_window(dialog)
        return result[0]
    
    def save_history(self, movie, won):
        try:
            log_dir = os.path.join(os.path.dirname(__file__), "logs")
            os.makedirs(log_dir, exist_ok=True)
            
            with open(os.path.join(log_dir, "log.txt"), 'a', encoding='utf-8') as f:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n{'='*50}\n")
                f.write(f"Date: {now}\n")
                f.write(f"Movie: {movie}\n")
                f.write(f"Result: {'AI Won' if won else 'Player Won'}\n")
                f.write(f"Questions Asked: {self.question_count}\n")
                f.write("-" * 30 + "\n")
                for q, a in self.history:
                    f.write(f"Q: {q}\nA: {a}\n\n")

        except Exception as e:
            print(f"Failed to save history: {e}")
    
    def end_game(self):
        self.game_active = False
        self.answer_entry.config(state=tk.DISABLED)
        self.send_btn.config(state=tk.DISABLED)
        self.start_btn.config(state=tk.NORMAL)
        self.update_status("Game ended")
        self.add_message("Click 'Start Game' to play again!", "system")

def main():
    root = tk.Tk()
    app = CineSleuthGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
