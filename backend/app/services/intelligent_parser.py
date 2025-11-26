"""
Intelligent Log Parser Service
Supports multiple file formats and uses AI to normalize different log structures
"""
from __future__ import annotations

import csv
import json
import re
from datetime import datetime
from io import StringIO
from typing import Any

import chardet
import pandas as pd
from fastapi import HTTPException, status
from loguru import logger
from groq import Groq

from app.core.config import get_settings

settings = get_settings()


class IntelligentLogParser:
    """
    AI-powered parser that can handle multiple file formats and log structures.
    Supports CSV, JSON, PSI (pipe-separated), TSV, and custom delimiters.
    Uses Groq AI to intelligently map different log formats to the expected schema.
    """

    def __init__(self):
        self.groq_client = None
        if hasattr(settings, 'groq_api_key') and settings.groq_api_key:
            try:
                self.groq_client = Groq(api_key=settings.groq_api_key)
            except Exception as e:
                logger.warning(f"Groq client initialization failed: {e}")

    def detect_encoding(self, contents: bytes) -> str:
        """Detect file encoding using chardet"""
        result = chardet.detect(contents)
        encoding = result.get('encoding', 'utf-8')
        logger.info(f"Detected encoding: {encoding} (confidence: {result.get('confidence', 0)})")
        return encoding or 'utf-8'

    def detect_delimiter(self, text_sample: str) -> str:
        """
        Intelligently detect the delimiter used in the file.
        Supports: comma, pipe, tab, semicolon, and custom delimiters.
        """
        # Count occurrences of common delimiters in first few lines
        lines = text_sample.split('\n')[:5]
        delimiters = {
            ',': 'comma (CSV)',
            '|': 'pipe (PSI)',
            '\t': 'tab (TSV)',
            ';': 'semicolon',
            ':': 'colon',
        }
        
        delimiter_counts = {}
        for delim, name in delimiters.items():
            count = sum(line.count(delim) for line in lines if line.strip())
            if count > 0:
                delimiter_counts[delim] = count / len([l for l in lines if l.strip()])
        
        if not delimiter_counts:
            logger.warning("No common delimiter found, defaulting to comma")
            return ','
        
        # Return the delimiter with highest average count per line
        detected_delim = max(delimiter_counts, key=delimiter_counts.get)
        logger.info(f"Detected delimiter: {delimiters.get(detected_delim, 'unknown')} ({repr(detected_delim)})")
        return detected_delim

    def detect_file_format(self, filename: str, contents: bytes) -> str:
        """Detect file format based on extension and content"""
        filename_lower = filename.lower()
        
        # Check by extension first
        if filename_lower.endswith('.json'):
            return 'json'
        elif filename_lower.endswith('.csv'):
            return 'csv'
        elif filename_lower.endswith('.psi'):
            return 'psi'
        elif filename_lower.endswith('.tsv') or filename_lower.endswith('.txt'):
            return 'tsv'
        
        # Try to detect by content
        try:
            encoding = self.detect_encoding(contents)
            text_sample = contents[:1000].decode(encoding, errors='ignore')
            
            # Try JSON
            try:
                json.loads(text_sample)
                return 'json'
            except:
                pass
            
            # Check for delimiters
            if '|' in text_sample:
                return 'psi'
            elif '\t' in text_sample:
                return 'tsv'
            else:
                return 'csv'
        except:
            return 'csv'  # Default fallback

    def parse_file(self, contents: bytes, filename: str) -> list[dict[str, Any]]:
        """
        Main parsing method that handles multiple formats
        """
        file_format = self.detect_file_format(filename, contents)
        encoding = self.detect_encoding(contents)
        
        logger.info(f"Parsing file: {filename} (format: {file_format}, encoding: {encoding})")
        
        try:
            text_content = contents.decode(encoding, errors='replace')
        except Exception as e:
            logger.error(f"Encoding error: {e}")
            text_content = contents.decode('utf-8', errors='replace')
        
        # Parse based on detected format
        if file_format == 'json':
            return self._parse_json(text_content)
        elif file_format == 'psi':
            return self._parse_delimited(text_content, delimiter='|')
        elif file_format == 'tsv':
            return self._parse_delimited(text_content, delimiter='\t')
        else:  # csv or unknown
            delimiter = self.detect_delimiter(text_content)
            return self._parse_delimited(text_content, delimiter=delimiter)

    def _parse_json(self, text_content: str) -> list[dict[str, Any]]:
        """Parse JSON format"""
        try:
            data = json.loads(text_content)
            
            # Handle different JSON structures
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Check for common wrapper keys
                for key in ['events', 'data', 'logs', 'records', 'items']:
                    if key in data and isinstance(data[key], list):
                        return data[key]
                # If it's a single object, wrap it in a list
                return [data]
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid JSON structure"
                )
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid JSON: {str(e)}"
            )

    def _parse_delimited(self, text_content: str, delimiter: str) -> list[dict[str, Any]]:
        """Parse delimited files (CSV, PSI, TSV, etc.)"""
        try:
            df = pd.read_csv(
                StringIO(text_content),
                delimiter=delimiter,
                encoding='utf-8',
                on_bad_lines='skip',
                engine='python'
            )
            
            # Clean column names
            df.columns = df.columns.str.strip().str.lower()
            
            logger.info(f"Parsed {len(df)} rows with columns: {list(df.columns)}")
            return df.to_dict(orient='records')
        except Exception as e:
            logger.error(f"Delimited file parsing error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse delimited file: {str(e)}"
            )

    def normalize_log_entry(self, raw_entry: dict[str, Any]) -> dict[str, Any]:
        """
        Intelligently normalize a log entry to match expected schema.
        Maps different field names and formats to the standard structure.
        """
        normalized = {}
        
        # Normalize event_type / type
        event_type = self._extract_event_type(raw_entry)
        if event_type:
            normalized['event_type'] = event_type
        
        # Normalize timestamp
        timestamp = self._extract_timestamp(raw_entry)
        if timestamp:
            normalized['timestamp'] = timestamp
        
        # Normalize session_id
        session_id = self._extract_field(raw_entry, [
            'session_id', 'sessionid', 'session', 'sid', 'session_key'
        ])
        if session_id:
            normalized['session_id'] = str(session_id)
        
        # Normalize page/url
        page = self._extract_field(raw_entry, [
            'page', 'url', 'path', 'page_url', 'page_path', 'pathname', 'location'
        ])
        if page:
            normalized['page'] = str(page)
        
        # Normalize website
        website = self._extract_field(raw_entry, [
            'website', 'site', 'domain', 'host', 'hostname', 'origin'
        ])
        if website:
            normalized['website'] = str(website)
        
        # Normalize scroll_depth
        scroll_depth = self._extract_field(raw_entry, [
            'scroll_depth', 'scroll', 'scroll_percentage', 'scroll_pct'
        ])
        if scroll_depth is not None:
            try:
                normalized['scroll_depth'] = float(scroll_depth)
            except (ValueError, TypeError):
                pass
        
        # Normalize metadata - collect remaining fields
        metadata_keys = [
            'metadata', 'meta', 'data', 'properties', 'props', 'attributes',
            'action', 'element', 'target', 'value', 'label'
        ]
        metadata = {}
        
        # First check if there's an explicit metadata field
        for key in metadata_keys:
            if key in raw_entry and isinstance(raw_entry[key], dict):
                metadata.update(raw_entry[key])
                break
        
        # Add other fields that aren't already normalized
        normalized_keys = set(normalized.keys())
        for key, value in raw_entry.items():
            if key.lower() not in normalized_keys and key.lower() not in metadata_keys:
                if value is not None and not (isinstance(value, float) and str(value) == 'nan'):
                    metadata[key] = value
        
        if metadata:
            normalized['metadata'] = metadata
        
        return normalized

    def _extract_event_type(self, entry: dict[str, Any]) -> str | None:
        """Extract and normalize event type"""
        # Try common field names
        type_value = self._extract_field(entry, [
            'event_type', 'type', 'event', 'action', 'event_name', 'name'
        ])
        
        if not type_value:
            # Infer from other fields
            if self._extract_field(entry, ['scroll_depth', 'scroll']):
                return 'scroll'
            elif self._extract_field(entry, ['page', 'url', 'path']):
                return 'page_view'
            elif self._extract_field(entry, ['click', 'button', 'element']):
                return 'click'
            else:
                return 'action'
        
        # Normalize type value
        type_str = str(type_value).strip().lower()
        
        # Map common variations
        type_mapping = {
            'pageview': 'page_view',
            'page_view': 'page_view',
            'page-view': 'page_view',
            'view': 'page_view',
            'click': 'click',
            'button_click': 'click',
            'scroll': 'scroll',
            'action': 'action',
            'event': 'action',
        }
        
        return type_mapping.get(type_str, type_str)

    def _extract_timestamp(self, entry: dict[str, Any]) -> datetime | None:
        """Extract and parse timestamp from various formats"""
        timestamp_value = self._extract_field(entry, [
            'timestamp', 'time', 'datetime', 'date', 'created_at', 'event_time'
        ])
        
        if not timestamp_value:
            return None
        
        # If already datetime
        if isinstance(timestamp_value, datetime):
            return timestamp_value
        
        # Try parsing various formats
        timestamp_str = str(timestamp_value)
        
        # Try ISO format
        try:
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except:
            pass
        
        # Try common formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y/%m/%d %H:%M:%S',
            '%d-%m-%Y %H:%M:%S',
            '%m/%d/%Y %H:%M:%S',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except:
                continue
        
        # Try Unix timestamp
        try:
            timestamp_float = float(timestamp_str)
            # Check if it's in milliseconds
            if timestamp_float > 1e12:
                timestamp_float /= 1000
            return datetime.fromtimestamp(timestamp_float)
        except:
            pass
        
        logger.warning(f"Could not parse timestamp: {timestamp_value}")
        return None

    def _extract_field(self, entry: dict[str, Any], field_names: list[str]) -> Any:
        """Extract field value trying multiple possible field names"""
        for field_name in field_names:
            # Try exact match
            if field_name in entry:
                value = entry[field_name]
                if value is not None and not (isinstance(value, float) and str(value) == 'nan'):
                    return value
            
            # Try case-insensitive match
            for key in entry.keys():
                if key.lower() == field_name.lower():
                    value = entry[key]
                    if value is not None and not (isinstance(value, float) and str(value) == 'nan'):
                        return value
        
        return None

    def use_ai_to_normalize(self, sample_entries: list[dict[str, Any]]) -> dict[str, str]:
        """
        Use Groq AI to intelligently map field names from unknown log formats.
        Returns a mapping of original field names to normalized field names.
        """
        if not self.groq_client or not sample_entries:
            return {}
        
        try:
            # Take first few entries as sample
            sample = sample_entries[:3]
            
            prompt = f"""
You are a data normalization expert. Given these log entries, create a mapping from the current field names to our standard schema.

Standard schema fields:
- event_type (values: page_view, click, action, scroll)
- timestamp (datetime)
- session_id (string)
- page (string - URL or page path)
- website (string - domain)
- scroll_depth (float 0-100)
- metadata (dict - any other fields)

Sample log entries:
{json.dumps(sample, indent=2, default=str)}

Return ONLY a JSON object mapping original field names to standard field names. Example:
{{"time": "timestamp", "url": "page", "type": "event_type"}}
"""
            
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a data mapping expert. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            mapping_str = response.choices[0].message.content.strip()
            # Extract JSON from markdown code blocks if present
            if '```json' in mapping_str:
                mapping_str = mapping_str.split('```json')[1].split('```')[0].strip()
            elif '```' in mapping_str:
                mapping_str = mapping_str.split('```')[1].split('```')[0].strip()
            
            mapping = json.loads(mapping_str)
            logger.info(f"AI-generated field mapping: {mapping}")
            return mapping
            
        except Exception as e:
            logger.error(f"AI normalization failed: {e}")
            return {}
