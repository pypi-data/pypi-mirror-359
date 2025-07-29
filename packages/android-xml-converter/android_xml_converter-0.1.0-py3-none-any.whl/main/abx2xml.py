#!/usr/bin/env python3
import argparse
import base64
import io
import struct
import sys
from pathlib import Path
from typing import BinaryIO, List, Optional, Union


def encode_xml_entities(text: str) -> str:
    """Encode XML entities in text."""
    return (text.replace("&", "&amp;")
               .replace("<", "&lt;")
               .replace(">", "&gt;")
               .replace('"', "&quot;")
               .replace("'", "&apos;"))


class FastDataInput:
    
    def __init__(self, data: Union[bytes, BinaryIO]):
        if isinstance(data, (bytes, bytearray)):
            self.stream = io.BytesIO(data)
        else:
            self.stream = io.BytesIO(data.read())
        self.interned_strings: List[str] = []
    
    def read_byte(self) -> int:
        """Read a single byte."""
        data = self.stream.read(1)
        if not data:
            raise EOFError("Failed to read byte from stream")
        return struct.unpack('B', data)[0]
    
    def read_short(self) -> int:
        """Read a 16-bit big-endian short."""
        data = self.stream.read(2)
        if len(data) != 2:
            raise EOFError("Failed to read short from stream")
        return struct.unpack('>H', data)[0]
    
    def read_int(self) -> int:
        """Read a 32-bit big-endian int."""
        data = self.stream.read(4)
        if len(data) != 4:
            raise EOFError("Failed to read int from stream")
        return struct.unpack('>i', data)[0]
    
    def read_long(self) -> int:
        """Read a 64-bit big-endian long."""
        data = self.stream.read(8)
        if len(data) != 8:
            raise EOFError("Failed to read long from stream")
        return struct.unpack('>q', data)[0]
    
    def read_float(self) -> float:
        """Read a 32-bit big-endian float."""
        int_value = self.read_int()
        return struct.unpack('>f', struct.pack('>i', int_value))[0]
    
    def read_double(self) -> float:
        """Read a 64-bit big-endian double."""
        long_value = self.read_long()
        return struct.unpack('>d', struct.pack('>q', long_value))[0]
    
    def read_utf(self) -> str:
        """Read a UTF-8 string with length prefix."""
        length = self.read_short()
        data = self.stream.read(length)
        if len(data) != length:
            raise EOFError("Failed to read UTF string from stream")
        return data.decode('utf-8', errors='replace')
    
    def read_interned_utf(self) -> str:
        """Read an interned UTF-8 string."""
        index = self.read_short()
        if index == 0xFFFF:
            # New string to intern
            string = self.read_utf()
            self.interned_strings.append(string)
            return string
        else:
            # Reference to existing interned string
            if index >= len(self.interned_strings):
                raise ValueError(f"Invalid interned string index: {index}")
            return self.interned_strings[index]
    
    def read_bytes(self, length: int) -> bytes:
        """Read specified number of bytes."""
        data = self.stream.read(length)
        if len(data) != length:
            raise EOFError("Failed to read bytes from stream")
        return data
    
    def eof(self) -> bool:
        """Check if at end of stream."""
        pos = self.stream.tell()
        data = self.stream.read(1)
        if data:
            self.stream.seek(pos)
            return False
        return True
    
    def tell(self) -> int:
        """Get current position."""
        return self.stream.tell()
    
    def seek(self, pos: int) -> None:
        """Seek to position."""
        self.stream.seek(pos)


