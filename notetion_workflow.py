"""
Notetion LangGraph Workflow
A LangGraph-based workflow for processing transcripts and slides to generate comprehensive notes.
"""

import os
import json
from typing import List, Dict, Any, TypedDict
from pathlib import Path
import PyPDF2
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END


class WorkflowState(TypedDict):
    """State object for the notetion workflow"""
    input_files: List[str]
    file_contents: Dict[str, str]
    processed_content: str
    comprehensive_notes: str
    error_messages: List[str]


class NotetionWorkflow:
    """Main workflow class for processing files and generating notes"""
    
    def __init__(self, openai_api_key: str = None):
        """Initialize the workflow with LLM configuration"""
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3,
            api_key=openai_api_key or os.getenv("OPENAI_API_KEY")
        )
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("file_reader", self.read_files)
        workflow.add_node("content_processor", self.process_content)
        workflow.add_node("note_generator", self.generate_notes)
        
        # Add edges
        workflow.add_edge("file_reader", "content_processor")
        workflow.add_edge("content_processor", "note_generator")
        workflow.add_edge("note_generator", END)
        
        # Set entry point
        workflow.set_entry_point("file_reader")
        
        return workflow.compile()
    
    def read_files(self, state: WorkflowState) -> WorkflowState:
        """Read and extract content from input files"""
        file_contents = {}
        error_messages = state.get("error_messages", [])
        
        for file_path in state["input_files"]:
            try:
                content = self._extract_file_content(file_path)
                file_contents[file_path] = content
            except Exception as e:
                error_msg = f"Error reading {file_path}: {str(e)}"
                error_messages.append(error_msg)
                print(error_msg)
        
        return {
            **state,
            "file_contents": file_contents,
            "error_messages": error_messages
        }
    
    def _extract_file_content(self, file_path: str) -> str:
        """Extract content from different file types"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.suffix.lower() == '.txt':
            return self._read_txt_file(file_path)
        elif file_path.suffix.lower() == '.pdf':
            return self._read_pdf_file(file_path)
        elif file_path.suffix.lower() == '.json':
            return self._read_json_file(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
    
    def _read_txt_file(self, file_path: Path) -> str:
        """Read content from text file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _read_pdf_file(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _read_json_file(self, file_path: Path) -> str:
        """Read and format JSON file content"""
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            # Convert JSON to readable text format
            return json.dumps(data, indent=2)
    
    def process_content(self, state: WorkflowState) -> WorkflowState:
        """Process and combine content from all files"""
        combined_content = ""
        
        for file_path, content in state["file_contents"].items():
            combined_content += f"\n{'='*50}\n"
            combined_content += f"FILE: {file_path}\n"
            combined_content += f"{'='*50}\n"
            combined_content += content + "\n"
        
        return {
            **state,
            "processed_content": combined_content
        }
    
    def generate_notes(self, state: WorkflowState) -> WorkflowState:
        """Generate comprehensive bullet-format notes using LLM"""
        system_prompt = """
        You are an expert note-taker and content synthesizer. Your task is to create comprehensive, 
        well-organized lecture-style notes from the provided content using proper Markdown formatting.
        
        CRITICAL FORMATTING REQUIREMENTS:
        1. Start with a main title using "# " (single hash + space)
        2. Use "## " for major section headers (like "Agenda", "Key Concepts", etc.)
        3. Use numbered sections "### 1. Section Name" for main topics
        4. Use proper Markdown bullet points with "- " (dash + space) for main points
        5. Use "  - " (two spaces + dash + space) for sub-points
        6. Use "    - " (four spaces + dash + space) for sub-sub-points
        7. **Bold** key terms, concepts, and important phrases
        8. Use *italics* for emphasis and clarification
        9. Include parenthetical explanations and examples in regular text
        10. Leave blank lines between major sections for readability
        11. Use colons after key terms when introducing lists or explanations
        
        CONTENT STRUCTURE:
        1. Create a clear title that summarizes the main topic
        2. Include an "Agenda" or "Overview" section if multiple topics are covered
        3. Organize content into numbered main sections
        4. Use hierarchical bullet points within each section
        5. Bold all key terms, concepts, and important phrases
        6. Include specific details, examples, and explanations
        7. Add parenthetical clarifications where helpful
        
        EXAMPLE FORMAT:
        # Lecture Title: Main Topic Name
        
        ## Agenda
        
        - **Key concept 1** (brief explanation; important details)
        - **Key concept 2** (conditional expectation; potential outcomes)
        - **Statistical methods** (standard errors, confidence intervals, tests)
        - **Important factors**:
          - **Study design** (crucial for causal inference)
          - **Sample size** (affects precision)
          - **Data quality** (does not fix bias)
        - **Practical application**:
          - **Pre-treatment analysis** (Table 1.3)
          - **Causal effects** on outcomes (Table 1.4)
        
        ### 1. Main Section Name
        
        - **Key term** mentioned in context but reserved for advanced topics
        - **Important concept** (detailed explanation with examples)
          - **Sub-concept**: Specific detail or clarification
          - **Another aspect**: Additional information
        - **Practical application**:
          - **Method 1** (explanation of approach)
          - **Method 2** (alternative approach)
        
        ### 2. Another Main Section
        
        - **Core principle**: Explanation with context
        - **Implementation details**:
          - **Step 1**: Specific action required
          - **Step 2**: Follow-up procedures
        
        Format your response as comprehensive, properly formatted lecture-style notes with clear hierarchy and extensive use of bold formatting for key terms.
        """
        
        user_prompt = f"""
        Please create comprehensive bullet-format notes from the following content:
        
        {state['processed_content']}
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            comprehensive_notes = response.content
        except Exception as e:
            error_msg = f"Error generating notes: {str(e)}"
            comprehensive_notes = f"Failed to generate notes due to error: {error_msg}"
            state["error_messages"].append(error_msg)
        
        return {
            **state,
            "comprehensive_notes": comprehensive_notes
        }
    
    def run(self, input_files: List[str]) -> Dict[str, Any]:
        """Run the complete workflow"""
        initial_state = {
            "input_files": input_files,
            "file_contents": {},
            "processed_content": "",
            "comprehensive_notes": "",
            "error_messages": []
        }
        
        result = self.workflow.invoke(initial_state)
        return result


def main():
    """Example usage of the Notetion workflow"""
    # Initialize workflow
    workflow = NotetionWorkflow()
    
    # Example file paths (replace with actual file paths)
    input_files = [
        "example_transcript.txt",
        "example_slides.pdf",
        "example_data.json"
    ]
    
    # Run workflow
    print("Starting Notetion workflow...")
    result = workflow.run(input_files)
    
    # Display results
    if result["error_messages"]:
        print("\nErrors encountered:")
        for error in result["error_messages"]:
            print(f"- {error}")
    
    print("\n" + "="*60)
    print("COMPREHENSIVE NOTES")
    print("="*60)
    print(result["comprehensive_notes"])
    
    # Optionally save notes to file
    with open("generated_notes.md", "w", encoding="utf-8") as f:
        f.write("# Comprehensive Notes\n\n")
        f.write(result["comprehensive_notes"])
    
    print(f"\nNotes saved to: generated_notes.md")


if __name__ == "__main__":
    main()
