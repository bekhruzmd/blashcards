# 🧠 Smart Flashcards - AI-Powered Learning System

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
- Optional AI explanations for wrong answers
- Progress tracking and performance analytics

### 📊 **Multiple Export Formats**
- **CSV** - For Excel/Google Sheets
- **XLSX** - Native Excel format
- **JSON** - For developers/programmers
- **Markdown** - For documentation
- **TXT** - Plain text format
- **Anki (APKG)** - For spaced repetition learning
- **TSV** - Tab-separated values

### 📈 **Performance Analytics**
- Track quiz performance over time
- Success rate and average score calculations
- Recent attempts history
- Learning progress insights

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Google Cloud Account** with Vertex AI API enabled
3. **Service Account JSON** file for authentication

### Installation

```bash
# Clone or download the repository
git clone <your-repo-url>
cd smart-flashcards

# Install required packages
pip install typer rich google-cloud-aiplatform langchain-google-vertexai
pip install pdfplumber PyPDF2 python-docx pandas openpyxl
pip install genanki  # Optional: for Anki export

# Set up Google Cloud credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service_account.json"
```

### Basic Usage

**1. Generate flashcards from study material:**
```bash
python generator.py make your_notes.pdf
python generator.py make study_guide.docx --format csv
python generator.py make lecture_notes.txt --format xlsx
```

**2. Take an interactive quiz:**
```bash
python generator.py quiz
python generator.py quiz --explain --limit 10
python generator.py quiz --cards-file my_cards.json
```

**3. Review your performance:**
```bash
python generator.py review
python generator.py review --file quiz_attempts.jsonl
```

## 📖 Detailed Usage

### Generate Flashcards

```bash
# Basic generation (saves as JSON)
python generator.py make notes.pdf

# Specify output format
python generator.py make notes.pdf --format csv
python generator.py make notes.pdf --format xlsx
python generator.py make notes.pdf --format md

# Custom output directory
python generator.py make notes.pdf --format csv --output-dir my_flashcards

# Create Anki deck for spaced repetition
python generator.py make notes.pdf --format apkg
```

**Supported Input Formats:**
- `.pdf` - PDF documents
- `.docx` - Microsoft Word documents  
- `.txt` - Plain text files

**Output Structure:**
Files are saved as: `output_files/[filename]_flashcards.[format]`

### Interactive Quiz

```bash
# Basic quiz with all cards
python generator.py quiz

# Quiz with AI explanations for wrong answers
python generator.py quiz --explain

# Limited number of cards
python generator.py quiz --limit 20

# Use specific flashcard file
python generator.py quiz --cards-file custom_cards.json

# Don't shuffle cards
python generator.py quiz --no-shuffle
```

**Quiz Features:**
- Type `quit` to exit early
- Type `skip` to skip a question
- Get instant AI feedback on answers
- Optional detailed explanations for mistakes

### Performance Review

```bash
# Review default attempts file
python generator.py review

# Review specific attempts file
python generator.py review --file old_attempts.jsonl
```

**Analytics Include:**
- Total attempts and success rate
- Average score across all attempts
- Recent attempts with scores
- Performance trends over time

## 🛠️ Configuration

### Google Cloud Setup

1. **Create a Google Cloud Project**
2. **Enable Vertex AI API**
3. **Create a Service Account** with Vertex AI permissions
4. **Download the JSON key file**
5. **Set the environment variable:**

```bash
# Linux/Mac
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service_account.json"

# Windows
set GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\service_account.json"
```

### AI Model Settings

The system uses Google's Gemini 2.5 Flash model with optimized settings:
- **Generation**: Temperature 0.3 for creative but consistent flashcards
- **Grading**: Temperature 0.1 for reliable, consistent scoring

## 📁 File Structure

```
smart-flashcards/
├── generator.py              # Main application
├── output_files/            # Generated flashcards (created automatically)
├── quiz_attempts.jsonl      # Quiz performance log
├── service_account.json     # Google Cloud credentials (you provide)
└── README.md               # This file
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

All quiz attempts are logged to `quiz_attempts.jsonl` including:
- Question and correct answer
- Your answer and AI verdict
- Score and detailed feedback
- Timestamp for progress tracking

Use `python generator.py review` to analyze your learning patterns and identify areas for improvement.

## 🔧 Troubleshooting

### Common Issues

**"Package not found" error:**
- Ensure file path is correct
- Use full file path if file is in different directory
- Check file isn't corrupted by opening in Word/PDF viewer

**"Invalid JSON from AI" error:**
- Usually resolves automatically with retry logic
- Check internet connection
- Verify Google Cloud credentials are valid

**"GOOGLE_APPLICATION_CREDENTIALS not set":**
- Set environment variable to your service account JSON file
- Ensure the file path is correct and accessible

### Getting Help

```bash
# See all available commands
python generator.py --help

# Get help for specific commands
python generator.py make --help
python generator.py quiz --help
python generator.py review --help
```

## 🚀 Advanced Usage

### Batch Processing
```bash
# Process multiple files
for file in *.pdf; do
    python generator.py make "$file" --format csv
done
```

### Custom Study Sessions
```bash
# Create focused study sessions
python generator.py quiz --limit 5 --explain  # Short session with explanations
python generator.py quiz --no-shuffle --limit 10  # Sequential review
```

### Integration with Study Tools
- Export as **APKG** for Anki spaced repetition
- Export as **CSV** for Excel analysis
- Export as **Markdown** for documentation

## 🎯 Tips for Best Results

### Input Materials
- Use well-structured documents with clear headings
- Include key concepts, definitions, and important facts
- Remove unnecessary formatting that might confuse the AI

### Quiz Strategy
- Enable explanations (`--explain`) when learning new material
- Use limited sessions (`--limit 10`) for focused practice
- Review performance regularly to identify weak areas

### Export Formats
- **Anki (APKG)**: Best for long-term retention and spaced repetition
- **CSV/Excel**: Great for sharing with study groups
- **Markdown**: Perfect for creating study guides

## 📝 License

This project is available for educational and personal use. Please respect AI usage terms and Google Cloud pricing.

---

**Happy Learning! 🎓**

*Transform your study materials into an intelligent learning experience with AI-powered flashcards.*