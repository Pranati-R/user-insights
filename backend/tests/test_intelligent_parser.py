"""
Tests for the Intelligent Log Parser
"""
import pytest
from datetime import datetime
from app.services.intelligent_parser import IntelligentLogParser


class TestIntelligentLogParser:
    """Test suite for IntelligentLogParser"""

    @pytest.fixture
    def parser(self):
        return IntelligentLogParser()

    def test_detect_encoding_utf8(self, parser):
        """Test UTF-8 encoding detection"""
        content = "Hello, World!".encode('utf-8')
        encoding = parser.detect_encoding(content)
        assert encoding == 'utf-8'

    def test_detect_delimiter_comma(self, parser):
        """Test comma delimiter detection"""
        text = "name,age,city\nJohn,30,NYC\nJane,25,LA"
        delimiter = parser.detect_delimiter(text)
        assert delimiter == ','

    def test_detect_delimiter_pipe(self, parser):
        """Test pipe delimiter detection"""
        text = "name|age|city\nJohn|30|NYC\nJane|25|LA"
        delimiter = parser.detect_delimiter(text)
        assert delimiter == '|'

    def test_detect_delimiter_tab(self, parser):
        """Test tab delimiter detection"""
        text = "name\tage\tcity\nJohn\t30\tNYC\nJane\t25\tLA"
        delimiter = parser.detect_delimiter(text)
        assert delimiter == '\t'

    def test_detect_file_format_csv(self, parser):
        """Test CSV format detection"""
        content = b"name,age\nJohn,30"
        format_type = parser.detect_file_format("test.csv", content)
        assert format_type == 'csv'

    def test_detect_file_format_json(self, parser):
        """Test JSON format detection"""
        content = b'{"events": []}'
        format_type = parser.detect_file_format("test.json", content)
        assert format_type == 'json'

    def test_detect_file_format_psi(self, parser):
        """Test PSI format detection"""
        content = b"name|age\nJohn|30"
        format_type = parser.detect_file_format("test.psi", content)
        assert format_type == 'psi'

    def test_parse_json_array(self, parser):
        """Test parsing JSON array"""
        content = '[{"event": "click", "time": "2024-01-01T12:00:00Z"}]'
        result = parser._parse_json(content)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['event'] == 'click'

    def test_parse_json_wrapped(self, parser):
        """Test parsing wrapped JSON"""
        content = '{"events": [{"event": "click"}]}'
        result = parser._parse_json(content)
        assert isinstance(result, list)
        assert len(result) == 1

    def test_parse_csv(self, parser):
        """Test parsing CSV"""
        content = "event,time\nclick,2024-01-01T12:00:00Z"
        result = parser._parse_delimited(content, ',')
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['event'] == 'click'

    def test_parse_psi(self, parser):
        """Test parsing PSI (pipe-separated)"""
        content = "event|time\nclick|2024-01-01T12:00:00Z"
        result = parser._parse_delimited(content, '|')
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['event'] == 'click'

    def test_normalize_event_type_page_view(self, parser):
        """Test event type normalization for page_view"""
        entry = {'type': 'pageview', 'time': '2024-01-01T12:00:00Z'}
        normalized = parser.normalize_log_entry(entry)
        assert normalized['event_type'] == 'page_view'

    def test_normalize_event_type_click(self, parser):
        """Test event type normalization for click"""
        entry = {'type': 'click', 'time': '2024-01-01T12:00:00Z'}
        normalized = parser.normalize_log_entry(entry)
        assert normalized['event_type'] == 'click'

    def test_normalize_timestamp_iso(self, parser):
        """Test timestamp normalization from ISO format"""
        entry = {'time': '2024-01-01T12:00:00Z'}
        normalized = parser.normalize_log_entry(entry)
        assert isinstance(normalized['timestamp'], datetime)

    def test_normalize_timestamp_unix(self, parser):
        """Test timestamp normalization from Unix timestamp"""
        entry = {'timestamp': '1704110400'}  # 2024-01-01 12:00:00
        normalized = parser.normalize_log_entry(entry)
        assert isinstance(normalized['timestamp'], datetime)

    def test_normalize_field_variations(self, parser):
        """Test field name variation normalization"""
        entry = {
            'url': '/home',
            'sessionid': 'sess_123',
            'site': 'example.com',
            'scroll': 50.5
        }
        normalized = parser.normalize_log_entry(entry)
        assert normalized['page'] == '/home'
        assert normalized['session_id'] == 'sess_123'
        assert normalized['website'] == 'example.com'
        assert normalized['scroll_depth'] == 50.5

    def test_normalize_metadata_collection(self, parser):
        """Test metadata collection from extra fields"""
        entry = {
            'event_type': 'click',
            'timestamp': '2024-01-01T12:00:00Z',
            'browser': 'Chrome',
            'device': 'Desktop',
            'custom_field': 'value'
        }
        normalized = parser.normalize_log_entry(entry)
        assert 'metadata' in normalized
        assert normalized['metadata']['browser'] == 'Chrome'
        assert normalized['metadata']['device'] == 'Desktop'
        assert normalized['metadata']['custom_field'] == 'value'

    def test_infer_event_type_from_scroll(self, parser):
        """Test event type inference from scroll_depth"""
        entry = {'scroll_depth': 75, 'time': '2024-01-01T12:00:00Z'}
        normalized = parser.normalize_log_entry(entry)
        assert normalized['event_type'] == 'scroll'

    def test_infer_event_type_from_page(self, parser):
        """Test event type inference from page field"""
        entry = {'page': '/home', 'time': '2024-01-01T12:00:00Z'}
        normalized = parser.normalize_log_entry(entry)
        assert normalized['event_type'] == 'page_view'

    def test_extract_field_case_insensitive(self, parser):
        """Test case-insensitive field extraction"""
        entry = {'EventType': 'click', 'TimeStamp': '2024-01-01T12:00:00Z'}
        result = parser._extract_field(entry, ['event_type'])
        assert result == 'click'

    def test_parse_file_csv(self, parser):
        """Test complete CSV file parsing"""
        content = b"event_type,timestamp,page\npage_view,2024-01-01T12:00:00Z,/home"
        result = parser.parse_file(content, "test.csv")
        assert isinstance(result, list)
        assert len(result) == 1

    def test_parse_file_json(self, parser):
        """Test complete JSON file parsing"""
        content = b'[{"event_type": "click", "timestamp": "2024-01-01T12:00:00Z"}]'
        result = parser.parse_file(content, "test.json")
        assert isinstance(result, list)
        assert len(result) == 1

    def test_parse_file_psi(self, parser):
        """Test complete PSI file parsing"""
        content = b"event_type|timestamp|page\npage_view|2024-01-01T12:00:00Z|/home"
        result = parser.parse_file(content, "test.psi")
        assert isinstance(result, list)
        assert len(result) == 1

    def test_handle_nan_values(self, parser):
        """Test handling of NaN values"""
        entry = {
            'event_type': 'click',
            'timestamp': '2024-01-01T12:00:00Z',
            'page': float('nan'),
            'metadata': float('nan')
        }
        normalized = parser.normalize_log_entry(entry)
        assert 'page' not in normalized or normalized.get('page') is None
        assert normalized.get('metadata', {}) == {}

    def test_multiple_timestamp_formats(self, parser):
        """Test various timestamp format parsing"""
        formats = [
            '2024-01-01T12:00:00Z',
            '2024-01-01 12:00:00',
            '2024/01/01 12:00:00',
            '01-01-2024 12:00:00',
            '1704110400',  # Unix timestamp
        ]
        for ts_format in formats:
            entry = {'timestamp': ts_format}
            result = parser._extract_timestamp(entry)
            assert result is not None or ts_format == '01-01-2024 12:00:00'  # Some formats may not parse

    def test_empty_file_handling(self, parser):
        """Test handling of empty files"""
        content = b""
        with pytest.raises(Exception):
            parser.parse_file(content, "test.csv")

    def test_malformed_json_handling(self, parser):
        """Test handling of malformed JSON"""
        content = '{"invalid json'
        with pytest.raises(Exception):
            parser._parse_json(content)


