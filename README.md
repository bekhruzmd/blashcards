# 🧠 Blashcards - AI-Powered Learning System

Transform your study materials into intelligent flashcards with AI-powered generation, grading, and explanations. Study smarter, not harder.

## ✨ Features

### 🎯 **AI-Powered Generation**
- Converts PDF, DOCX, and TXT files into high-quality flashcards
- Focuses on key concepts and important facts
- Creates clear, specific questions with complete answers

### 🤖 **Intelligent Grading System**
- AI judge that understands conceptual meaning, not just exact words
- Accepts synonyms, paraphrasing, and alternative explanations
- Provides detailed feedback and scoring (0.0-1.0)
- Generous grading focused on understanding

### 📚 **Interactive Quiz Experience**
- Beautiful command-line interface with Rich formatting
- Real-time AI grading with instant feedback
- AI explanations enabled by default for wrong answers
- Progress tracking and performance analytics
- Early exit with proper results and attempt saving

### 📊 **Multiple Export Formats**
- **CSV** - For Excel/Google Sheets
- **XLSX** - Native Excel format
- **JSON** - For developers/programmers
- **Markdown** - For documentation
- **TXT** - Plain text format
- **Anki (APKG)** - For spaced repetition learning
- **TSV** - Tab-separated values

### 📈 **Performance Analytics**
- Organized quiz attempts in dedicated directory
- Session-based tracking with timestamped files
- Success rate and average score calculations
- Review individual sessions or all-time performance
- Learning progress insights over time

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Google Cloud Account** with Vertex AI API enabled
3. **Service Account JSON** file for authentication

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/blashcards.git
cd blashcards

# Install required packages
pip install -r requirements.txt
```

### Basic Usage

**1. Generate flashcards from study material:**
```bash
python main.py make your_notes.pdf
python main.py make study_guide.docx --format csv
python main.py make lecture_notes.txt --format xlsx
```

**2. Take an interactive quiz (AI explanations ON by default):**
```bash
python main.py quiz
python main.py quiz --limit 10
python main.py quiz --cards-file output_files/my_cards.json
```

**3. Review your performance:**
```bash
python main.py review
python main.py review --file quiz_session_20241220_143052.jsonl
```

## 📖 Detailed Usage

### Generate Flashcards

```bash
# Basic generation (saves as JSON)
python main.py make notes.pdf

# Specify output format
python main.py make notes.pdf --format csv
python main.py make notes.pdf --format xlsx
python main.py make notes.pdf --format md

# Custom output directory
python main.py make notes.pdf --format csv --output-dir my_flashcards

# Create Anki deck for spaced repetition
python main.py make notes.pdf --format apkg
```

**Supported Input Formats:**
- `.pdf` - PDF documents (with fallback readers)
- `.docx` - Microsoft Word documents  
- `.txt` - Plain text files

**Output Structure:**
Files are saved as: `output_files/[filename]_flashcards.[format]`

### Interactive Quiz

```bash
# Basic quiz with AI explanations (default ON)
python main.py quiz

# Turn OFF AI explanations
python main.py quiz --no-explain

# Limited number of cards
python main.py quiz --limit 20

# Use specific flashcard file
python main.py quiz --cards-file output_files/custom_cards.json

# Don't shuffle cards
python main.py quiz --no-shuffle
```

**Quiz Features:**
- Type `quit` to exit early (saves progress and shows results)
- Type `skip` to skip a question
- Get instant AI feedback on answers
- AI explanations enabled by default for deeper learning
- Progress saved even when quitting mid-session

### Performance Review

```bash
# Review all quiz sessions
python main.py review

# Review specific session
python main.py review --file quiz_session_20241220_143052.jsonl

# Use custom quiz directory
python main.py review --dir my_quiz_data
```

**Analytics Include:**
- Total attempts across all sessions
- Average score and success rate
- Recent attempts with detailed breakdown
- Session-specific or combined analysis

## 🛠️ Configuration

### Google Cloud Setup

Update `config.py` with your project details:

```python
# Update these values in config.py
project_id = "your-project-id"
service_account_path = "/path/to/your/service_account.json"
```

Or use environment variables:
```bash
# Linux/Mac
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service_account.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

### AI Model Settings

The system uses Google's Gemini 2.5 Flash model with optimized settings:
- **Generation**: Temperature 0.3 for creative but consistent flashcards
- **Grading**: Temperature 0.1 for reliable, consistent scoring

## 📁 Project Structure

```
blashcards/
├── main.py                  # CLI interface and commands
├── models.py               # Data classes (Verdict, Attempt)
├── config.py               # Google Cloud setup and LLM config
├── ai_judge.py             # Intelligent grading system
├── ai_explainer.py         # AI tutoring explanations
├── file_readers.py         # Multi-format file loading
├── flashcard_gen.py        # AI flashcard generation
├── exporters.py            # Export functions for all formats
├── quiz_logger.py          # Quiz attempt logging
├── utils.py                # JSON parsing utilities
├── requirements.txt        # Python dependencies
├── README.md              # This documentation
├── output_files/          # Generated flashcards (auto-created)
├── quiz_attempts/         # Quiz session logs (auto-created)
│   ├── quiz_session_20241220_090000.jsonl
│   ├── quiz_session_20241220_143052.jsonl
│   └── quiz_session_20241220_200130.jsonl
└── service_account.json   # Your Google Cloud credentials
```

