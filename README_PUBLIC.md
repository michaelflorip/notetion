# Notetion - Public Version

A public-facing version of the Notetion AI Note Generator that requires users to provide their own OpenAI API keys.

## 🌟 Features

- **User-Provided API Keys**: Secure, session-only API key storage
- **Multiple File Formats**: Support for TXT, PDF, and JSON files
- **AI Model Selection**: Choose between GPT-3.5-turbo, GPT-4, and GPT-4-turbo
- **Cost Transparency**: Real-time cost estimation and tracking
- **Usage Analytics**: Track your processing history and costs
- **Export Options**: Download notes as Markdown or plain text
- **Search & History**: Find and reuse past note generations

## 🚀 Quick Start

### For Users

1. **Get an OpenAI API Key**:
   - Visit [OpenAI Platform](https://platform.openai.com)
   - Sign up or log in to your account
   - Navigate to API Keys section
   - Create a new secret key

2. **Run the Application**:
   ```bash
   streamlit run streamlit_app_public.py
   ```

3. **Use the Tool**:
   - Enter your API key in the sidebar
   - Upload your files (TXT, PDF, JSON)
   - Select your preferred AI model
   - Generate comprehensive notes!

### For Hosting Providers

This version is designed for public hosting where:
- Users provide their own OpenAI API keys
- No server-side API costs for the host
- Each user controls their own usage and costs
- Maximum security and privacy

## 🔒 Security & Privacy

- **API keys are never stored permanently**
- **Session-only storage** in browser memory
- **No server-side API key exposure**
- **Users control their own costs**
- **Local database for usage tracking only**

## 💰 Cost Information

Typical costs per note generation:
- **GPT-3.5-turbo**: $0.001-0.005
- **GPT-4**: $0.01-0.03
- **GPT-4-turbo**: $0.005-0.015

*Costs depend on input file size and complexity*

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/michaelflorip/notetion.git
   cd notetion
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the public version**:
   ```bash
   streamlit run streamlit_app_public.py
   ```

## 📁 File Structure

```
notetion/
├── streamlit_app_public.py    # Public version (user API keys)
├── streamlit_app.py           # Private version (env API keys)
├── notetion_workflow.py       # Core workflow logic
├── database_manager.py        # Usage tracking
├── requirements.txt           # Dependencies
└── README_PUBLIC.md          # This file
```

## 🌐 Deployment Options

### Streamlit Cloud
1. Fork this repository
2. Connect to Streamlit Cloud
3. Deploy `streamlit_app_public.py`
4. Users provide their own API keys

### Heroku
```bash
# Create Procfile
echo "web: streamlit run streamlit_app_public.py --server.port=$PORT --server.address=0.0.0.0" > Procfile

# Deploy
git add .
git commit -m "Deploy public version"
git push heroku main
```

### Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app_public.py", "--server.address=0.0.0.0"]
```

## 🔧 Configuration

The public version automatically:
- Requires user API key input
- Validates API key format
- Provides cost estimates
- Tracks usage locally
- Handles errors gracefully

## 📊 Analytics & Tracking

Users can view their own:
- Processing history
- Cost breakdown
- Model usage statistics
- Success rates
- Token consumption

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with the public version
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues or questions:
1. Check the [GitHub Issues](https://github.com/michaelflorip/notetion/issues)
2. Create a new issue with details
3. Include error messages and steps to reproduce

## 🔄 Differences from Private Version

| Feature | Private Version | Public Version |
|---------|----------------|----------------|
| API Key Source | Environment variables | User input |
| API Key Storage | Server environment | Session only |
| Cost Responsibility | Server owner | Individual users |
| Security Model | Server-side | Client-side |
| Deployment Complexity | Higher | Lower |

## 🎯 Use Cases

Perfect for:
- **Educational institutions** wanting to provide AI tools
- **Open source communities** sharing AI capabilities
- **Developers** learning about AI integration
- **Organizations** wanting cost transparency
- **Personal projects** with controlled usage

---

**Built with ❤️ using Streamlit and LangGraph**