class BinaryXmlDeserializer:
    """Android Binary XML deserializer."""
    
    # Protocol constants
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
    DOCDECL = 10
    ATTRIBUTE = 15
    
    # Data types
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
    
    def __init__(self, input_data: Union[bytes, BinaryIO]):
        self.input = FastDataInput(input_data)
        self._check_magic_header()
    
    def _check_magic_header(self) -> None:
        """Check the ABX magic header."""
        magic = self.input.read_bytes(4)
        if magic != self.PROTOCOL_MAGIC_VERSION_0:
            raise ValueError("Invalid ABX file format - magic header mismatch")
    
    def _bytes_to_hex(self, data: bytes) -> str:
        """Convert bytes to hexadecimal string."""
        return data.hex().upper()
    
    def _process_attribute(self, token: int) -> str:
        """Process an attribute and return its XML representation."""
        attr_type = token & 0xF0
        name = self.input.read_interned_utf()
        
        value = ""
        if attr_type == self.TYPE_STRING:
            value = encode_xml_entities(self.input.read_utf())
        elif attr_type == self.TYPE_STRING_INTERNED:
            value = encode_xml_entities(self.input.read_interned_utf())
        elif attr_type == self.TYPE_INT:
            value = str(self.input.read_int())
        elif attr_type == self.TYPE_INT_HEX:
            value = f"0x{self.input.read_int():x}"
        elif attr_type == self.TYPE_LONG:
            value = str(self.input.read_long())
        elif attr_type == self.TYPE_LONG_HEX:
            value = f"0x{self.input.read_long():x}"
        elif attr_type == self.TYPE_FLOAT:
            value = str(self.input.read_float())
        elif attr_type == self.TYPE_DOUBLE:
            value = str(self.input.read_double())
        elif attr_type == self.TYPE_BOOLEAN_TRUE:
            value = "true"
        elif attr_type == self.TYPE_BOOLEAN_FALSE:
            value = "false"
        elif attr_type == self.TYPE_BYTES_HEX:
            length = self.input.read_short()
            data = self.input.read_bytes(length)
            value = self._bytes_to_hex(data)
        elif attr_type == self.TYPE_BYTES_BASE64:
            length = self.input.read_short()
            data = self.input.read_bytes(length)
            value = base64.b64encode(data).decode('ascii')
        else:
            raise ValueError(f"Unknown attribute type: {attr_type}")
        
        return f' {name}="{value}"'
    
    def deserialize(self) -> str:
        """Deserialize the ABX data to XML string."""
        output = ['<?xml version="1.0" encoding="UTF-8"?>']
        
        while not self.input.eof():
            try:
                token = self.input.read_byte()
                command = token & 0x0F
                token_type = token & 0xF0
                
                if command == self.START_DOCUMENT:
                    continue
                
                elif command == self.END_DOCUMENT:
                    break
                
                elif command == self.START_TAG:
                    tag_name = self.input.read_interned_utf()
                    tag_parts = [f'<{tag_name}']
                    
                    # Read attributes
                    while True:
                        pos = self.input.tell()
                        try:
                            next_token = self.input.read_byte()
                            if (next_token & 0x0F) == self.ATTRIBUTE:
                                tag_parts.append(self._process_attribute(next_token))
                            else:
                                self.input.seek(pos)
                                break
                        except EOFError:
                            self.input.seek(pos)
                            break
                    
                    tag_parts.append('>')
                    output.append(''.join(tag_parts))
                
                elif command == self.END_TAG:
                    tag_name = self.input.read_interned_utf()
                    output.append(f'</{tag_name}>')
                
                elif command == self.TEXT:
                    if token_type == self.TYPE_STRING:
                        text = self.input.read_utf()
                        if text:
                            output.append(encode_xml_entities(text))
                
                elif command == self.CDSECT:
                    if token_type == self.TYPE_STRING:
                        text = self.input.read_utf()
                        output.append(f'<![CDATA[{text}]]>')
                
                elif command == self.COMMENT:
                    if token_type == self.TYPE_STRING:
                        text = self.input.read_utf()
                        output.append(f'<!--{text}-->')
                
                elif command == self.PROCESSING_INSTRUCTION:
                    if token_type == self.TYPE_STRING:
                        text = self.input.read_utf()
                        output.append(f'<?{text}?>')
                
                elif command == self.DOCDECL:
                    if token_type == self.TYPE_STRING:
                        text = self.input.read_utf()
                        output.append(f'<!DOCTYPE {text}>')
                
                elif command == self.ENTITY_REF:
                    if token_type == self.TYPE_STRING:
                        text = self.input.read_utf()
                        output.append(f'&{text};')
                
                elif command == self.IGNORABLE_WHITESPACE:
                    if token_type == self.TYPE_STRING:
                        text = self.input.read_utf()
                        output.append(text)
                
                else:
                    print(f"Warning: Unknown token: {command}", file=sys.stderr)
            
            except Exception as e:
                print(f"Warning: Error parsing token: {e}", file=sys.stderr)
                break
        
        return ''.join(output)


class AbxToXmlConverter:
    """Main converter class for ABX to XML conversion."""
    
    def convert_bytes(self, abx_data: bytes) -> str:
        
        deserializer = BinaryXmlDeserializer(abx_data)
        return deserializer.deserialize()
    
    def convert_file(self, input_path: Union[str, Path], 
                    output_path: Optional[Union[str, Path]] = None) -> str:

        # Read input
        if input_path == '-':
            input_data = sys.stdin.buffer.read()
        else:
            with open(input_path, 'rb') as f:
                input_data = f.read()
        
        # Convert
        xml_content = self.convert_bytes(input_data)
        
        # Write output
        if output_path is None:
            return xml_content
        elif output_path == '-':
            print(xml_content)
            return ""
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            return ""
    
    def convert_in_place(self, file_path: Union[str, Path]) -> None:

        xml_content = self.convert_file(file_path)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)


def convert(input_path: Union[str, Path], output_path: Optional[Union[str, Path]] = None) -> str:
    """Convenient function to convert ABX to XML, callable from other Python code."""
    return AbxToXmlConverter().convert_file(input_path, output_path)


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Converts Android Binary XML (ABX) to human-readable XML.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        """)
    
    parser.add_argument('-i', '--in-place', action='store_true',
                       help='Overwrite input file with converted output')
    parser.add_argument('input', 
                       help='Input ABX file path (use "-" for stdin)')
    parser.add_argument('output', nargs='?', default='-',
                       help='Output XML file path (use "-" for stdout, default: stdout)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.in_place and args.input == '-':
        parser.error("Cannot use -i/--in-place option with stdin input")
    
    if args.in_place:
        args.output = args.input
    
    try:
        converter = AbxToXmlConverter()
        
        if args.in_place:
            converter.convert_in_place(args.input)
            print(f"Successfully converted {args.input} in place", file=sys.stderr)
        else:
            converter.convert_file(args.input, args.output)
            if args.output != '-':
                input_name = "stdin" if args.input == '-' else args.input
                print(f"Successfully converted {input_name} to {args.output}", file=sys.stderr)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
