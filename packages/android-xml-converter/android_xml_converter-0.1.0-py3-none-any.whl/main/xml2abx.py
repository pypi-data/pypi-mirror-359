#!/usr/bin/env python3
"""
XML to Android Binary XML (ABX) Converter

This module provides functionality to convert XML files to Android Binary XML format.
Can be used as both a library and a command-line tool.
"""

import argparse
import base64
import binascii
import io
import re
import struct
import sys
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Union, BinaryIO
from xml.etree import ElementTree as ET


class ABXWarning(UserWarning):
    """Custom warning for ABX conversion issues."""
    pass


def show_warning(feature: str, details: str = "") -> None:
    """Show a warning about unsupported features."""
    message = f"{feature} is not supported and might be lost."
    if details:
        message += f" {details}"
    warnings.warn(message, ABXWarning, stacklevel=2)


class FastDataOutput:
    """Binary data output handler with string interning."""
    
    MAX_UNSIGNED_SHORT = 65535
    
    def __init__(self, output_stream: BinaryIO):
        self.output_stream = output_stream
        self.string_pool: Dict[str, int] = {}
        self.interned_strings: List[str] = []
    
    def write_byte(self, value: int) -> None:
        """Write a single byte."""
        self.output_stream.write(struct.pack('>B', value))
    
    def write_short(self, value: int) -> None:
        """Write a 16-bit big-endian short."""
        self.output_stream.write(struct.pack('>H', value))
    
    def write_int(self, value: int) -> None:
        """Write a 32-bit big-endian integer."""
        self.output_stream.write(struct.pack('>i', value))
    
    def write_long(self, value: int) -> None:
        """Write a 64-bit big-endian long."""
        self.output_stream.write(struct.pack('>q', value))
    
    def write_float(self, value: float) -> None:
        """Write a 32-bit big-endian float."""
        self.output_stream.write(struct.pack('>f', value))
    
    def write_double(self, value: float) -> None:
        """Write a 64-bit big-endian double."""
        self.output_stream.write(struct.pack('>d', value))
    
    def write_utf(self, string: str) -> None:
        """Write a UTF-8 string with length prefix."""
        utf8_bytes = string.encode('utf-8')
        if len(utf8_bytes) > self.MAX_UNSIGNED_SHORT:
            show_warning("String length exceeds 65,535 bytes",
                        f"String will be truncated: {string[:50]}...")
            raise ValueError("String length exceeds maximum allowed size")
        
        self.write_short(len(utf8_bytes))
        self.output_stream.write(utf8_bytes)
    
    def write_interned_utf(self, string: str) -> None:
        """Write an interned UTF-8 string."""
        if string in self.string_pool:
            self.write_short(self.string_pool[string])
        else:
            self.write_short(0xFFFF)
            self.write_utf(string)
            self.string_pool[string] = len(self.interned_strings)
            self.interned_strings.append(string)
    
    def write_bytes(self, data: bytes) -> None:
        """Write raw bytes."""
        self.output_stream.write(data)
    
    def flush(self) -> None:
        """Flush the output stream."""
        self.output_stream.flush()


