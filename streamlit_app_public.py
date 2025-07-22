"""
Notetion Streamlit Dashboard - Public Version
A user-friendly web interface for the Notetion workflow tool that requires users to provide their own OpenAI API key.
"""

import streamlit as st
import os
import tempfile
from pathlib import Path
from typing import List
from notetion_workflow import NotetionWorkflow
from database_manager import DatabaseManager, get_file_info
import time
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Notetion - AI Note Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .upload-section {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .notes-section {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    .error-message {
        background-color: #ffebee;
        color: #c62828;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #c62828;
    }
    .success-message {
        background-color: #e8f5e8;
        color: #2e7d32;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #2e7d32;
    }
    .api-key-section {
        background-color: #fff3cd;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'workflow' not in st.session_state:
        st.session_state.workflow = None
    if 'generated_notes' not in st.session_state:
        st.session_state.generated_notes = ""
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    if 'api_key_valid' not in st.session_state:
        st.session_state.api_key_valid = False

def setup_api_key():
    """Setup OpenAI API key from user input"""
    st.sidebar.header("🔑 API Configuration")
    
    # API Key input
    api_key = st.sidebar.text_input(
        "Enter your OpenAI API Key",
        type="password",
        help="Your API key is not stored and is only used for this session. Get your API key from https://platform.openai.com/api-keys"
    )
    
    if api_key:
        if api_key.startswith('sk-') and len(api_key) > 20:
            st.sidebar.success("✅ API Key format looks valid")
            st.session_state.api_key = api_key
            st.session_state.api_key_valid = True
            return True
        else:
            st.sidebar.error("❌ Invalid API key format")
            st.session_state.api_key_valid = False
            return False
    else:
        st.sidebar.warning("⚠️ Please enter your OpenAI API key to continue")
        
        # Information about getting an API key
        with st.sidebar.expander("ℹ️ How to get an API key"):
            st.markdown("""
            **Steps to get your OpenAI API key:**
            
            1. Go to [OpenAI Platform](https://platform.openai.com)
            2. Sign up or log in to your account
            3. Navigate to API Keys section
            4. Click "Create new secret key"
            5. Copy the key and paste it above
            
            **Important:**
            - Your API key is never stored by this application
            - You will be charged by OpenAI for usage
            - Typical cost: $0.001-0.03 per note generation
            - Keep your API key secure and don't share it
            """)
        
        st.session_state.api_key_valid = False
        return False

def save_uploaded_files(uploaded_files) -> List[str]:
    """Save uploaded files to temporary directory and return file paths"""
    temp_dir = tempfile.mkdtemp()
    file_paths = []
    
    for uploaded_file in uploaded_files:
        # Create temporary file path
        temp_file_path = os.path.join(temp_dir, uploaded_file.name)
        
        # Save uploaded file
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        file_paths.append(temp_file_path)
    
    return file_paths

def display_file_info(uploaded_files):
    """Display information about uploaded files"""
    if uploaded_files:
        st.subheader("📁 Uploaded Files")
        for i, file in enumerate(uploaded_files, 1):
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.write(f"{i}. **{file.name}**")
            with col2:
                st.write(f"Size: {file.size:,} bytes")
            with col3:
                st.write(f"Type: {file.type}")

def main():
    """Main Streamlit application"""
    initialize_session_state()
    
    # Initialize database manager
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = DatabaseManager()
    
    # Navigation
    st.sidebar.title("📝 Notetion")
    
    # API Key setup first
    api_key_valid = setup_api_key()
    
    # Only show navigation if API key is valid
    if api_key_valid:
        page = st.sidebar.selectbox(
            "Navigate",
            ["🏠 Generate Notes", "📊 Analytics", "📋 History", "🔍 Search", "⚙️ Settings"]
        )
        
        if page == "🏠 Generate Notes":
            show_generate_notes_page()
        elif page == "📊 Analytics":
            show_analytics_page()
        elif page == "📋 History":
            show_history_page()
        elif page == "🔍 Search":
            show_search_page()
        elif page == "⚙️ Settings":
            show_settings_page()
    else:
        show_welcome_page()

def show_welcome_page():
    """Show welcome page when no API key is provided"""
    # Header
    st.markdown('<h1 class="main-header">📝 Notetion - AI Note Generator</h1>', unsafe_allow_html=True)
    
    # Welcome message
    st.markdown('<div class="api-key-section">', unsafe_allow_html=True)
    st.markdown("""
    ## Welcome to Notetion! 🎉
    
    Transform your transcripts, slides, and documents into comprehensive bullet-point notes using AI.
    
    **To get started:**
    1. Enter your OpenAI API key in the sidebar ←
    2. Upload your files (TXT, PDF, JSON)
    3. Generate professional notes instantly!
    
    ### Why do I need an API key?
    - This is a **free, open-source tool** that uses OpenAI's API
    - You pay OpenAI directly for usage (typically $0.001-0.03 per note)
    - Your API key is **never stored** and only used during your session
    - This ensures your data privacy and gives you full control over costs
    
    ### Features:
    - 📄 **Multiple file formats**: TXT, PDF, JSON support
    - 🤖 **Multiple AI models**: GPT-3.5-turbo, GPT-4, GPT-4-turbo
    - 📊 **Usage analytics**: Track your costs and usage
    - 💾 **Export options**: Download as Markdown or Text
    - 🔍 **Search history**: Find and reuse past notes
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Demo section
    st.subheader("📋 Example Output")
    st.markdown("""
    Here's what Notetion generates from your content:
    
    ```markdown
    # Lecture Title: Machine Learning Fundamentals
    
    ## Agenda
    - **Supervised Learning** (classification and regression tasks)
    - **Unsupervised Learning** (clustering and dimensionality reduction)
    - **Model Evaluation** (cross-validation, metrics, overfitting)
    
    ### 1. Supervised Learning
    - **Classification**: Predicting discrete categories
      - **Decision Trees** (interpretable, handles non-linear data)
      - **Random Forest** (ensemble method, reduces overfitting)
    - **Regression**: Predicting continuous values
      - **Linear Regression** (baseline method, assumes linear relationship)
      - **Polynomial Features** (captures non-linear patterns)
    ```
    """)
    
    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit and LangGraph | [GitHub Repository](https://github.com/michaelflorip/notetion)")

def show_generate_notes_page():
    """Show the main note generation page"""
    # Header
    st.markdown('<h1 class="main-header">📝 Generate Notes</h1>', unsafe_allow_html=True)
    st.markdown("Transform your transcripts, slides, and documents into comprehensive bullet-point notes using AI.")
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Settings")
    
    # Model selection
    model_options = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
    selected_model = st.sidebar.selectbox(
        "Select AI Model",
        model_options,
        index=0,
        help="Choose the AI model for note generation. GPT-3.5-turbo is fastest and cheapest, GPT-4 provides better quality but costs more."
    )
    
    # Temperature setting
    temperature = st.sidebar.slider(
        "Creativity Level",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1,
        help="Lower values make output more focused and deterministic."
    )
    
    # Cost estimation
    st.sidebar.markdown("### 💰 Estimated Costs")
    if selected_model == "gpt-3.5-turbo":
        st.sidebar.info("~$0.001-0.005 per note")
    elif selected_model == "gpt-4":
        st.sidebar.info("~$0.01-0.03 per note")
    else:  # gpt-4-turbo
        st.sidebar.info("~$0.005-0.015 per note")
    
    # File upload section
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.subheader("📤 Upload Your Files")
    st.markdown("Upload transcripts, slides, or documents (TXT, PDF, JSON formats supported)")
    
    uploaded_files = st.file_uploader(
        "Choose files",
        accept_multiple_files=True,
        type=['txt', 'pdf', 'json'],
        help="You can upload multiple files at once. Supported formats: TXT, PDF, JSON"
    )
    
    # Display uploaded file information
    if uploaded_files:
        display_file_info(uploaded_files)
        st.session_state.uploaded_files = uploaded_files
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Processing section
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Generate Notes", type="primary", disabled=not uploaded_files or st.session_state.processing):
            if uploaded_files:
                process_files(uploaded_files, selected_model, temperature)
            else:
                st.error("Please upload at least one file before generating notes.")
    
    # Progress indicator
    if st.session_state.processing:
        with st.spinner("Processing your files and generating notes..."):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
    
    # Results section
    if st.session_state.generated_notes:
        display_results()

def process_files(uploaded_files, model, temperature):
    """Process uploaded files and generate notes with database tracking"""
    st.session_state.processing = True
    start_time = time.time()
    
    try:
        # Prepare file information for database
        files_info = []
        for uploaded_file in uploaded_files:
            try:
                # Read file content based on type
                if uploaded_file.type == 'text/plain':
                    content = uploaded_file.getvalue().decode('utf-8')
                elif uploaded_file.type == 'application/pdf':
                    # For PDF, we'll let the workflow handle the reading
                    content = f"PDF file: {uploaded_file.name}"
                else:
                    content = str(uploaded_file.getvalue())
                
                files_info.append({
                    'filename': uploaded_file.name,
                    'file_type': uploaded_file.type or uploaded_file.name.split('.')[-1],
                    'file_size': uploaded_file.size,
                    'content': content
                })
            except Exception as e:
                st.error(f"Error reading file {uploaded_file.name}: {str(e)}")
                continue
        
        # Start database session
        db_manager = st.session_state.db_manager
        session_id = db_manager.start_processing_session(model, temperature, files_info)
        
        # Save uploaded files to temporary location
        file_paths = save_uploaded_files(uploaded_files)
        
        # Initialize workflow with user's API key
        workflow = NotetionWorkflow(openai_api_key=st.session_state.api_key)
        workflow.llm.model_name = model
        workflow.llm.temperature = temperature
        
        # Run the workflow
        with st.spinner("Processing files and generating comprehensive notes..."):
            result = workflow.run(file_paths)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Complete database session
        success = not bool(result.get('error_messages'))
        notes_content = result.get('comprehensive_notes', '')
        error_message = '; '.join(result.get('error_messages', [])) if result.get('error_messages') else None
        
        db_manager.complete_processing_session(
            session_id=session_id,
            success=success,
            notes_content=notes_content,
            processing_time=processing_time,
            error_message=error_message
        )
        
        # Store results in session state
        st.session_state.generated_notes = notes_content
        st.session_state.workflow_result = result
        st.session_state.current_session_id = session_id
        
        # Clean up temporary files
        for file_path in file_paths:
            try:
                os.remove(file_path)
            except:
                pass
        
        # Show success message with cost information
        if result.get('error_messages'):
            st.warning("Notes generated with some warnings. Check the details below.")
        else:
            # Get session details for cost display
            session_details = db_manager.get_session_details(session_id)
            if session_details:
                cost = session_details['session']['estimated_cost_usd']
                st.success(f"Notes generated successfully! Estimated cost: ${cost:.4f}")
            else:
                st.success("Notes generated successfully!")
            
    except Exception as e:
        # Complete database session with error
        if 'session_id' in locals():
            db_manager.complete_processing_session(
                session_id=session_id,
                success=False,
                processing_time=time.time() - start_time,
                error_message=str(e)
            )
        
        # Handle API key errors specifically
        if "api_key" in str(e).lower() or "authentication" in str(e).lower():
            st.error("❌ API Key Error: Please check that your OpenAI API key is valid and has sufficient credits.")
        else:
            st.error(f"An error occurred while processing files: {str(e)}")
    
    finally:
        st.session_state.processing = False

def format_notes_for_display(notes_content: str) -> str:
    """Post-process notes to ensure proper markdown formatting"""
    if not notes_content:
        return notes_content
    
    lines = notes_content.split('\n')
    formatted_lines = []
    
    for line in lines:
        original_line = line
        line = line.strip()
        
        if not line:
            formatted_lines.append('')
            continue
        
        # Handle different bullet point symbols
        if line.startswith('•'):
            # Convert • to proper markdown bullet
            line = '- ' + line[1:].strip()
        elif line.startswith('◦'):
            # Convert ◦ to sub-bullet
            line = '  - ' + line[1:].strip()
        elif line.startswith('▪'):
            # Convert ▪ to sub-sub-bullet
            line = '    - ' + line[1:].strip()
        
        # Ensure proper spacing for nested bullets while preserving indentation
        if line.startswith('-') and not line.startswith('- '):
            # Count leading spaces to preserve indentation level
            leading_spaces = len(original_line) - len(original_line.lstrip())
            if leading_spaces >= 4:
                line = '    - ' + line[1:].strip()
            elif leading_spaces >= 2:
                line = '  - ' + line[1:].strip()
            else:
                line = '- ' + line[1:].strip()
        
        # Enhance bold formatting for key terms
        # Look for patterns like "Key term:" or "Important concept" and make them bold
        import re
        
        # Bold terms followed by colons (like "Key factors:")
        line = re.sub(r'^(\s*-\s*)([A-Z][^:]*?):', r'\1**\2**:', line)
        
        # Bold terms in parentheses that look like definitions
        line = re.sub(r'\(([^)]+)\)', lambda m: f'({m.group(1)})', line)
        
        formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def display_results():
    """Display the generated notes and additional options"""
    st.markdown('<div class="notes-section">', unsafe_allow_html=True)
    st.subheader("📋 Generated Notes")
    
    # Display any error messages
    if hasattr(st.session_state, 'workflow_result') and st.session_state.workflow_result.get('error_messages'):
        st.markdown('<div class="error-message">', unsafe_allow_html=True)
        st.write("⚠️ **Warnings/Errors:**")
        for error in st.session_state.workflow_result['error_messages']:
            st.write(f"• {error}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Format and display the notes
    st.markdown("### 📝 Comprehensive Notes")
    formatted_notes = format_notes_for_display(st.session_state.generated_notes)
    
    # Use a styled container for better formatting
    with st.container():
        # Add custom CSS for the notes container
        st.markdown("""
        <style>
        .notes-container {
            background-color: #fafafa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #1f77b4;
            margin: 10px 0;
        }
        .notes-container ul {
            margin-left: 0;
            padding-left: 20px;
        }
        .notes-container li {
            margin-bottom: 8px;
            line-height: 1.6;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Display the formatted notes using Streamlit's markdown
        st.markdown(f'<div class="notes-container">', unsafe_allow_html=True)
        st.markdown(formatted_notes)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Download options
    st.markdown("### 💾 Download Options")
    col1, col2 = st.columns(2)
    
    with col1:
        # Download as Markdown
        st.download_button(
            label="📄 Download as Markdown",
            data=f"# Comprehensive Notes\n\n{st.session_state.generated_notes}",
            file_name="notetion_notes.md",
            mime="text/markdown"
        )
    
    with col2:
        # Download as Text
        st.download_button(
            label="📝 Download as Text",
            data=st.session_state.generated_notes,
            file_name="notetion_notes.txt",
            mime="text/plain"
        )
    
    # Clear results button
    if st.button("🗑️ Clear Results"):
        st.session_state.generated_notes = ""
        st.session_state.workflow_result = None
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_analytics_page():
    """Show analytics and statistics page"""
    st.markdown('<h1 class="main-header">📊 Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    db_manager = st.session_state.db_manager
    analytics = db_manager.get_analytics_summary()
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Sessions", analytics['total_sessions'])
    
    with col2:
        st.metric("Success Rate", f"{analytics['success_rate']:.1f}%")
    
    with col3:
        st.metric("Total Cost", f"${analytics['total_cost_usd']:.4f}")
    
    with col4:
        st.metric("Avg Processing Time", f"{analytics['avg_processing_time_seconds']:.1f}s")
    
    # Token usage
    st.subheader("📈 Token Usage")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Input Tokens", f"{analytics['total_input_tokens']:,}")
    
    with col2:
        st.metric("Total Output Tokens", f"{analytics['total_output_tokens']:,}")
    
    # Model usage chart
    if analytics['model_usage']:
        st.subheader("🤖 Model Usage Distribution")
        model_df = pd.DataFrame(list(analytics['model_usage'].items()), columns=['Model', 'Count'])
        st.bar_chart(model_df.set_index('Model'))
    
    # Recent activity
    st.subheader("📋 Recent Activity")
    recent_sessions = db_manager.get_processing_history(limit=10)
    
    if recent_sessions:
        df = pd.DataFrame(recent_sessions)
        df['created_at'] = pd.to_datetime(df['created_at'])
        df = df[['created_at', 'model_used', 'total_files', 'estimated_cost_usd', 'success', 'processing_time_seconds']]
        df.columns = ['Date', 'Model', 'Files', 'Cost ($)', 'Success', 'Time (s)']
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No processing history available yet.")

def show_history_page():
    """Show processing history page"""
    st.markdown('<h1 class="main-header">📋 Processing History</h1>', unsafe_allow_html=True)
    
    db_manager = st.session_state.db_manager
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        limit = st.selectbox("Show entries", [10, 25, 50, 100], index=1)
    
    with col2:
        model_filter = st.selectbox("Filter by model", ["All"] + ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"])
    
    with col3:
        success_filter = st.selectbox("Filter by status", ["All", "Success", "Failed"])
    
    # Get history
    history = db_manager.get_processing_history(limit=limit)
    
    # Apply filters
    if model_filter != "All":
        history = [h for h in history if h['model_used'] == model_filter]
    
    if success_filter == "Success":
        history = [h for h in history if h['success']]
    elif success_filter == "Failed":
        history = [h for h in history if not h['success']]
    
    if history:
        # Display as expandable cards
        for session in history:
            with st.expander(
                f"📄 {session['created_at'].strftime('%Y-%m-%d %H:%M')} - "
                f"{session['model_used']} - "
                f"{'✅' if session['success'] else '❌'} - "
                f"${session['estimated_cost_usd']:.4f}"
            ):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Session ID:** {session['session_id']}")
                    st.write(f"**Files Processed:** {session['total_files']}")
                    st.write(f"**Processing Time:** {session['processing_time_seconds']:.2f}s")
                    st.write(f"**Input Tokens:** {session['total_input_tokens']:,}")
                    st.write(f"**Output Tokens:** {session['total_output_tokens']:,}")
                
                with col2:
                    st.write(f"**Model:** {session['model_used']}")
                    st.write(f"**Temperature:** {session['temperature']}")
                    st.write(f"**Cost:** ${session['estimated_cost_usd']:.4f}")
                    st.write(f"**Notes Length:** {session['notes_length']:,} chars")
                    if session['error_message']:
                        st.error(f"**Error:** {session['error_message']}")
                
                # View details button
                if st.button(f"View Details", key=f"details_{session['session_id']}"):
                    show_session_details(session['session_id'])
    else:
        st.info("No sessions found matching the selected filters.")

def show_session_details(session_id: str):
    """Show detailed information about a specific session"""
    db_manager = st.session_state.db_manager
    details = db_manager.get_session_details(session_id)
    
    if details:
        st.subheader(f"Session Details: {session_id}")
        
        # Session info
        session = details['session']
        st.write(f"**Created:** {session['created_at']}")
        st.write(f"**Model:** {session['model_used']} (temp: {session['temperature']})")
        st.write(f"**Processing Time:** {session['processing_time_seconds']:.2f} seconds")
        st.write(f"**Cost:** ${session['estimated_cost_usd']:.4f}")
        
        # Files
        st.subheader("📁 Processed Files")
        for file_info in details['files']:
            st.write(f"- **{file_info['filename']}** ({file_info['file_type']}, {file_info['file_size_bytes']:,} bytes)")
            if file_info['content_preview']:
                with st.expander("Preview"):
                    st.text(file_info['content_preview'])
        
        # Notes
        if details['notes']:
            st.subheader("📝 Generated Notes")
            st.markdown(details['notes'])

def show_search_page():
    """Show search page for finding past sessions"""
    st.markdown('<h1 class="main-header">🔍 Search Sessions</h1>', unsafe_allow_html=True)
    
    db_manager = st.session_state.db_manager
    
    # Search form
    with st.form("search_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            query = st.text_input("Search in notes content", placeholder="Enter keywords...")
            model_filter = st.selectbox("Model", ["All"] + ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"])
        
        with col2:
            start_date = st.date_input("Start date", value=datetime.now() - timedelta(days=30))
            end_date = st.date_input("End date", value=datetime.now())
        
        search_button = st.form_submit_button("🔍 Search")
    
    if search_button:
        # Convert dates to datetime
        start_datetime = datetime.combine(start_date, datetime.min.time()) if start_date else None
        end_datetime = datetime.combine(end_date, datetime.max.time()) if end_date else None
        
        # Perform search
        results = db_manager.search_sessions(
            query=query,
            model=model_filter if model_filter != "All" else "",
            start_date=start_datetime,
            end_date=end_datetime
        )
        
        st.subheader(f"Search Results ({len(results)} found)")
        
        if results:
            for session in results:
                with st.expander(
                    f"📄 {session['created_at'].strftime('%Y-%m-%d %H:%M')} - "
                    f"{session['model_used']} - "
                    f"${session['estimated_cost_usd']:.4f}"
                ):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Session ID:** {session['session_id']}")
                        st.write(f"**Files:** {session['total_files']}")
                        st.write(f"**Processing Time:** {session['processing_time_seconds']:.2f}s")
                    
                    with col2:
                        st.write(f"**Model:** {session['model_used']}")
                        st.write(f"**Cost:** ${session['estimated_cost_usd']:.4f}")
                        st.write(f"**Success:** {'✅' if session['success'] else '❌'}")
                    
                    if st.button(f"View Full Details", key=f"search_details_{session['session_id']}"):
                        show_session_details(session['session_id'])
        else:
            st.info("No sessions found matching your search criteria.")

def show_settings_page():
    """Show settings and data management page"""
    st.markdown('<h1 class="main-header">⚙️ Settings & Data Management</h1>', unsafe_allow_html=True)
    
    db_manager = st.session_state.db_manager
    
    # Database info
    st.subheader("🗄️ Database Information")
    analytics = db_manager.get_analytics_summary()
    st.write(f"**Database Location:** {db_manager.db_path}")
    st.write(f"**Total Sessions:** {analytics['total_sessions']}")
    st.write(f"**Total Cost:** ${analytics['total_cost_usd']:.4f}")
    
    # Export data
    st.subheader("📤 Export Data")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export as CSV"):
            try:
                filename = db_manager.export_data('csv')
                st.success(f"Data exported to {filename}")
            except Exception as e:
                st.error(f"Export failed: {str(e)}")
    
    with col2:
        if st.button("📋 Export as JSON"):
            try:
                filename = db_manager.export_data('json')
                st.success(f"Data exported to {filename}")
            except Exception as e:
                st.error(f"Export failed: {str(e)}")
    
    # Data cleanup
    st.subheader("🧹 Data Cleanup")
    st.warning("⚠️ Data cleanup is permanent and cannot be undone!")
    
    days_to_keep = st.number_input("Keep data for how many days?", min_value=1, max_value=365, value=90)
    
    if st.button("🗑️ Clean Old Data", type="secondary"):
        try:
            deleted_count = db_manager.cleanup_old_data(days_to_keep)
            st.success(f"Cleaned up {deleted_count} old sessions.")
        except Exception as e:
            st.error(f"Cleanup failed: {str(e)}")
    
    # API Key information
    st.subheader("🔑 API Key Information")
    st.info("""
    **Your API Key Security:**
    - Your API key is only stored in your browser session
    - It is never saved to disk or transmitted to our servers
    - Each session requires you to re-enter your API key
    - This ensures maximum security for your OpenAI credentials
    """)
    
    # Database statistics
    st.subheader("📈 Database Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Successful Sessions", analytics['successful_sessions'])
    
    with col2:
        st.metric("Average Processing Time", f"{analytics['avg_processing_time_seconds']:.2f}s")
    
    with col3:
        st.metric("Total Tokens Processed", f"{analytics['total_input_tokens'] + analytics['total_output_tokens']:,}")


if __name__ == "__main__":
    main()
