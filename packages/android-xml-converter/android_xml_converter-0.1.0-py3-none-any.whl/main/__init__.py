from typing import Optional
from .abx2xml import convert as abx_to_xml
from .abx2xml import AbxToXmlConverter
from .xml2abx import XmlToAbxConverter

# Convenience functions
def convert_abx_to_xml(input_path: str, output_path: Optional[str] = None) -> str:
    """Convert ABX file to XML (convenience wrapper)."""
    return AbxToXmlConverter().convert_file(input_path, output_path)

def convert_xml_to_abx(input_path: str, output_path: str) -> None:
    """Convert XML file to ABX format (convenience wrapper)."""
    XmlToAbxConverter().convert_file(input_path, output_path)

def abx_to_xml_string(abx_data: bytes) -> str:
    """Convert ABX bytes to XML string."""
    return AbxToXmlConverter().convert_bytes(abx_data)

def xml_to_abx_string(xml_string: str) -> bytes:
    """Convert XML string to ABX bytes."""
    return XmlToAbxConverter().convert_string(xml_string)

__all__ = [
    'AbxToXmlConverter',
    'XmlToAbxConverter',
    'abx_to_xml',
    'convert_abx_to_xml',
    'convert_xml_to_abx',
    'abx_to_xml_string',
    'xml_to_abx_string',
]