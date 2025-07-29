# Android-XML-Converter

A Python library for converting between ABX format and human-readable XML.

## Features

- Convert ABX files to XML
- Convert XML files to ABX
- Command-line interface

## Installation

```bash
pip install android-xml-converter
```

## CLI Usage
```bash
usage: abx2xml [-h] [-i] input [output]
usage: xml2abx [-h] [-i] input [output]

Converts Android Binary XML (ABX) to human-readable XML.

positional arguments:
  input           Input file path (use "-" for stdin)
  output          Output file path (use "-" for stdout)

options:
  -h, --help      show this help message and exit
  -i, --in-place  Overwrite input file with converted output
  ```


### Use as Library

```python
from android_xml_converter import (
    AbxToXmlConverter,
    XmlToAbxConverter,
    abx_to_xml_string,
    xml_to_abx_string
)

# Convert between strings/bytes
xml = abx_to_xml_string(abx_data)  # ABX bytes to XML string
abx_data = xml_to_abx_string(xml)  # XML string to ABX bytes

# File conversion
abx_converter = AbxToXmlConverter()
abx_converter.convert_file('input.abx', 'output.xml')

xml_converter = XmlToAbxConverter()
xml_converter.convert_file('input.xml', 'output.abx')
```

