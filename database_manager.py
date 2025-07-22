"""
Database Manager for Notetion
Handles storage and retrieval of processing history, costs, and analytics.
"""

import os
import sqlite3
import json
import hashlib
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import tiktoken

Base = declarative_base()

class ProcessingSession(Base):
    """Table for storing processing session information"""
    __tablename__ = 'processing_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    model_used = Column(String(50), nullable=False)
    temperature = Column(Float, nullable=False)
    total_files = Column(Integer, nullable=False)
    processing_time_seconds = Column(Float, nullable=False)
    total_input_tokens = Column(Integer, nullable=False)
    total_output_tokens = Column(Integer, nullable=False)
    estimated_cost_usd = Column(Float, nullable=False)
    success = Column(Boolean, nullable=False)
    error_message = Column(Text, nullable=True)
    notes_length = Column(Integer, nullable=False)
    
    # Relationships
    files = relationship("ProcessedFile", back_populates="session")

class ProcessedFile(Base):
    """Table for storing information about processed files"""
    __tablename__ = 'processed_files'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey('processing_sessions.session_id'), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    file_hash = Column(String(64), nullable=False)  # SHA-256 hash for deduplication
    content_preview = Column(Text, nullable=True)  # First 500 chars
    processing_success = Column(Boolean, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    session = relationship("ProcessingSession", back_populates="files")

class GeneratedNotes(Base):
    """Table for storing generated notes"""
    __tablename__ = 'generated_notes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey('processing_sessions.session_id'), nullable=False)
    notes_content = Column(Text, nullable=False)
    notes_hash = Column(String(64), nullable=False)  # For deduplication
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

class DatabaseManager:
    """Main database manager class"""
    
    # OpenAI pricing (as of 2024 - update as needed)
    PRICING = {
        'gpt-4': {'input': 0.03, 'output': 0.06},  # per 1K tokens
        'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
        'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002},
    }
    
    def __init__(self, db_path: str = "notetion_history.db"):
        """Initialize database manager"""
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
    def generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now(timezone.utc).isoformat()
        return hashlib.sha256(timestamp.encode()).hexdigest()[:16]
    
    def calculate_file_hash(self, content: str) -> str:
        """Calculate SHA-256 hash of file content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def count_tokens(self, text: str, model: str = "gpt-4") -> int:
        """Count tokens in text using tiktoken"""
        try:
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except Exception:
            # Fallback estimation: ~4 chars per token
            return len(text) // 4
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Estimate API cost based on token usage"""
        if model not in self.PRICING:
            model = 'gpt-4'  # Default fallback
        
        pricing = self.PRICING[model]
        input_cost = (input_tokens / 1000) * pricing['input']
        output_cost = (output_tokens / 1000) * pricing['output']
        return round(input_cost + output_cost, 6)
    
    def start_processing_session(self, model: str, temperature: float, files_info: List[Dict]) -> str:
        """Start a new processing session and return session ID"""
        session_id = self.generate_session_id()
        
        # Calculate total input tokens from all files
        total_input_tokens = 0
        for file_info in files_info:
            content = file_info.get('content', '')
            total_input_tokens += self.count_tokens(content, model)
        
        # Create session record (will be updated when processing completes)
        session = ProcessingSession(
            session_id=session_id,
            model_used=model,
            temperature=temperature,
            total_files=len(files_info),
            processing_time_seconds=0,  # Will be updated
            total_input_tokens=total_input_tokens,
            total_output_tokens=0,  # Will be updated
            estimated_cost_usd=0,  # Will be updated
            success=False,  # Will be updated
            notes_length=0  # Will be updated
        )
        
        self.session.add(session)
        
        # Add file records
        for file_info in files_info:
            content = file_info.get('content', '')
            file_record = ProcessedFile(
                session_id=session_id,
                filename=file_info['filename'],
                file_type=file_info['file_type'],
                file_size_bytes=file_info['file_size'],
                file_hash=self.calculate_file_hash(content),
                content_preview=content[:500] if content else None,
                processing_success=True,  # Assume success for now
                error_message=None
            )
            self.session.add(file_record)
        
        self.session.commit()
        return session_id
    
    def complete_processing_session(self, session_id: str, success: bool, 
                                  notes_content: str = "", processing_time: float = 0,
                                  error_message: str = None):
        """Complete a processing session with results"""
        session = self.session.query(ProcessingSession).filter_by(session_id=session_id).first()
        if not session:
            return
        
        # Count output tokens
        output_tokens = self.count_tokens(notes_content, session.model_used) if notes_content else 0
        
        # Calculate cost
        estimated_cost = self.estimate_cost(
            session.total_input_tokens, 
            output_tokens, 
            session.model_used
        )
        
        # Update session
        session.success = success
        session.processing_time_seconds = processing_time
        session.total_output_tokens = output_tokens
        session.estimated_cost_usd = estimated_cost
        session.notes_length = len(notes_content) if notes_content else 0
        session.error_message = error_message
        
        # Save notes if successful
        if success and notes_content:
            notes_record = GeneratedNotes(
                session_id=session_id,
                notes_content=notes_content,
                notes_hash=self.calculate_file_hash(notes_content)
            )
            self.session.add(notes_record)
        
        self.session.commit()
    
    def get_processing_history(self, limit: int = 50) -> List[Dict]:
        """Get processing history with summary statistics"""
        sessions = self.session.query(ProcessingSession)\
                              .order_by(ProcessingSession.created_at.desc())\
                              .limit(limit).all()
        
        history = []
        for session in sessions:
            history.append({
                'session_id': session.session_id,
                'created_at': session.created_at,
                'model_used': session.model_used,
                'temperature': session.temperature,
                'total_files': session.total_files,
                'processing_time_seconds': session.processing_time_seconds,
                'total_input_tokens': session.total_input_tokens,
                'total_output_tokens': session.total_output_tokens,
                'estimated_cost_usd': session.estimated_cost_usd,
                'success': session.success,
                'notes_length': session.notes_length,
                'error_message': session.error_message
            })
        
        return history
    
    def get_session_details(self, session_id: str) -> Optional[Dict]:
        """Get detailed information about a specific session"""
        session = self.session.query(ProcessingSession).filter_by(session_id=session_id).first()
        if not session:
            return None
        
        # Get files for this session
        files = self.session.query(ProcessedFile).filter_by(session_id=session_id).all()
        
        # Get notes for this session
        notes = self.session.query(GeneratedNotes).filter_by(session_id=session_id).first()
        
        return {
            'session': {
                'session_id': session.session_id,
                'created_at': session.created_at,
                'model_used': session.model_used,
                'temperature': session.temperature,
                'total_files': session.total_files,
                'processing_time_seconds': session.processing_time_seconds,
                'total_input_tokens': session.total_input_tokens,
                'total_output_tokens': session.total_output_tokens,
                'estimated_cost_usd': session.estimated_cost_usd,
                'success': session.success,
                'notes_length': session.notes_length,
                'error_message': session.error_message
            },
            'files': [{
                'filename': f.filename,
                'file_type': f.file_type,
                'file_size_bytes': f.file_size_bytes,
                'content_preview': f.content_preview,
                'processing_success': f.processing_success,
                'error_message': f.error_message
            } for f in files],
            'notes': notes.notes_content if notes else None
        }
    
    def get_analytics_summary(self) -> Dict:
        """Get analytics summary"""
        total_sessions = self.session.query(ProcessingSession).count()
        successful_sessions = self.session.query(ProcessingSession).filter_by(success=True).count()
        
        # Cost analytics
        total_cost = self.session.query(ProcessingSession.estimated_cost_usd).all()
        total_cost_sum = sum([cost[0] for cost in total_cost if cost[0]])
        
        # Token analytics
        total_input_tokens = self.session.query(ProcessingSession.total_input_tokens).all()
        total_output_tokens = self.session.query(ProcessingSession.total_output_tokens).all()
        
        total_input_sum = sum([tokens[0] for tokens in total_input_tokens if tokens[0]])
        total_output_sum = sum([tokens[0] for tokens in total_output_tokens if tokens[0]])
        
        # Processing time analytics
        processing_times = self.session.query(ProcessingSession.processing_time_seconds).all()
        avg_processing_time = sum([time[0] for time in processing_times if time[0]]) / len(processing_times) if processing_times else 0
        
        # Model usage
        model_usage = {}
        models = self.session.query(ProcessingSession.model_used).all()
        for model in models:
            model_name = model[0]
            model_usage[model_name] = model_usage.get(model_name, 0) + 1
        
        return {
            'total_sessions': total_sessions,
            'successful_sessions': successful_sessions,
            'success_rate': (successful_sessions / total_sessions * 100) if total_sessions > 0 else 0,
            'total_cost_usd': round(total_cost_sum, 4),
            'total_input_tokens': total_input_sum,
            'total_output_tokens': total_output_sum,
            'avg_processing_time_seconds': round(avg_processing_time, 2),
            'model_usage': model_usage
        }
    
    def search_sessions(self, query: str = "", model: str = "", 
                       start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """Search sessions with filters"""
        query_obj = self.session.query(ProcessingSession)
        
        if model:
            query_obj = query_obj.filter(ProcessingSession.model_used == model)
        
        if start_date:
            query_obj = query_obj.filter(ProcessingSession.created_at >= start_date)
        
        if end_date:
            query_obj = query_obj.filter(ProcessingSession.created_at <= end_date)
        
        sessions = query_obj.order_by(ProcessingSession.created_at.desc()).all()
        
        # If there's a text query, filter by notes content
        if query:
            filtered_sessions = []
            for session in sessions:
                notes = self.session.query(GeneratedNotes).filter_by(session_id=session.session_id).first()
                if notes and query.lower() in notes.notes_content.lower():
                    filtered_sessions.append(session)
            sessions = filtered_sessions
        
        return [{
            'session_id': session.session_id,
            'created_at': session.created_at,
            'model_used': session.model_used,
            'temperature': session.temperature,
            'total_files': session.total_files,
            'processing_time_seconds': session.processing_time_seconds,
            'estimated_cost_usd': session.estimated_cost_usd,
            'success': session.success,
            'notes_length': session.notes_length
        } for session in sessions]
    
    def export_data(self, format: str = 'csv') -> str:
        """Export data to CSV or JSON"""
        sessions = self.get_processing_history(limit=1000)  # Get more for export
        
        if format.lower() == 'csv':
            df = pd.DataFrame(sessions)
            filename = f"notetion_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            return filename
        elif format.lower() == 'json':
            filename = f"notetion_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(sessions, f, indent=2, default=str)
            return filename
        else:
            raise ValueError("Format must be 'csv' or 'json'")
    
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old data beyond specified days"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
        
        # Delete old sessions and related data
        old_sessions = self.session.query(ProcessingSession)\
                                  .filter(ProcessingSession.created_at < cutoff_date).all()
        
        for session in old_sessions:
            # Delete related files and notes
            self.session.query(ProcessedFile).filter_by(session_id=session.session_id).delete()
            self.session.query(GeneratedNotes).filter_by(session_id=session.session_id).delete()
            self.session.delete(session)
        
        self.session.commit()
        return len(old_sessions)
    
    def close(self):
        """Close database connection"""
        self.session.close()

# Utility functions
def get_file_info(uploaded_file) -> Dict:
    """Extract file information from Streamlit uploaded file"""
    return {
        'filename': uploaded_file.name,
        'file_type': uploaded_file.type or uploaded_file.name.split('.')[-1],
        'file_size': uploaded_file.size,
        'content': uploaded_file.getvalue().decode('utf-8') if uploaded_file.type == 'text/plain' else str(uploaded_file.getvalue())
    }
