# 🎬 CineSleuth

An AI-powered movie guessing game that uses Google's Gemini API to guess the movie you're thinking of. Think of it as "20 Questions" for movies!

## 🎯 How It Works

1. Think of a movie
2. Start the game
3. Answer the AI's questions about your movie
4. The AI will try to guess your movie within 20 questions!

## 🚀 Features

- **Two Interfaces**: Choose between CLI (command line) or GUI (graphical interface)
- **Interactive Gameplay**: The AI asks strategic questions about genre, actors, plot, time period, and more
- **Free-form Answers**: Answer with any text, not just yes/no
- **Smart Guessing**: Uses Gemini 2.0 Flash for intelligent movie detection
- **Automatic API Key Rotation**: Seamlessly switches to backup API keys when quota is exceeded
- **Clean Output**: Removes markdown formatting for a better experience
- **Game History**: Saves game sessions to `logs/log.txt` for reference
- **Error Handling**: Comprehensive exception handling for API errors, quota limits, and connectivity issues
- **Graceful Exit**: Exit anytime by typing 'exit'

## 📋 Prerequisites

- Python 3.8+
- Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))

## 🛠️ Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/lakaThabrew/CineSleuth.git
   cd CineSleuth
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**

   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**

   ```bash
   pip install -r requirement.txt
   ```

5. **Set up your API key**

   Create a `.env` file in the project root:

   ```
   GEMINI_API_KEY=your_primary_api_key_here
   ```

   **Optional: Add backup API keys for automatic failover**

   If your primary key's quota is exceeded, CineSleuth will automatically switch to backup keys:

   ```
   GEMINI_API_KEY=your_primary_api_key
   GEMINI_API_KEY_2=your_backup_key_2
   GEMINI_API_KEY_3=your_backup_key_3
   GEMINI_API_KEY_4=your_backup_key_4
   ```

   You can add up to 9 API keys (GEMINI_API_KEY through GEMINI_API_KEY_9).

## 🎮 Usage

### Command Line Interface (CLI)

```bash
python main.py
```

### Graphical User Interface (GUI)

```bash
python gui.py
```

The GUI provides:

- 🎨 Modern dark theme interface
- 💬 Scrollable chat display
- ⌨️ Text input for answers (press Enter or click Send)
- 🎮 Start/Reset buttons
- 📊 Question counter and status display

### Using Make (Optional)

If you have `make` installed:

```bash
# Set up environment and install dependencies
make install

# Run the game
make run

# Run tests
make test

# Clean up
make clean
```

## 🧪 Running Tests

```bash
# Run all tests
pytest test.py -v

# Run with coverage
pytest test.py --cov=main -v
```

## 📁 Project Structure

```
CineSleuth/
├── main.py # CLI version with logic
├── gui.py   # GUI with tkinter 
├── test.py           # Unit tests
├── requirement.txt # Python deps
├── Makefile       # Build automation
├── logs/             # Game history logs
│   └── log.txt    # Saved game sessions
├── .env # API keys (create this file)
└── README.md         # This file
```

## 🔧 Dependencies

- `google-generativeai` - Google Gemini API client
- `python-dotenv` - Environment variable management
- `pytest` - Testing framework

## ⚠️ Error Handling

The application handles various error scenarios:

| Error                   | Description                                  |
| ----------------------- | -------------------------------------------- |
| `APIKeyError`           | Missing or invalid API key                   |
| `APIQuotaError`         | API quota exceeded                           |
| `AllKeysExhaustedError` | All API keys have reached their quota limits |
| `APIConnectionError`    | Connection issues with the API               |
| `CineSleuthError`       | General application errors                   |

## 🔄 Automatic API Key Rotation

CineSleuth includes built-in API key rotation:

- When a key's quota is exceeded, it automatically switches to the next available key
- Displays which key is being used and when switching occurs
- Continues the game seamlessly without losing progress
- Supports up to 9 API keys

## 🎯 Game Tips

- Answer questions with as much detail as you like
- Think of well-known movies for better results
- The AI considers genre, actors, directors, plot elements, and more
- If the AI guesses wrong, keep playing - it learns from your answers!

## 🖼️ Screenshots

### GUI Mode

```
+----------------------------------------------------------------------+
|                       🎬 CineSleuth                                  |
|                Your AI-powered movie detector                        |
+----------------------------------------------------------------------+
| 🤖 AI: Question 1: Is the movie from the 21st century?              |
| 👤 You: Yes, it was released in 2010                                |
| 🤖 AI: Question 2: Is it an action or adventure movie?              |
+----------------------------------------------------------------------+
| [Your answer here...                              ] [Send]           |
| [🎮 Start Game]                    [🔄 Reset]                        |
+----------------------------------------------------------------------+
```

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Made with ❤️ and 🤖 AI
