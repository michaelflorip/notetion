# Notetion Database System

A comprehensive database storage and analytics system for the Notetion AI note generation tool.

## Overview

The database system tracks all processing sessions, file uploads, costs, performance metrics, and generated notes. It provides detailed analytics, search capabilities, and data management features.

## Database Schema

### Tables

1. **processing_sessions**
   - Session metadata (ID, timestamps, model, settings)
   - Performance metrics (processing time, token usage)
   - Cost tracking (estimated API costs)
   - Success/failure status

2. **processed_files**
   - File information (name, type, size, hash)
   - Content preview (first 500 characters)
   - Processing status per file

3. **generated_notes**
   - Complete generated notes content
   - Content hash for deduplication
   - Timestamps

## Features

### 📊 Analytics Dashboard
- **Overview Metrics**: Total sessions, success rate, costs, processing times
- **Token Usage**: Input/output token tracking
- **Model Usage**: Distribution of AI model usage
- **Recent Activity**: Latest processing sessions

### 📋 Processing History
- **Filterable History**: View sessions by model, status, date range
- **Detailed Session View**: Complete session information including files and notes
- **Expandable Cards**: Easy-to-browse session summaries

### 🔍 Search Functionality
- **Content Search**: Search within generated notes
- **Advanced Filters**: Filter by model, date range, status
- **Quick Access**: Jump to specific sessions

### ⚙️ Data Management
- **Export Options**: CSV and JSON export formats
- **Data Cleanup**: Remove old sessions (configurable retention)
- **Database Statistics**: Storage and usage metrics

## Cost Tracking

### Pricing Models (as of 2024)
- **GPT-4**: $0.03/1K input tokens, $0.06/1K output tokens
- **GPT-4-Turbo**: $0.01/1K input tokens, $0.03/1K output tokens
- **GPT-3.5-Turbo**: $0.0015/1K input tokens, $0.002/1K output tokens

### Token Counting
- Uses `tiktoken` library for accurate token counting
- Fallback estimation: ~4 characters per token
- Tracks both input and output tokens separately

## Database Operations

### Automatic Tracking
Every processing session automatically records:
- File metadata and content previews
- Processing start/end times
- Token usage and estimated costs
- Success/failure status
- Complete generated notes

### Session Lifecycle
1. **Start Session**: Create session record with file info
2. **Process Files**: Run AI workflow
3. **Complete Session**: Update with results, costs, timing
4. **Store Notes**: Save generated content with hash

### Data Integrity
- **File Hashing**: SHA-256 hashes for deduplication
- **Content Hashing**: Detect duplicate note generation
- **Relationship Integrity**: Foreign key constraints
- **Error Handling**: Graceful failure recording

## Usage Examples

### Basic Usage (Automatic)
```python
# Database tracking happens automatically when using Streamlit interface
# No manual intervention required
```

### Manual Database Operations
```python
from database_manager import DatabaseManager

# Initialize database
db = DatabaseManager("my_notetion.db")

# Get analytics
analytics = db.get_analytics_summary()
print(f"Total cost: ${analytics['total_cost_usd']:.4f}")

# Search sessions
results = db.search_sessions(
    query="machine learning",
    model="gpt-4",
    start_date=datetime(2024, 1, 1)
)

# Export data
filename = db.export_data('csv')
print(f"Data exported to {filename}")

# Cleanup old data
deleted = db.cleanup_old_data(days_to_keep=30)
print(f"Deleted {deleted} old sessions")
```

## File Structure

```
notetion/
├── database_manager.py      # Core database functionality
├── streamlit_app.py         # UI with database integration
├── notetion_history.db      # SQLite database (auto-created)
├── requirements.txt         # Updated with database dependencies
└── README_DATABASE.md       # This documentation
```

## Security & Privacy

### Data Protection
- **Local Storage**: All data stored locally in SQLite
- **No Cloud Sync**: Database never leaves your machine
- **API Key Safety**: Keys not stored in database
- **Content Privacy**: Your notes remain private

### Git Safety
- Database files excluded from version control
- Export files automatically ignored
- Sensitive data protected

## Performance Considerations

### Database Size
- Typical session: ~1-10KB storage
- 1000 sessions: ~1-10MB database
- Notes content: Variable (depends on output length)

### Optimization
- Indexed session IDs for fast lookups
- Efficient queries with SQLAlchemy ORM
- Automatic cleanup options available

## Troubleshooting

### Common Issues

1. **Database Lock Errors**
   - Close other database connections
   - Restart Streamlit application

2. **Missing Dependencies**
   ```bash
   pip install sqlalchemy pandas tiktoken
   ```

3. **Permission Errors**
   - Ensure write permissions in project directory
   - Check database file ownership

4. **Large Database Size**
   - Use cleanup function in Settings page
   - Export and archive old data

### Database Recovery
```python
# If database becomes corrupted
import os
os.remove("notetion_history.db")  # Will be recreated automatically
```

## Future Enhancements

### Planned Features
- **Custom Pricing**: User-configurable API pricing
- **Advanced Analytics**: Trend analysis, cost predictions
- **Data Sync**: Optional cloud backup/sync
- **Batch Operations**: Bulk session management
- **API Access**: REST API for external integrations

### Performance Improvements
- **Database Indexing**: Additional indexes for faster queries
- **Caching**: Session result caching
- **Compression**: Note content compression
- **Archiving**: Automatic old data archiving

## Contributing

When contributing to the database system:

1. **Schema Changes**: Update migration scripts
2. **New Features**: Add corresponding tests
3. **Performance**: Profile database operations
4. **Documentation**: Update this README

## Support

For database-related issues:
1. Check the troubleshooting section
2. Review Streamlit logs for errors
3. Verify database file permissions
4. Test with a fresh database file

The database system is designed to be robust and self-healing, automatically creating tables and handling most common issues transparently.
