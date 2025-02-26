"""
This code is for testing only. 
"""

import xml.etree.ElementTree as ET
from lxml import etree
import re

def get_namespace(element):
    """Extract the namespace from an XML element tag."""
    m = re.match(r'\{(.*)\}', element.tag)
    return m.group(1) if m else None

#  Creates a parser and applies it to the file
parser = etree.XMLParser(recover=True)  # Recover from parsing errors
tree = etree.parse("example_scheda_bibliografica.xml", parser)
root = tree.getroot()

ns = get_namespace(root)  #  extracts the namespace of the root tag. If no namespace is found, returns None. 
ns_map = {'ns': ns} if ns else {}

# Initialize the result dictionary
result = {
    'title_in_titlestmt': False,
    'title_in_sourcedesc': False,
    'title_text': []
}

# Create namespace-aware path expressions
if ns:
    # With namespace
    titlestmt_path = ".//ns:titleStmt"
    title_path = ".//ns:title[@type='main']"
    sourcedesc_path = ".//ns:sourceDesc//ns:biblFull//ns:titleStmt"
else:
    # No namespace
    titlestmt_path = ".//titleStmt"
    title_path = ".//title[@type='main']"
    sourcedesc_path = ".//sourceDesc//biblFull//titleStmt"

# Check for <title type="main"> under <titleStmt>
for titlestmt in tree.xpath(titlestmt_path, namespaces=ns_map):  #  Looks for any titleStmt element in the namespace, using ns: to reference elements in that namespace.
    #  namespaces=ns_map maps the prefix ns: to the actual namespace URI extracted from the document.
    # Only check direct children titleStmt to avoid picking up nested ones
    parent = titlestmt.getparent()  #  Retrieves the parent element of the titleStmt element we're examining. 
    if parent is not None and parent.tag.endswith('sourceDesc'):  #  These cases (titleStmt under sourceDesc) will be treated separately.
        continue
        
    title_elements = titlestmt.xpath(title_path, namespaces=ns_map)  #  Looks for any title element with type="main" under the titleStmt element
    if title_elements:
        result['title_in_titlestmt'] = True
        for title in title_elements:
            if title.text:
                result['title_text'].append(title.text.strip())

# Check for <title type="main"> under <sourceDesc><biblFull><titleStmt>
for sourcedesc_titlestmt in tree.xpath(sourcedesc_path, namespaces=ns_map):  #  Looks for any titleStmt element with a namespace, using ns: to reference elements in that namespace.
    title_elements = sourcedesc_titlestmt.xpath(title_path, namespaces=ns_map)  #  Looks for any title element with type="main" under the titleStmt element 
    if title_elements:
        result['title_in_sourcedesc'] = True
        for title in title_elements:
            if title.text:
                result['title_text'].append(title.text.strip())
                
