# 🎬 CineSleuth

An AI-powered movie guessing game that uses Google's Gemini API to guess the movie you're thinking of by asking yes/no questions. Think of it as "20 Questions" for movies!

## 🎯 How It Works

1. Think of a movie
2. Start the game
3. Answer the AI's yes/no questions
4. The AI will try to guess your movie within 20 questions!

## 🚀 Features

- **Interactive Gameplay**: The AI asks strategic questions about genre, actors, plot, time period, and more
- **Smart Guessing**: Uses Gemini 2.0 Flash for intelligent movie detection
- **Automatic API Key Rotation**: Seamlessly switches to backup API keys when quota is exceeded
- **Clean Output**: Removes markdown formatting for a better console experience
- **Game History**: Saves game sessions to `history.txt` for reference
- **Error Handling**: Comprehensive exception handling for API errors, quota limits, and connectivity issues
- **Graceful Exit**: Exit anytime by typing 'exit'

## 📋 Prerequisites

- Python 3.8+
- Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))

## 🛠️ Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/lakaThabrew/Cine-Sleuth.git
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
   NO_of_keys=1
   ```

   **Optional: Add backup API keys for automatic failover**

   If your primary key's quota is exceeded, CineSleuth will automatically switch to backup keys:

   ```
   NO_of_keys=4
   GEMINI_API_KEY=your_primary_api_key
   GEMINI_API_KEY_2=your_backup_key_2
   GEMINI_API_KEY_3=your_backup_key_3
   GEMINI_API_KEY_4=your_backup_key_4
   ```

   Set `NO_of_keys` to the total number of API keys you have configured.

## 🎮 Usage

Run the game:

```bash
python main.py
```

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
├── main.py         # Main with game logic
├── test.py           # Unit tests
├── requirement.txt   # Python dependencies
├── Makefile          # Build automation
├── history.txt   # Game history (auto-generated)
├── .env           # API keys (create this file)
|── .env.example
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

- Answer questions truthfully with 'yes' or 'no'
- Think of well-known movies for better results
- The AI considers genre, actors, directors, plot elements, and more
- If the AI guesses wrong, keep playing - it learns from your answers!

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Made with ❤️ and 🤖 AI