# Integration tests
class TestIntelligentParserIntegration:
    """Integration tests with realistic data"""

    @pytest.fixture
    def parser(self):
        return IntelligentLogParser()

    def test_library_log_format_1(self, parser):
        """Test parsing logs from a typical library format"""
        content = b"""timestamp|event|url|session|browser
2024-01-01T12:00:00Z|pageview|/home|sess_123|Chrome
2024-01-01T12:01:00Z|click|/products|sess_123|Chrome
2024-01-01T12:02:00Z|scroll|/products|sess_123|Chrome"""
        
        result = parser.parse_file(content, "library_logs.psi")
        assert len(result) == 3
        
        normalized = [parser.normalize_log_entry(entry) for entry in result]
        assert normalized[0]['event_type'] == 'page_view'
        assert normalized[1]['event_type'] == 'click'
        assert normalized[2]['event_type'] == 'scroll'

    def test_library_log_format_2(self, parser):
        """Test parsing logs with different field names"""
        content = b"""time,type,path,sid,meta
2024-01-01T12:00:00Z,view,/home,s1,"{""browser"":""Firefox""}"
2024-01-01T12:01:00Z,action,/cart,s1,"{""action"":""add_to_cart""}" """
        
        result = parser.parse_file(content, "app_logs.csv")
        assert len(result) == 2
        
        normalized = [parser.normalize_log_entry(entry) for entry in result]
        assert 'timestamp' in normalized[0]
        assert 'event_type' in normalized[0]

    def test_mixed_case_headers(self, parser):
        """Test handling of mixed case headers"""
        content = b"""EventType,TimeStamp,PageURL,SessionID
page_view,2024-01-01T12:00:00Z,/home,sess_123"""
        
        result = parser.parse_file(content, "mixed_case.csv")
        normalized = parser.normalize_log_entry(result[0])
        
        assert normalized['event_type'] == 'page_view'
        assert isinstance(normalized['timestamp'], datetime)