class BinaryXmlSerializer:
    """Android Binary XML serializer."""
    
    # Protocol magic bytes
    PROTOCOL_MAGIC_VERSION_0 = b'\x41\x42\x58\x00'  # ABX\0
    
    # Token types
    START_DOCUMENT = 0
    END_DOCUMENT = 1
    START_TAG = 2
    END_TAG = 3
    TEXT = 4
    CDSECT = 5
    ENTITY_REF = 6
    IGNORABLE_WHITESPACE = 7
    PROCESSING_INSTRUCTION = 8
    COMMENT = 9
    DOC_DECL = 10
    ATTRIBUTE = 15
    
    # Type flags (shifted left by 4)
    TYPE_NULL = 1 << 4
    TYPE_STRING = 2 << 4
    TYPE_STRING_INTERNED = 3 << 4
    TYPE_BYTES_HEX = 4 << 4
    TYPE_BYTES_BASE64 = 5 << 4
    TYPE_INT = 6 << 4
    TYPE_INT_HEX = 7 << 4
    TYPE_LONG = 8 << 4
    TYPE_LONG_HEX = 9 << 4
    TYPE_FLOAT = 10 << 4
    TYPE_DOUBLE = 11 << 4
    TYPE_BOOLEAN_TRUE = 12 << 4
    TYPE_BOOLEAN_FALSE = 13 << 4
    
    def __init__(self, output_stream: BinaryIO):
        self.output = FastDataOutput(output_stream)
        output_stream.write(self.PROTOCOL_MAGIC_VERSION_0)
        self.tag_count = 0
        self.tag_names: List[str] = []
    
    def _write_token(self, token: int, text: Optional[str] = None) -> None:
        """Write a token with optional text data."""
        if text is not None:
            self.output.write_byte(token | self.TYPE_STRING)
            self.output.write_utf(text)
        else:
            self.output.write_byte(token | self.TYPE_NULL)
    
    def start_document(self) -> None:
        """Start document serialization."""
        self.output.write_byte(self.START_DOCUMENT | self.TYPE_NULL)
    
    def end_document(self) -> None:
        """End document serialization."""
        self.output.write_byte(self.END_DOCUMENT | self.TYPE_NULL)
        self.output.flush()
    
    def start_tag(self, name: str) -> None:
        """Start an XML tag."""
        if self.tag_count == len(self.tag_names):
            self.tag_names.extend([None] * max(1, len(self.tag_names) // 2))
        self.tag_names[self.tag_count] = name
        self.tag_count += 1
        
        self.output.write_byte(self.START_TAG | self.TYPE_STRING_INTERNED)
        self.output.write_interned_utf(name)
    
    def end_tag(self, name: str) -> None:
        """End an XML tag."""
        self.tag_count -= 1
        self.output.write_byte(self.END_TAG | self.TYPE_STRING_INTERNED)
        self.output.write_interned_utf(name)
    
    def attribute(self, name: str, value: str) -> None:
        """Write a string attribute."""
        self.output.write_byte(self.ATTRIBUTE | self.TYPE_STRING)
        self.output.write_interned_utf(name)
        self.output.write_utf(value)
    
    def attribute_interned(self, name: str, value: str) -> None:
        """Write an interned string attribute."""
        self.output.write_byte(self.ATTRIBUTE | self.TYPE_STRING_INTERNED)
        self.output.write_interned_utf(name)
        self.output.write_interned_utf(value)
    
    def attribute_bytes_hex(self, name: str, value: bytes) -> None:
        """Write a hex bytes attribute."""
        if len(value) > FastDataOutput.MAX_UNSIGNED_SHORT:
            raise ValueError(f"Hex bytes length ({len(value)}) exceeds maximum")
        
        self.output.write_byte(self.ATTRIBUTE | self.TYPE_BYTES_HEX)
        self.output.write_interned_utf(name)
        self.output.write_short(len(value))
        self.output.write_bytes(value)
    
    def attribute_bytes_base64(self, name: str, value: bytes) -> None:
        """Write a base64 bytes attribute."""
        if len(value) > FastDataOutput.MAX_UNSIGNED_SHORT:
            raise ValueError(f"Base64 bytes length ({len(value)}) exceeds maximum")
        
        self.output.write_byte(self.ATTRIBUTE | self.TYPE_BYTES_BASE64)
        self.output.write_interned_utf(name)
        self.output.write_short(len(value))
        self.output.write_bytes(value)
    
    def attribute_int(self, name: str, value: int) -> None:
        """Write an integer attribute."""
        self.output.write_byte(self.ATTRIBUTE | self.TYPE_INT)
        self.output.write_interned_utf(name)
        self.output.write_int(value)
    
    def attribute_int_hex(self, name: str, value: int) -> None:
        """Write a hex integer attribute."""
        self.output.write_byte(self.ATTRIBUTE | self.TYPE_INT_HEX)
        self.output.write_interned_utf(name)
        self.output.write_int(value)
    
    def attribute_long(self, name: str, value: int) -> None:
        """Write a long integer attribute."""
        self.output.write_byte(self.ATTRIBUTE | self.TYPE_LONG)
        self.output.write_interned_utf(name)
        self.output.write_long(value)
    
    def attribute_long_hex(self, name: str, value: int) -> None:
        """Write a hex long integer attribute."""
        self.output.write_byte(self.ATTRIBUTE | self.TYPE_LONG_HEX)
        self.output.write_interned_utf(name)
        self.output.write_long(value)
    
    def attribute_float(self, name: str, value: float) -> None:
        """Write a float attribute."""
        self.output.write_byte(self.ATTRIBUTE | self.TYPE_FLOAT)
        self.output.write_interned_utf(name)
        self.output.write_float(value)
    
    def attribute_double(self, name: str, value: float) -> None:
        """Write a double attribute."""
        self.output.write_byte(self.ATTRIBUTE | self.TYPE_DOUBLE)
        self.output.write_interned_utf(name)
        self.output.write_double(value)
    
    def attribute_boolean(self, name: str, value: bool) -> None:
        """Write a boolean attribute."""
        token_type = self.TYPE_BOOLEAN_TRUE if value else self.TYPE_BOOLEAN_FALSE
        self.output.write_byte(self.ATTRIBUTE | token_type)
        self.output.write_interned_utf(name)
    
    def text(self, text: str) -> None:
        """Write text content."""
        self._write_token(self.TEXT, text)
    
    def cdsect(self, text: str) -> None:
        """Write CDATA section."""
        self._write_token(self.CDSECT, text)
    
    def comment(self, text: str) -> None:
        """Write comment."""
        self._write_token(self.COMMENT, text)
    
    def processing_instruction(self, target: str, data: str = "") -> None:
        """Write processing instruction."""
        full_pi = f"{target} {data}" if data else target
        self._write_token(self.PROCESSING_INSTRUCTION, full_pi)
    
    def doc_decl(self, text: str) -> None:
        """Write document declaration."""
        self._write_token(self.DOC_DECL, text)
    
    def ignorable_whitespace(self, text: str) -> None:
        """Write ignorable whitespace."""
        self._write_token(self.IGNORABLE_WHITESPACE, text)
    
    def entity_ref(self, text: str) -> None:
        """Write entity reference."""
        self._write_token(self.ENTITY_REF, text)


class ValueTypeDetector:
    """Utility class for detecting value types from strings."""
    
    @staticmethod
    def is_boolean(value: str) -> bool:
        """Check if string represents a boolean."""
        return value.lower() in ('true', 'false')
    
    @staticmethod
    def is_integer(value: str) -> bool:
        """Check if string represents an integer."""
        try:
            int(value)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_hex_number(value: str) -> bool:
        """Check if string represents a hex number."""
        if len(value) < 3:
            return False
        if not value.lower().startswith('0x'):
            return False
        try:
            int(value, 16)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_float(value: str) -> bool:
        """Check if string represents a float."""
        try:
            float(value)
            return '.' in value
        except ValueError:
            return False
    
    @staticmethod
    def is_double(value: str) -> bool:
        """Check if string should be treated as double precision."""
        if 'e' in value.lower():
            return True
        if ValueTypeDetector.is_float(value) and len(value) > 10:
            return True
        return False
    
    @staticmethod
    def is_base64(value: str) -> bool:
        """Check if string represents base64 data."""
        if not value or len(value) % 4 != 0:
            return False
        try:
            # Check if it's valid base64
            base64.b64decode(value, validate=True)
            # Additional heuristic: should be reasonably long and contain base64 chars
            return len(value) > 8 and re.match(r'^[A-Za-z0-9+/]*={0,2}$', value)
        except Exception:
            return False
    
    @staticmethod
    def is_hex_string(value: str) -> bool:
        """Check if string represents hex-encoded bytes."""
        if len(value) % 2 != 0 or len(value) <= 2:
            return False
        try:
            bytes.fromhex(value)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_whitespace_only(value: str) -> bool:
        """Check if string contains only whitespace."""
        return value.isspace()


class XmlToAbxConverter:
    """Main converter class for XML to ABX conversion."""
    
    def __init__(self):
        self.detector = ValueTypeDetector()
    
    def _process_attribute_value(self, serializer: BinaryXmlSerializer, 
                                name: str, value: str) -> None:
        """Process and write an attribute with type detection."""
        # Check for namespace declarations
        if name.startswith('xmlns') or ':' in name:
            show_warning("Namespaces and prefixes", 
                        f"Found namespace declaration or prefixed attribute: {name}")
        
        # Type detection and conversion
        if self.detector.is_boolean(value):
            serializer.attribute_boolean(name, value.lower() == 'true')
        elif self.detector.is_hex_number(value):
            try:
                int_val = int(value, 16)
                if value.lower().startswith('0x') and len(value) <= 10:
                    serializer.attribute_int_hex(name, int_val)
                else:
                    serializer.attribute_long_hex(name, int_val)
            except (ValueError, OverflowError):
                serializer.attribute(name, value)
        elif self.detector.is_integer(value):
            try:
                int_val = int(value)
                if -2**31 <= int_val <= 2**31 - 1:
                    serializer.attribute_int(name, int_val)
                else:
                    serializer.attribute_long(name, int_val)
            except (ValueError, OverflowError):
                serializer.attribute(name, value)
        elif self.detector.is_double(value):
            try:
                serializer.attribute_double(name, float(value))
            except (ValueError, OverflowError):
                serializer.attribute(name, value)
        elif self.detector.is_float(value):
            try:
                serializer.attribute_float(name, float(value))
            except (ValueError, OverflowError):
                serializer.attribute(name, value)
        elif self.detector.is_base64(value):
            try:
                decoded = base64.b64decode(value)
                serializer.attribute_bytes_base64(name, decoded)
            except Exception:
                serializer.attribute(name, value)
        elif self.detector.is_hex_string(value):
            try:
                decoded = bytes.fromhex(value)
                serializer.attribute_bytes_hex(name, decoded)
            except Exception:
                serializer.attribute(name, value)
        else:
            # Use interned strings for short values without spaces
            if (len(value) < 50 and 
                (' ' not in value or value in ('true', 'false') or '.' in value)):
                serializer.attribute_interned(name, value)
            else:
                serializer.attribute(name, value)
    
    def _process_element(self, serializer: BinaryXmlSerializer, element: ET.Element) -> None:
        """Process an XML element and its children."""
        tag_name = element.tag
        
        # Check for namespace prefixes
        if ':' in tag_name:
            show_warning("Namespaces and prefixes", f"Found prefixed element: {tag_name}")
        
        serializer.start_tag(tag_name)
        
        # Process attributes
        for attr_name, attr_value in element.attrib.items():
            self._process_attribute_value(serializer, attr_name, attr_value)
        
        # Process text content
        if element.text:
            if self.detector.is_whitespace_only(element.text):
                serializer.ignorable_whitespace(element.text)
            else:
                serializer.text(element.text)
        
        # Process children
        for child in element:
            self._process_element(serializer, child)
            # Handle tail text
            if child.tail:
                if self.detector.is_whitespace_only(child.tail):
                    serializer.ignorable_whitespace(child.tail)
                else:
                    serializer.text(child.tail)
        
        serializer.end_tag(tag_name)
    
    def convert_file(self, input_path: Union[str, Path], 
                    output_path: Union[str, Path]) -> None:
        """Convert XML file to ABX format."""
        input_path = Path(input_path) if input_path != '-' else input_path
        output_path = Path(output_path) if output_path != '-' else output_path
        
        # Parse XML
        try:
            if input_path == '-':
                xml_content = sys.stdin.read()
                root = ET.fromstring(xml_content)
                tree = ET.ElementTree(root)
            else:
                tree = ET.parse(input_path)
                root = tree.getroot()
        except ET.ParseError as e:
            raise ValueError(f"XML parsing failed: {e}")
        
        # Open output
        if output_path == '-':
            output_stream = sys.stdout.buffer
        else:
            output_stream = open(output_path, 'wb')
        
        try:
            serializer = BinaryXmlSerializer(output_stream)
            serializer.start_document()
            
            # Process the root element
            self._process_element(serializer, root)
            
            serializer.end_document()
            
        finally:
            if output_path != '-':
                output_stream.close()
    
    def convert_string(self, xml_string: str) -> bytes:
        """Convert XML string to ABX bytes."""
        try:
            root = ET.fromstring(xml_string)
        except ET.ParseError as e:
            raise ValueError(f"XML parsing failed: {e}")
        
        output_buffer = io.BytesIO()
        serializer = BinaryXmlSerializer(output_buffer)
        serializer.start_document()
        
        self._process_element(serializer, root)
        
        serializer.end_document()
        return output_buffer.getvalue()


def main():
    """Command-line interface for the converter."""
    parser = argparse.ArgumentParser(
        description='Convert XML to Android Binary XML (ABX) format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument('input', help='Input XML file (use "-" for stdin)')
    parser.add_argument('output', nargs='?', help='Output ABX file (use "-" for stdout)')
    parser.add_argument('-i', '--in-place', action='store_true',
                       help='Overwrite input file with output')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.in_place:
        if args.input == '-':
            parser.error("Cannot use -i with stdin input")
        if args.output:
            parser.error("Cannot specify output file with -i option")
        args.output = args.input
    elif not args.output:
        parser.error("Output file is required unless using -i option")
    
    try:
        converter = XmlToAbxConverter()
        converter.convert_file(args.input, args.output)
        
        input_name = "stdin" if args.input == '-' else args.input
        output_name = "stdout" if args.output == '-' else args.output
        print(f"Successfully converted {input_name} to {output_name}", file=sys.stderr)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