## 🎨 Example Outputs

### CSV Format
```csv
question,answer
"What is photosynthesis?","The process by which plants convert sunlight into chemical energy"
"Name the capital of France","Paris"
```

### Anki Format
Ready-to-import `.apkg` files for the popular spaced repetition app.

### Markdown Format
```markdown
### Q: What is photosynthesis?
A: The process by which plants convert sunlight into chemical energy

### Q: Name the capital of France
A: Paris
```

## 🤝 AI Grading Philosophy

The system uses an intelligent grading approach that:

✅ **Accepts conceptual understanding** over exact wording
✅ **Recognizes synonyms** and paraphrasing  
✅ **Ignores minor spelling/grammar** errors
✅ **Focuses on core concepts** rather than memorization
✅ **Provides encouraging feedback** to support learning

**Example:**
- **Question:** "What is the capital of France?"
- **Expected:** "Paris is the capital of France"
- **Student:** "paris" → ✅ **Correct (1.0)** - Shows understanding
- **Student:** "It's Paris" → ✅ **Correct (1.0)** - Same concept, different words

## 📊 Performance Tracking

### Session-Based Logging
- Each quiz creates a new timestamped file: `quiz_session_YYYYMMDD_HHMMSS.jsonl`
- Organized in dedicated `quiz_attempts/` directory
- Tracks questions, answers, verdicts, and timestamps
- Progress saved even when quitting early

### Review Analytics
- **Individual sessions**: Focus on specific study periods
- **Combined analysis**: Overall learning progress
- **Performance metrics**: Success rates, average scores, improvement trends

## 🔧 Troubleshooting

### Common Issues

**"Cards file not found" error:**
- Check file path: files are saved in `output_files/` by default
- Generate cards first: `python main.py make your_notes.pdf`
- Use correct file extension (usually `.json`)

**"Invalid JSON from AI" error:**
- Built-in retry logic handles most cases automatically
- Check internet connection and Google Cloud credentials
- Verify your service account has Vertex AI permissions

**"GOOGLE_APPLICATION_CREDENTIALS not set":**
- Update the path in `config.py`
- Or set environment variable to your service account JSON file
- Ensure the file path exists and is accessible

### Getting Help

```bash
# See all available commands
python main.py --help

# Get help for specific commands
python main.py make --help
python main.py quiz --help
python main.py review --help
```

## 🚀 Advanced Usage

### Batch Processing
```bash
# Process multiple files
for file in *.pdf; do
    python main.py make "$file" --format csv
done
```

### Custom Study Sessions
```bash
# Quick focused session
python main.py quiz --limit 5

# Turn off explanations for speed
python main.py quiz --no-explain --limit 10

# Sequential review (no shuffle)
python main.py quiz --no-shuffle --limit 15
```

### Session Management
```bash
# Review today's morning session
python main.py review --file quiz_session_20241220_090000.jsonl

# Analyze all-time performance
python main.py review

# Use custom quiz directory
python main.py review --dir backup_attempts
```

## 🎯 Tips for Best Results

### Input Materials
- Use well-structured documents with clear headings
- Include key concepts, definitions, and important facts
- Remove unnecessary formatting that might confuse the AI

### Quiz Strategy
- Keep AI explanations ON (default) when learning new material
- Use limited sessions (`--limit 10`) for focused practice
- Review individual sessions to track topic-specific progress
- Quit early if needed - your progress is always saved

### Export Formats
- **Anki (APKG)**: Best for long-term retention and spaced repetition
- **CSV/Excel**: Great for sharing with study groups
- **Markdown**: Perfect for creating study guides
- **JSON**: Default format that works seamlessly with the quiz system

## 🏗️ Modular Architecture

The codebase is organized into focused modules:

- **`main.py`**: CLI interface and user interaction
- **`ai_judge.py`**: Intelligent answer grading
- **`ai_explainer.py`**: Mistake explanations and tutoring
- **`flashcard_gen.py`**: AI-powered flashcard generation
- **`file_readers.py`**: Multi-format document processing
- **`exporters.py`**: Export to various formats
- **`models.py`**: Data structures and types

This makes the system easy to extend, test, and maintain.

## 📝 Dependencies

Core requirements (install with `pip install -r requirements.txt`):
- `typer` - CLI framework
- `rich` - Beautiful terminal output
- `google-cloud-aiplatform` - Vertex AI integration
- `langchain-google-vertexai` - LLM interface
- `pandas` - Data processing
- `pdfplumber`, `PyPDF2` - PDF reading
- `python-docx` - Word document processing
- `genanki` - Anki export (optional)

## 📝 License

This project is available for educational and personal use. Please respect AI usage terms and Google Cloud pricing.

---

**Happy Learning! 🎓**

*Transform your study materials into an intelligent learning experience with AI-powered flashcards.*