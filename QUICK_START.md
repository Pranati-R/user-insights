# Quick Start Guide - AI-Powered File Upload

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: (Optional) Add OpenAI Key

Edit `backend/.env`:
```env
OPENAI_API_KEY=sk-your-api-key-here
```

**Note**: Works without OpenAI using rule-based parsing!

### Step 3: Test the Parser

```bash
# Run tests
pytest backend/tests/test_intelligent_parser.py -v

# Test with sample files
python -c "
from app.services.intelligent_parser import IntelligentLogParser
parser = IntelligentLogParser()

# Test CSV
with open('backend/tests/sample_data/sample_events.csv', 'rb') as f:
    events = parser.parse_file(f.read(), 'test.csv')
    print(f'Parsed {len(events)} events from CSV')

# Test PSI
with open('backend/tests/sample_data/sample_events.psi', 'rb') as f:
    events = parser.parse_file(f.read(), 'test.psi')
    print(f'Parsed {len(events)} events from PSI')
"
```

### Step 4: Upload via Frontend

1. Start backend: `uvicorn app.main:app --reload`
2. Start frontend: `npm run dev`
3. Navigate to File Upload page
4. Drop any supported file (CSV, JSON, PSI, TSV, TXT, LOG)
5. Click "Upload & process"

### Step 5: Upload via API

```bash
# Login first
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.data.access_token')

# Upload file
curl -X POST http://localhost:8000/api/upload-file \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@backend/tests/sample_data/sample_events.csv"
```

## 📋 Supported Formats Cheat Sheet

| Format | Extension | Example |
|--------|-----------|---------|
| CSV | `.csv` | `event,time\nclick,2024-01-01` |
| PSI | `.psi` | `event\|time\nclick\|2024-01-01` |
| TSV | `.tsv` | `event\ttime\nclick\t2024-01-01` |
| JSON | `.json` | `[{"event":"click","time":"2024-01-01"}]` |
| TXT/LOG | `.txt`, `.log` | Auto-detected delimiter |

## 🎯 Field Mapping Quick Reference

Your logs can use any of these field names:

```python
# Event Type
"event_type", "type", "event", "action", "event_name", "name"

# Timestamp
"timestamp", "time", "datetime", "date", "created_at", "event_time"

# Session ID
"session_id", "sessionid", "session", "sid", "session_key"

# Page/URL
"page", "url", "path", "page_url", "page_path", "pathname", "location"

# Website
"website", "site", "domain", "host", "hostname", "origin"

# Scroll Depth
"scroll_depth", "scroll", "scroll_percentage", "scroll_pct"
```

## 💡 Common Use Cases

### Use Case 1: Upload Library Logs

Your library logs look like this:
```
timestamp|event|url|session
2024-11-25T12:00:00Z|pageview|/home|sess_123
```

Just upload the `.psi` file - it will automatically:
- ✅ Detect pipe delimiter
- ✅ Map `event` → `event_type`
- ✅ Map `url` → `page`
- ✅ Normalize `pageview` → `page_view`

### Use Case 2: Upload Custom CSV

Your CSV has different column names:
```csv
time,type,path,sid
2024-11-25T12:00:00Z,view,/home,s1
```

Just upload - it will automatically:
- ✅ Map `time` → `timestamp`
- ✅ Map `path` → `page`
- ✅ Map `sid` → `session_id`
- ✅ Normalize `view` → `page_view`

### Use Case 3: Upload JSON Logs

Your JSON is wrapped:
```json
{
  "logs": [
    {"time": "2024-11-25T12:00:00Z", "type": "click"}
  ]
}
```

Just upload - it will automatically:
- ✅ Unwrap the array
- ✅ Map fields intelligently
- ✅ Handle nested structures

## 🔧 Troubleshooting

### Error: "No valid events found"
**Solution**: Ensure your file has:
- ✅ Column headers (for CSV/PSI/TSV)
- ✅ At least one data row
- ✅ Valid timestamp format

### Error: "Failed to parse delimited file"
**Solution**:
- ✅ Check delimiter consistency
- ✅ Escape special characters in values
- ✅ Use UTF-8 encoding

### Error: "Invalid JSON structure"
**Solution**:
- ✅ Validate JSON syntax
- ✅ Ensure it's an array or has "events" key
- ✅ Check for trailing commas

## 📚 Next Steps

- Read [FILE_UPLOAD_GUIDE.md](FILE_UPLOAD_GUIDE.md) for detailed documentation
- Check [IMPROVEMENTS_SUGGESTIONS.md](IMPROVEMENTS_SUGGESTIONS.md) for roadmap
- Review [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for technical details

## 🎓 Code Examples

### Python: Parse a File Programmatically

```python
from app.services.intelligent_parser import IntelligentLogParser

parser = IntelligentLogParser()

# Read file
with open('your_logs.csv', 'rb') as f:
    contents = f.read()

# Parse
events = parser.parse_file(contents, 'your_logs.csv')

# Normalize each event
normalized_events = [
    parser.normalize_log_entry(event) 
    for event in events
]

print(f"Parsed {len(normalized_events)} events")
```

### Python: Test Different Formats

```python
# Test CSV
csv_data = b"event,time\nclick,2024-01-01T12:00:00Z"
events = parser.parse_file(csv_data, "test.csv")

# Test PSI
psi_data = b"event|time\nclick|2024-01-01T12:00:00Z"
events = parser.parse_file(psi_data, "test.psi")

# Test JSON
json_data = b'[{"event":"click","time":"2024-01-01T12:00:00Z"}]'
events = parser.parse_file(json_data, "test.json")
```

### JavaScript: Upload from Frontend

```typescript
const uploadFile = async (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await fetch('/api/upload-file', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  })
  
  const result = await response.json()
  console.log(`Ingested ${result.data.ingested_events} events`)
}
```

## ⚡ Performance Tips

1. **Large Files**: Split into chunks (<50MB each)
2. **Many Files**: Upload sequentially to avoid memory issues
3. **Slow Parsing**: Check file encoding (UTF-8 is fastest)
4. **High Error Rate**: Validate timestamp format first

## 🎉 You're Ready!

Start uploading logs from any source - the system will handle the rest!

**Questions?** Check the detailed guides or run the tests for examples.
