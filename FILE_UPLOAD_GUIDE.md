# File Upload Guide - AI-Powered Log Parsing

## Overview

The UserInsight AI platform now supports **intelligent, multi-format log file uploads** with AI-powered parsing and normalization. This allows you to import logs from various sources without manual preprocessing.

## Supported File Formats

### 1. **CSV (Comma-Separated Values)**
- Standard comma-delimited files
- Example: `events.csv`

### 2. **PSI (Pipe-Separated Values)**
- Pipe-delimited files (common in many logging systems)
- Example: `logs.psi`

### 3. **TSV (Tab-Separated Values)**
- Tab-delimited files
- Example: `data.tsv`

### 4. **JSON**
- Standard JSON format
- Supports both array of objects and wrapped formats
- Example: `events.json`

### 5. **TXT/LOG**
- Plain text log files with auto-detected delimiters
- Example: `application.log`, `events.txt`

## Features

### 🤖 AI-Powered Normalization
- Automatically detects and maps different field names to the standard schema
- Handles variations like: `time` → `timestamp`, `url` → `page`, etc.
- Infers event types from log content when not explicitly provided

### 🔍 Intelligent Detection
- **Encoding Detection**: Automatically detects file encoding (UTF-8, Latin-1, etc.)
- **Delimiter Detection**: Identifies comma, pipe, tab, semicolon, or custom delimiters
- **Format Detection**: Determines file format from extension and content
- **Field Mapping**: Maps various field name variations to standard schema

### 📊 Standard Schema

The system normalizes all logs to this schema:

```json
{
  "event_type": "page_view | click | action | scroll",
  "timestamp": "2024-11-25T12:00:00Z",
  "session_id": "optional-session-identifier",
  "page": "/path/to/page",
  "website": "example.com",
  "scroll_depth": 75.5,
  "metadata": {
    "additional": "fields",
    "custom": "data"
  }
}
```

## Field Mapping Examples

The intelligent parser recognizes many field name variations:

| Standard Field | Recognized Variations |
|---------------|----------------------|
| `event_type` | type, event, action, event_name, name |
| `timestamp` | time, datetime, date, created_at, event_time |
| `session_id` | sessionid, session, sid, session_key |
| `page` | url, path, page_url, page_path, pathname, location |
| `website` | site, domain, host, hostname, origin |
| `scroll_depth` | scroll, scroll_percentage, scroll_pct |

## Example File Formats

### CSV Example
```csv
timestamp,event_type,page,session_id,metadata
2024-11-25T12:00:00Z,page_view,/home,sess_123,"{""browser"":""Chrome""}"
2024-11-25T12:01:00Z,click,/products,sess_123,"{""element"":""buy_button""}"
```

### PSI (Pipe-Separated) Example
```
timestamp|type|url|session|browser|action
2024-11-25T12:00:00Z|pageview|/home|sess_123|Chrome|view
2024-11-25T12:01:00Z|click|/products|sess_123|Chrome|button_click
```

### JSON Example
```json
{
  "events": [
    {
      "time": "2024-11-25T12:00:00Z",
      "type": "page_view",
      "url": "/home",
      "session": "sess_123",
      "metadata": {"browser": "Chrome"}
    }
  ]
}
```

### Library Log Example (Auto-detected)
Even if your logs come from different libraries with different formats:

```
[2024-11-25 12:00:00] INFO: User visited /home | session=sess_123 | browser=Chrome
[2024-11-25 12:01:00] INFO: User clicked button | session=sess_123 | element=buy_button
```

The AI parser will:
1. Detect the format and structure
2. Extract relevant fields
3. Map them to the standard schema
4. Infer event types from context

## Configuration

### Optional: Groq AI Integration

For enhanced AI-powered field mapping, add your Groq API key to `.env`:

```env
GROQ_API_KEY=gsk_your-api-key-here
```

**Get your free API key**: https://console.groq.com/

**Note**: The system works without Groq using rule-based parsing. Groq AI enhances accuracy for unusual log formats and is faster than OpenAI.

## Upload Limits

- **Max File Size**: 50 MB
- **Recommended**: Split larger files into chunks for faster processing

## Error Handling

The system is resilient:
- **Partial Success**: Processes valid events even if some fail
- **Detailed Errors**: Provides specific error messages for troubleshooting
- **Fallback Values**: Uses sensible defaults when fields are missing
  - Missing `event_type`: Inferred from other fields
  - Missing `timestamp`: Uses current time
  - Missing `session_id`: Generated automatically

## Best Practices

1. **Include Headers**: For CSV/PSI/TSV files, include column headers
2. **Consistent Timestamps**: Use ISO 8601 format when possible
3. **Test Small First**: Upload a small sample to verify format compatibility
4. **Check Results**: Review the ingested events count and summary after upload

## Troubleshooting

### "No valid events found"
- Check that your file has data rows (not just headers)
- Verify timestamp format is parseable
- Ensure at least one field maps to the standard schema

### "Failed to parse delimited file"
- Check for consistent delimiter usage
- Verify no unescaped delimiters in field values
- Try saving with UTF-8 encoding

### "Invalid JSON structure"
- Validate JSON syntax using a JSON validator
- Ensure it's either an array or object with an "events" key

## API Endpoint

```http
POST /api/upload-file
Content-Type: multipart/form-data
Authorization: Bearer <token>

file: <binary file data>
```

**Response**:
```json
{
  "success": true,
  "data": {
    "ingested_events": 1250,
    "summary": {
      "total_events": 5000,
      "total_sessions": 150,
      "anomaly_rate": 2.5,
      "last_event_at": "2024-11-25T12:00:00Z",
      "top_pages": [...]
    }
  }
}
```

## Technical Details

### Parser Architecture

1. **Encoding Detection** (chardet)
2. **Format Detection** (extension + content analysis)
3. **Delimiter Detection** (statistical analysis)
4. **Parsing** (pandas + custom parsers)
5. **Normalization** (rule-based + optional AI)
6. **Validation** (Pydantic schemas)
7. **Ingestion** (MongoDB + sessionization)

### Dependencies

- `pandas`: Data parsing and manipulation
- `chardet`: Encoding detection
- `groq`: AI-powered field mapping (optional, faster than OpenAI)
- `python-magic-bin`: File type detection

## Future Enhancements

- [ ] Support for compressed files (.zip, .gz)
- [ ] Real-time streaming for large files
- [ ] Custom field mapping UI
- [ ] Log format templates library
- [ ] Batch upload API
- [ ] Preview before import
