# Notetion Streamlit Dashboard

A user-friendly web interface for the Notetion AI note generation tool.

## Features

- **Easy File Upload**: Drag and drop or browse to upload TXT, PDF, and JSON files
- **AI Model Selection**: Choose between GPT-4, GPT-4-turbo, and GPT-3.5-turbo
- **Customizable Settings**: Adjust creativity level (temperature) for note generation
- **Real-time Processing**: Watch progress as your files are processed
- **Download Options**: Export generated notes as Markdown or plain text
- **Error Handling**: Clear feedback on any processing issues

## Setup Instructions

1. **Activate Virtual Environment**:
   ```bash
   source venv/bin/activate
   ```

2. **Install Dependencies** (if not already done):
   ```bash
   pip install -r requirements.txt
   ```

3. **Set OpenAI API Key** (recommended secure method):
   ```bash
   # Option 1: Set environment variable (most secure)
   export OPENAI_API_KEY="your-api-key-here"
   
   # Option 2: Create .env file (also secure)
   cp .env.example .env
   # Then edit .env file and add your actual API key
   
   # Option 3: Enter in web interface (less secure)
   # You can also enter it directly in the sidebar, but environment variables are safer
   ```

4. **Run the Streamlit App**:
   ```bash
   streamlit run streamlit_app.py
   ```

5. **Open in Browser**:
   - The app will automatically open in your default browser
   - If not, navigate to `http://localhost:8501`

## How to Use

1. **Configure API Key**: Enter your OpenAI API key in the sidebar
2. **Select Model**: Choose your preferred AI model (GPT-4 recommended for best quality)
3. **Adjust Settings**: Set the creativity level using the slider
4. **Upload Files**: Upload your transcripts, slides, or documents
5. **Generate Notes**: Click the "Generate Notes" button
6. **Download Results**: Save your notes as Markdown or text files

## Supported File Types

- **TXT**: Plain text files (transcripts, notes, etc.)
- **PDF**: PDF documents (slides, papers, etc.)
- **JSON**: JSON data files

## Tips for Best Results

- Use clear, well-structured input files
- GPT-4 provides higher quality notes but takes longer to process
- Lower creativity levels (0.1-0.3) work best for factual content
- Higher creativity levels (0.5-0.8) can be useful for more creative interpretations

## Troubleshooting

- **API Key Issues**: Make sure your OpenAI API key is valid and has sufficient credits
- **File Upload Problems**: Ensure files are in supported formats (TXT, PDF, JSON)
- **Processing Errors**: Check the error messages displayed in the interface
- **Slow Performance**: Try using GPT-3.5-turbo for faster processing

## Project Structure

```
notetion/
├── streamlit_app.py          # Main Streamlit dashboard
├── notetion_workflow.py      # Core workflow logic
├── requirements.txt          # Python dependencies
├── config_example.py         # Configuration template
└── README_STREAMLIT.md       # This file
```

## Development

To modify the dashboard:

1. Edit `streamlit_app.py` for UI changes
2. Edit `notetion_workflow.py` for workflow logic changes
3. Test changes by rerunning `streamlit run streamlit_app.py`

The Streamlit app will automatically reload when you save changes to the files.
