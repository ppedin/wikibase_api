"""
This code defines detectors, which are objects with a detect method.
The method allows to check if a xml file contains a specific field.
The classes are based on the schema defined by Links.
"""

import xml.etree.ElementTree as ET
from lxml import etree
import re


def get_namespace(element):
    """Extract the namespace from an XML element tag."""
    m = re.match(r'\{(.*)\}', element.tag)
    return m.group(1) if m else None


class Detector():
    """
    Generic class for detectors. 
    Implements minimal functionalities used by all detectors.
    """
    def __init__(self):
        pass


class TitleDetector(Detector):
    """
    This class is a detector for the Title field.
    """
    def __init__(self):
        self.field = 'title'
        super().__init__()

    def detect(self, root, ns, ns_map):
        """
        Detects if the Title field can be found in the XML content.
        Takes as input the byte representation of the XML content produced by the FileUpload.read() method of FastAPI.
        Uses the schemas defined by Links. 
        Returns a list with the detected results. 
        """

        #  Here will be saved all the results of the detection. 
        results = []

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
        for titlestmt in root.xpath(titlestmt_path, namespaces=ns_map):  #  Looks for any titleStmt element in the namespace, using ns: to reference elements in that namespace.
            #  namespaces=ns_map maps the prefix ns: to the actual namespace URI extracted from the document.
            # Only check direct children titleStmt to avoid picking up nested ones
            parent = titlestmt.getparent()  #  Retrieves the parent element of the titleStmt element we're examining. 
            if parent is not None and parent.tag.endswith('sourceDesc'):  #  These cases (titleStmt under sourceDesc) will be treated separately.
                continue
                
            title_elements = titlestmt.xpath(title_path, namespaces=ns_map)  #  Looks for any title element with type="main" under the titleStmt element
            if title_elements:
                for title in title_elements:
                    if title.text:
                        results.append(title.text.strip())
                        
        # Check for <title type="main"> under <sourceDesc><biblFull><titleStmt>
        for sourcedesc_titlestmt in root.xpath(sourcedesc_path, namespaces=ns_map):  #  Looks for any titleStmt element with a namespace, using ns: to reference elements in that namespace.
            title_elements = sourcedesc_titlestmt.xpath(title_path, namespaces=ns_map)  #  Looks for any title element with type="main" under the titleStmt element 
            if title_elements:
                for title in title_elements:
                    if title.text:
                        results.append(title.text.strip())
                        
        return list(set(results))


class ShortTitleDetector(Detector):
    """
    This class is a detector for the field Short Title
    """
    def __init__(self):
        self.field = 'short_title'
        super().__init__()

    def detect(self, root, ns, ns_map):
        """
        Detects if the Short Title field can be found in the XML content.
        Takes as input the byte representation of the XML content produced by the FileUpload.read() method of FastAPI.
        Uses the schemas defined by Links.
        Returns a list with the detected results.
        """

        results = []

        # Create namespace-aware path expressions
        if ns:
            # With namespace
            titlestmt_path = ".//ns:titleStmt"
            short_title_path = ".//ns:title[@type='short']"
            sourcedesc_path = ".//ns:sourceDesc//ns:biblFull//ns:titleStmt"
        else:
            # No namespace
            titlestmt_path = ".//titleStmt"
            short_title_path = ".//title[@type='short']"
            sourcedesc_path = ".//sourceDesc//biblFull//titleStmt"

        # 1) Check for <title type="short"> under <titleStmt> (but not under <sourceDesc>)
        for titlestmt in root.xpath(titlestmt_path, namespaces=ns_map):
            parent = titlestmt.getparent()
            # If the parent is <sourceDesc>, skip here (it will be handled in the next loop)
            if parent is not None and parent.tag.endswith('sourceDesc'):
                continue

            short_title_elements = titlestmt.xpath(short_title_path, namespaces=ns_map)
            for short_title in short_title_elements:
                if short_title.text:
                    results.append(short_title.text.strip())

        # 2) Check for <title type="short"> under <sourceDesc><biblFull><titleStmt>
        for sourcedesc_titlestmt in root.xpath(sourcedesc_path, namespaces=ns_map):
            short_title_elements = sourcedesc_titlestmt.xpath(short_title_path, namespaces=ns_map)
            for short_title in short_title_elements:
                if short_title.text:
                    results.append(short_title.text.strip())

        # Return unique results
        return list(set(results))


class AlternativeTitleDetector(Detector):
    """
    This class is a detector for the field Alternative Title
    """
    def __init__(self):
        self.field = 'alternative_title'
        super().__init__()

    def detect(self, root, ns, ns_map):
        """
        Detects if the Alternative Title field can be found in the XML content.
        Takes as input the byte representation of the XML content produced by the FileUpload.read() method of FastAPI.
        Uses the schemas defined by Links.
        Returns a list with the detected results.
        """

        results = []

        # Create namespace-aware path expressions
        if ns:
            # With namespace
            titlestmt_path = ".//ns:titleStmt"
            alt_title_path = ".//ns:title[@type='alternative']"
            sourcedesc_path = ".//ns:sourceDesc//ns:biblFull//ns:titleStmt"
        else:
            # No namespace
            titlestmt_path = ".//titleStmt"
            alt_title_path = ".//title[@type='alternative']"
            sourcedesc_path = ".//sourceDesc//biblFull//titleStmt"

        # 1) Check for <title type="alternative"> under <titleStmt> (but not under <sourceDesc>)
        for titlestmt in root.xpath(titlestmt_path, namespaces=ns_map):
            parent = titlestmt.getparent()
            # If the parent is <sourceDesc>, skip here (it will be handled in the next loop)
            if parent is not None and parent.tag.endswith('sourceDesc'):
                continue

            alt_title_elements = titlestmt.xpath(alt_title_path, namespaces=ns_map)
            for alt_title in alt_title_elements:
                if alt_title.text:
                    results.append(alt_title.text.strip())

        # 2) Check for <title type="alternative"> under <sourceDesc><biblFull><titleStmt>
        for sourcedesc_titlestmt in root.xpath(sourcedesc_path, namespaces=ns_map):
            alt_title_elements = sourcedesc_titlestmt.xpath(alt_title_path, namespaces=ns_map)
            for alt_title in alt_title_elements:
                if alt_title.text:
                    results.append(alt_title.text.strip())

        # Return unique results
        return list(set(results))


class AuthorDetector(Detector):
    """
    This class is a detector for the field Author
    """
    def __init__(self):
        self.field = 'author'
        super().__init__()

    def detect(self, root, ns, ns_map):
        """
        Detects if the Author field can be found in the XML content.
        Takes as input the byte representation of the XML content produced by the FileUpload.read() method of FastAPI.
        Uses the schemas defined by Links. 
        Returns a list with the detected results. 
        """

        # Here will be saved all the results of the detection.
        results = []
 
        # Create namespace-aware path expressions
        if ns:
            # With namespace
            titlestmt_path = ".//ns:titleStmt"
            author_path = ".//ns:author"
            persname_path = ".//ns:persName"
            forename_path = ".//ns:forename"
            surname_path = ".//ns:surname"
            sourcedesc_path = ".//ns:sourceDesc//ns:biblFull//ns:titleStmt"
        else:
            # No namespace
            titlestmt_path = ".//titleStmt"
            author_path = ".//author"
            persname_path = ".//persName"
            forename_path = ".//forename"
            surname_path = ".//surname"
            sourcedesc_path = ".//sourceDesc//biblFull//titleStmt"

        # Process author information from titleStmt
        for titlestmt in root.xpath(titlestmt_path, namespaces=ns_map):
            # Skip titleStmt under sourceDesc - will be handled separately
            parent = titlestmt.getparent()
            if parent is not None and parent.tag.endswith('sourceDesc'):
                continue
                
            # Find all author elements under titleStmt
            author_elements = titlestmt.xpath(author_path, namespaces=ns_map)
            for author in author_elements:
                author_info = self._extract_author_info(author, persname_path, forename_path, surname_path, ns_map)
                if author_info:
                    results.append(author_info)

        # Process author information from sourceDesc/biblFull/titleStmt
        for sourcedesc_titlestmt in root.xpath(sourcedesc_path, namespaces=ns_map):
            author_elements = sourcedesc_titlestmt.xpath(author_path, namespaces=ns_map)
            for author in author_elements:
                author_info = self._extract_author_info(author, persname_path, forename_path, surname_path, ns_map)
                if author_info:
                    results.append(author_info)
                        
        return list(set(results))
    
    def _extract_author_info(self, author_element, persname_path, forename_path, surname_path, ns_map):
        """
        Helper method to extract author information from an author element.
        Handles the extraction of forename and surname from persName.
        """
        # First look for persName element
        persname_elements = author_element.xpath(persname_path, namespaces=ns_map)
        
        if persname_elements:
            persname = persname_elements[0]
            
            # Extract forename and surname
            forenames = persname.xpath(forename_path, namespaces=ns_map)
            surnames = persname.xpath(surname_path, namespaces=ns_map)
            
            # Construct the author name
            name_parts = []
            
            # Add forenames
            for forename in forenames:
                if forename.text:
                    # Check if it's an initial (has full="init" attribute)
                    if forename.get('full') == 'init':
                        name_parts.append(f"{forename.text.strip()}.")
                    else:
                        name_parts.append(forename.text.strip())
            
            # Add surnames
            for surname in surnames:
                if surname.text:
                    name_parts.append(surname.text.strip())
            
            # If we have any name parts, return the joined name
            if name_parts:
                return " ".join(name_parts)
            
            # If persName has direct text content but no forename/surname elements
            if persname.text and persname.text.strip():
                return persname.text.strip()
                
        # If no persName or no valid structure inside persName,
        # check if author element has direct text
        if author_element.text and author_element.text.strip():
            return author_element.text.strip()
            
        return None


class VIAFDetector(Detector):
    """
    This class is a detector for the VIAF field.
    It looks for <persName> elements in four main locations:
      1) Under <titleStmt><author>
      2) Under <titleStmt><respStmt><resp>
      3) Under <sourceDesc><biblFull><titleStmt><author>
      4) Under <sourceDesc><biblFull><titleStmt><respStmt><resp>

    Within each <persName>, it extracts:
      - The value of the 'ref' attribute (if present)
      - The text of <idno type="VIAF"> (if present)

    It returns a list of unique strings in the form:
      "<ref_attribute> - <viaf_text>"
    or just one of the two if the other is missing.
    """
    def __init__(self):
        self.field = 'viaf'
        super().__init__()

    def detect(self, root, ns, ns_map):
        """
        Detects if the VIAF field can be found in the XML content.
        Takes as input the byte representation of the XML content produced
        by the FileUpload.read() method of FastAPI.
        Uses the schemas defined by Links.
        Returns a list with the detected results.
        """

        results = []

        # Create namespace-aware path expressions
        if ns:
            # With namespace
            titlestmt_path = ".//ns:titleStmt"
            sourcedesc_path = ".//ns:sourceDesc//ns:biblFull//ns:titleStmt"
            author_persname_path = ".//ns:author//ns:persName"
            resp_persname_path = ".//ns:respStmt//ns:resp//ns:persName"
            viaf_idno_path = ".//ns:idno[@type='VIAF']"
        else:
            # No namespace
            titlestmt_path = ".//titleStmt"
            sourcedesc_path = ".//sourceDesc//biblFull//titleStmt"
            author_persname_path = ".//author//persName"
            resp_persname_path = ".//respStmt//resp//persName"
            viaf_idno_path = ".//idno[@type='VIAF']"

        # Helper function to extract ref + VIAF from a <persName>
        def extract_viaf_info(persname_element):
            """
            Extracts:
              - the 'ref' attribute from <persName>
              - all <idno type="VIAF"> texts
            Returns a list of combined strings (one for each VIAF ID found).
            """
            ref_val = persname_element.get("ref")
            viaf_id_elems = persname_element.xpath(viaf_idno_path, namespaces=ns_map)
            viaf_ids = [elem.text.strip() for elem in viaf_id_elems if elem.text]

            # If there's no VIAF and no ref, return an empty list
            if not viaf_ids and not ref_val:
                return []

            # If we have multiple VIAF IDs, pair each with ref if present
            results_local = []
            if viaf_ids:
                for viaf_id in viaf_ids:
                    if ref_val:
                        results_local.append(f"{ref_val} - {viaf_id}")
                    else:
                        results_local.append(viaf_id)
            else:
                # If no VIAF, just use the ref
                results_local.append(ref_val)
            return results_local

        # 1) Check for <persName> under <titleStmt> that is NOT under <sourceDesc>
        for titlestmt in root.xpath(titlestmt_path, namespaces=ns_map):
            parent = titlestmt.getparent()
            # Skip if the parent is <sourceDesc>, since that is handled separately
            if parent is not None and parent.tag.endswith('sourceDesc'):
                continue

            # Gather all <persName> in <author> and <respStmt><resp>
            persname_elems = titlestmt.xpath(author_persname_path, namespaces=ns_map)
            persname_elems += titlestmt.xpath(resp_persname_path, namespaces=ns_map)

            for persname in persname_elems:
                results.extend(extract_viaf_info(persname))

        # 2) Check for <persName> under <sourceDesc><biblFull><titleStmt>
        for sourcedesc_titlestmt in root.xpath(sourcedesc_path, namespaces=ns_map):
            # Gather all <persName> in <author> and <respStmt><resp>
            persname_elems = sourcedesc_titlestmt.xpath(author_persname_path, namespaces=ns_map)
            persname_elems += sourcedesc_titlestmt.xpath(resp_persname_path, namespaces=ns_map)

            for persname in persname_elems:
                results.extend(extract_viaf_info(persname))

        return list(set(results))


class ISNIDetector(Detector):
    """
    This class is a detector for the ISNI field.
    It looks for <persName> elements in four main locations:
      1) Under <titleStmt><author>
      2) Under <titleStmt><respStmt><resp>
      3) Under <sourceDesc><biblFull><titleStmt><author>
      4) Under <sourceDesc><biblFull><titleStmt><respStmt><resp>

    Within each <persName>, it extracts:
      - The value of the 'ref' attribute (if present)
      - The text of <idno type="ISNI"> (if present)

    It returns a list of unique strings in the form:
      "<ref_attribute> - <isni_text>"
    or just one of the two if the other is missing.
    """
    def __init__(self):
        self.field = 'isni'
        super().__init__()

    def detect(self, root, ns, ns_map):
        """
        Detects if the ISNI field can be found in the XML content.
        Takes as input the byte representation of the XML content produced
        by the FileUpload.read() method of FastAPI.
        Uses the schemas defined by Links.
        Returns a list with the detected results.
        """

        results = []

        # Create namespace-aware path expressions
        if ns:
            # With namespace
            titlestmt_path = ".//ns:titleStmt"
            sourcedesc_path = ".//ns:sourceDesc//ns:biblFull//ns:titleStmt"
            author_persname_path = ".//ns:author//ns:persName"
            resp_persname_path = ".//ns:respStmt//ns:resp//ns:persName"
            isni_idno_path = ".//ns:idno[@type='ISNI']"
        else:
            # No namespace
            titlestmt_path = ".//titleStmt"
            sourcedesc_path = ".//sourceDesc//biblFull//titleStmt"
            author_persname_path = ".//author//persName"
            resp_persname_path = ".//respStmt//resp//persName"
            isni_idno_path = ".//idno[@type='ISNI']"

        # Helper function to extract ref + ISNI from a <persName>
        def extract_isni_info(persname_element):
            """
            Extracts:
              - the 'ref' attribute from <persName>
              - all <idno type="ISNI"> texts
            Returns a list of combined strings (one for each ISNI ID found).
            """
            ref_val = persname_element.get("ref")
            isni_id_elems = persname_element.xpath(isni_idno_path, namespaces=ns_map)
            isni_ids = [elem.text.strip() for elem in isni_id_elems if elem.text]

            # If there's no ISNI and no ref, return an empty list
            if not isni_ids and not ref_val:
                return []

            # If we have multiple ISNI IDs, pair each with ref if present
            results_local = []
            if isni_ids:
                for isni_id in isni_ids:
                    if ref_val:
                        results_local.append(f"{ref_val} - {isni_id}")
                    else:
                        results_local.append(isni_id)
            else:
                # If no ISNI, just use the ref
                results_local.append(ref_val)
            return results_local

        # 1) Check for <persName> under <titleStmt> that is NOT under <sourceDesc>
        for titlestmt in root.xpath(titlestmt_path, namespaces=ns_map):
            parent = titlestmt.getparent()
            # Skip if the parent is <sourceDesc>, since that is handled separately
            if parent is not None and parent.tag.endswith('sourceDesc'):
                continue

            # Gather all <persName> in <author> and <respStmt><resp>
            persname_elems = titlestmt.xpath(author_persname_path, namespaces=ns_map)
            persname_elems += titlestmt.xpath(resp_persname_path, namespaces=ns_map)

            for persname in persname_elems:
                results.extend(extract_isni_info(persname))

        # 2) Check for <persName> under <sourceDesc><biblFull><titleStmt>
        for sourcedesc_titlestmt in root.xpath(sourcedesc_path, namespaces=ns_map):
            # Gather all <persName> in <author> and <respStmt><resp>
            persname_elems = sourcedesc_titlestmt.xpath(author_persname_path, namespaces=ns_map)
            persname_elems += sourcedesc_titlestmt.xpath(resp_persname_path, namespaces=ns_map)

            for persname in persname_elems:
                results.extend(extract_isni_info(persname))

        return list(set(results))


class RoleDetector(Detector):
    """
    This class is a detector for the 'role' field.
    It looks for <resp> elements in two main locations:
      1) Under <titleStmt><respStmt> (that is not itself under <sourceDesc>)
      2) Under <sourceDesc><biblFull><titleStmt><respStmt>

    It returns the text content of each <resp> found.
    """
    def __init__(self):
        self.field = 'role'
        super().__init__()

    def detect(self, root, ns, ns_map):
        """
        Detects if the 'role' field can be found in the XML content.
        Takes as input the byte representation of the XML content produced
        by the FileUpload.read() method of FastAPI.
        Uses the schemas defined by Links.
        Returns a list with the detected results (unique values).
        """

        results = []

        # Create namespace-aware path expressions
        if ns:
            # With namespace
            titlestmt_path = ".//ns:titleStmt"
            sourcedesc_titlestmt_path = ".//ns:sourceDesc//ns:biblFull//ns:titleStmt"
            resp_path = ".//ns:resp"
        else:
            # No namespace
            titlestmt_path = ".//titleStmt"
            sourcedesc_titlestmt_path = ".//sourceDesc//biblFull//titleStmt"
            resp_path = ".//resp"

        # 1) Check <resp> under <titleStmt><respStmt> (excluding those under <sourceDesc>)
        for titlestmt in root.xpath(titlestmt_path, namespaces=ns_map):
            parent = titlestmt.getparent()
            # Skip if the parent is <sourceDesc>, since that is handled separately
            if parent is not None and parent.tag.endswith('sourceDesc'):
                continue

            # Find all <resp> within <respStmt>
            resp_elements = titlestmt.xpath(resp_path, namespaces=ns_map)
            for resp_elem in resp_elements:
                if resp_elem.text:
                    results.append(resp_elem.text.strip())

        # 2) Check <resp> under <sourceDesc><biblFull><titleStmt><respStmt>
        for sourcedesc_titlestmt in root.xpath(sourcedesc_titlestmt_path, namespaces=ns_map):
            # Find all <resp> within <respStmt>
            resp_elements = sourcedesc_titlestmt.xpath(resp_path, namespaces=ns_map)
            for resp_elem in resp_elements:
                if resp_elem.text:
                    results.append(resp_elem.text.strip())

        # Return unique results
        return list(set(results))


class TypeDetector(Detector):
    """
    This class is a detector for the M8 'Type' field.
    According to the description, it looks for:
      1) <fileDesc>
      2) <titleStmt><respStmt><resp>
      3) <persName> or <orgName>

    It extracts the text content of <persName> and <orgName> elements found
    under <resp>, which indicate whether the entity associated with the selected
    role is an individual (persName) or an organisation (orgName).

    It returns a list of unique strings containing those names.
    """
    def __init__(self):
        self.field = 'type'
        super().__init__()

    def detect(self, root, ns, ns_map):
        """
        Detects if the M8 'Type' field can be found in the XML content.
        Takes as input the byte representation of the XML content produced
        by the FileUpload.read() method of FastAPI.
        Uses the schemas defined by Links.
        Returns a list with the detected results (unique values).
        """

        results = []

        # Create namespace-aware path expressions
        # We are interested in <fileDesc> -> <titleStmt><respStmt><resp> -> <persName>/<orgName>
        if ns:
            filedesc_path = ".//ns:fileDesc"
            resp_path = ".//ns:titleStmt//ns:respStmt//ns:resp"
            persName_path = ".//ns:persName"
            orgName_path = ".//ns:orgName"
        else:
            filedesc_path = ".//fileDesc"
            resp_path = ".//titleStmt//respStmt//resp"
            persName_path = ".//persName"
            orgName_path = ".//orgName"

        # 1) Find all <fileDesc> elements
        filedesc_elems = root.xpath(filedesc_path, namespaces=ns_map)
        for filedesc_el in filedesc_elems:
            # 2) Within each <fileDesc>, look for <resp> under <titleStmt><respStmt>
            resp_elems = filedesc_el.xpath(resp_path, namespaces=ns_map)
            for resp_el in resp_elems:
                # 3) Within each <resp>, extract <persName> and <orgName> text
                pers_elems = resp_el.xpath(persName_path, namespaces=ns_map)
                for p_el in pers_elems:
                    if p_el.text:
                        results.append(p_el.text.strip())

                org_elems = resp_el.xpath(orgName_path, namespaces=ns_map)
                for o_el in org_elems:
                    if o_el.text:
                        results.append(o_el.text.strip())

        # Return unique results
        return list(set(results))


class NameDetector(Detector):
    """
    This class is a detector for the M9 'Name' field.
    According to the description, it looks for:
      1) <fileDesc><titleStmt><respStmt><resp><persName>
      2) <sourceDesc><biblFull><titleStmt><respStmt><resp><persName>

    Within each <persName>, it extracts the text from:
      - <forename> (including those with full="init")
      - <surname>

    It then combines the forenames and surnames into a single string per <persName>.
    It returns a list of unique name strings (the name and surname of the person
    for a specific role, e.g., curator).
    """
    def __init__(self):
        self.field = 'm9_name'
        super().__init__()

    def detect(self, root, ns, ns_map):
        """
        Detects if the M9 'Name' field can be found in the XML content.
        Takes as input the byte representation of the XML content produced
        by the FileUpload.read() method of FastAPI.
        Uses the schemas defined by Links.
        Returns a list with the detected results (unique values).
        """

        results = []

        # Create namespace-aware path expressions
        if ns:
            # With namespace
            titlestmt_resp_path = ".//ns:fileDesc//ns:titleStmt//ns:respStmt//ns:resp"
            sourcedesc_resp_path = ".//ns:sourceDesc//ns:biblFull//ns:titleStmt//ns:respStmt//ns:resp"
            forename_path = ".//ns:forename"
            surname_path = ".//ns:surname"
        else:
            # No namespace
            titlestmt_resp_path = ".//fileDesc//titleStmt//respStmt//resp"
            sourcedesc_resp_path = ".//sourceDesc//biblFull//titleStmt//respStmt//resp"
            forename_path = ".//forename"
            surname_path = ".//surname"

        def extract_name_from_persName(persName_element):
            """
            Collects all <forename> and <surname> text under a <persName> element,
            combines them into one string, and returns it.
            """
            forenames = [
                fn.text.strip()
                for fn in persName_element.xpath(forename_path, namespaces=ns_map)
                if fn.text
            ]
            surnames = [
                sn.text.strip()
                for sn in persName_element.xpath(surname_path, namespaces=ns_map)
                if sn.text
            ]
            if forenames or surnames:
                return " ".join(forenames + surnames).strip()
            return None

        # 1) Search in <fileDesc><titleStmt><respStmt><resp><persName>
        resp_elements_titlestmt = root.xpath(titlestmt_resp_path, namespaces=ns_map)
        for resp_el in resp_elements_titlestmt:
            # Find all <persName> inside each <resp>
            persName_elems = resp_el.xpath(".//persName" if not ns else ".//ns:persName", namespaces=ns_map)
            for pers_el in persName_elems:
                name_val = extract_name_from_persName(pers_el)
                if name_val:
                    results.append(name_val)

        # 2) Search in <sourceDesc><biblFull><titleStmt><respStmt><resp><persName>
        resp_elements_sourcedesc = root.xpath(sourcedesc_resp_path, namespaces=ns_map)
        for resp_el in resp_elements_sourcedesc:
            # Find all <persName> inside each <resp>
            persName_elems = resp_el.xpath(".//persName" if not ns else ".//ns:persName", namespaces=ns_map)
            for pers_el in persName_elems:
                name_val = extract_name_from_persName(pers_el)
                if name_val:
                    results.append(name_val)

        # Return unique results
        return list(set(results))


class EditionDetector(Detector):
    """
    This class is a detector for the 'edition' field.
    It looks for <editionStmt> elements in two main locations:
      1) Under <fileDesc> (i.e., <editionStmt><edition>) that is not itself under <sourceDesc>
      2) Under <sourceDesc><biblFull><editionStmt>

    Within each <editionStmt>, it extracts the text from:
      - <note type="digital-edition">
      - <edition>

    It returns a list of unique strings (each being the text content of these elements).
    """
    def __init__(self):
        self.field = 'edition'
        super().__init__()

    def detect(self, root, ns, ns_map):
        """
        Detects if the 'edition' field can be found in the XML content.
        Takes as input the byte representation of the XML content produced
        by the FileUpload.read() method of FastAPI.
        Uses the schemas defined by Links.
        Returns a list with the detected results (unique values).
        """

        results = []

        # Create namespace-aware path expressions
        if ns:
            filedesc_editionstmt_path = ".//ns:editionStmt"
            sourcedesc_editionstmt_path = ".//ns:sourceDesc//ns:biblFull//ns:editionStmt"
            edition_path = ".//ns:edition"
            digital_note_path = ".//ns:note[@type='digital-edition']"
        else:
            filedesc_editionstmt_path = ".//editionStmt"
            sourcedesc_editionstmt_path = ".//sourceDesc//biblFull//editionStmt"
            edition_path = ".//edition"
            digital_note_path = ".//note[@type='digital-edition']"

        # 1) Check <editionStmt> in <fileDesc>, excluding those under <sourceDesc>
        #    (similar pattern to how we exclude <titleStmt> under <sourceDesc> in other detectors)
        for editionstmt in root.xpath(filedesc_editionstmt_path, namespaces=ns_map):
            parent = editionstmt.getparent()
            # Skip if the parent is <sourceDesc>, since that is handled separately
            if parent is not None and parent.tag.endswith('sourceDesc'):
                continue

            # Extract <note type="digital-edition">
            note_elems = editionstmt.xpath(digital_note_path, namespaces=ns_map)
            for note_el in note_elems:
                if note_el.text:
                    results.append(note_el.text.strip())

            # Extract <edition>
            edition_elems = editionstmt.xpath(edition_path, namespaces=ns_map)
            for ed_el in edition_elems:
                if ed_el.text:
                    results.append(ed_el.text.strip())

        # 2) Check <editionStmt> under <sourceDesc><biblFull>
        for editionstmt in root.xpath(sourcedesc_editionstmt_path, namespaces=ns_map):
            # Extract <note type="digital-edition">
            note_elems = editionstmt.xpath(digital_note_path, namespaces=ns_map)
            for note_el in note_elems:
                if note_el.text:
                    results.append(note_el.text.strip())

            # Extract <edition>
            edition_elems = editionstmt.xpath(edition_path, namespaces=ns_map)
            for ed_el in edition_elems:
                if ed_el.text:
                    results.append(ed_el.text.strip())

        # Return unique results
        return list(set(results))


class DigitalFormatDetector(Detector):
    """
    This class is a detector for the 'digital_format' field (M11).
    According to the description, it looks for:
      - <fileDesc>
      - <editionStmt><edition>
      - <note type="digital-format">
    and extracts the text of the <note type="digital-format"> element.

    It returns a list of unique strings, each representing the digital format
    (e.g., "fac-simile", "transcription", "critical edition", etc.).
    """
    def __init__(self):
        self.field = 'digital_format'
        super().__init__()

    def detect(self, root, ns, ns_map):
        """
        Detects if the 'digital_format' field can be found in the XML content.
        Takes as input the byte representation of the XML content produced
        by the FileUpload.read() method of FastAPI.
        Uses the schemas defined by Links.
        Returns a list with the detected results (unique values).
        """

        results = []

        # Create namespace-aware path expressions
        # We are interested in <fileDesc> -> <editionStmt><edition> -> <note type="digital-format">
        if ns:
            filedesc_path = ".//ns:fileDesc"
            editionstmt_path = ".//ns:editionStmt"
            edition_path = ".//ns:edition"
            digital_format_note_path = ".//ns:note[@type='digital-format']"
        else:
            filedesc_path = ".//fileDesc"
            editionstmt_path = ".//editionStmt"
            edition_path = ".//edition"
            digital_format_note_path = ".//note[@type='digital-format']"

        # Find all <fileDesc> elements
        for filedesc in root.xpath(filedesc_path, namespaces=ns_map):
            # Within <fileDesc>, look for <editionStmt> elements
            editionstmt_elems = filedesc.xpath(editionstmt_path, namespaces=ns_map)
            for editionstmt in editionstmt_elems:
                # Within each <editionStmt>, look for <edition>
                edition_elems = editionstmt.xpath(edition_path, namespaces=ns_map)
                for ed_el in edition_elems:
                    # Finally, look for <note type="digital-format"> inside <edition>
                    digital_format_notes = ed_el.xpath(digital_format_note_path, namespaces=ns_map)
                    for note_el in digital_format_notes:
                        if note_el.text:
                            results.append(note_el.text.strip())

        # Return unique results
        return list(set(results))


class EditorDetector(Detector):
    """
    This class is a detector for the M12 'Editor' field.
    According to the description, it looks for:
      1) <fileDesc><publicationStmt>
      2) <sourceDesc><biblFull><publicationStmt>
    and extracts the text of the <publisher> element (the name of the organization
    responsible for publication/distribution of the resource).

    It returns a list of unique publisher names.
    """
    def __init__(self):
        self.field = 'editor'  # or 'm12_editor' if you prefer to label it more explicitly
        super().__init__()

    def detect(self, root, ns, ns_map):
        """
        Detects if the M12 'Editor' field can be found in the XML content.
        Takes as input the byte representation of the XML content produced
        by the FileUpload.read() method of FastAPI.
        Uses the schemas defined by Links.
        Returns a list with the detected results (unique values).
        """

        results = []

        # Create namespace-aware path expressions
        # 1) <fileDesc><publicationStmt>
        # 2) <sourceDesc><biblFull><publicationStmt>
        # Then extract <publisher>.
        if ns:
            filedesc_pubstmt_path = ".//ns:fileDesc//ns:publicationStmt"
            biblfull_pubstmt_path = ".//ns:sourceDesc//ns:biblFull//ns:publicationStmt"
            publisher_path = ".//ns:publisher"
        else:
            filedesc_pubstmt_path = ".//fileDesc//publicationStmt"
            biblfull_pubstmt_path = ".//sourceDesc//biblFull//publicationStmt"
            publisher_path = ".//publisher"

        # 1) Gather all <publicationStmt> under <fileDesc>, excluding those under <sourceDesc> if necessary
        for pubstmt in root.xpath(filedesc_pubstmt_path, namespaces=ns_map):
            parent = pubstmt.getparent()
            # If you want to exclude publicationStmt under <sourceDesc> for consistency, do so:
            if parent is not None and parent.tag.endswith('sourceDesc'):
                continue

            # Find all <publisher> elements
            publisher_elems = pubstmt.xpath(publisher_path, namespaces=ns_map)
            for pub_el in publisher_elems:
                if pub_el.text:
                    results.append(pub_el.text.strip())

        # 2) Gather all <publicationStmt> under <sourceDesc><biblFull>
        for pubstmt in root.xpath(biblfull_pubstmt_path, namespaces=ns_map):
            # Find all <publisher> elements
            publisher_elems = pubstmt.xpath(publisher_path, namespaces=ns_map)
            for pub_el in publisher_elems:
                if pub_el.text:
                    results.append(pub_el.text.strip())

        # Return unique results
        return list(set(results))


class IDResourceDetector(Detector):
    """
    This class is a detector for the M13 'ID Resource' field.
    According to the description, it looks for:
      1) <fileDesc>
      2) <publicationStmt>
      3) <idno type="identifier">

    It extracts the text of each matching <idno> element, which serves
    as a unique identifier for the resource (such as a bibliographic item,
    person, title, or organisation).

    It returns a list of unique identifier strings.
    """
    def __init__(self):
        self.field = 'id_resource'
        super().__init__()

    def detect(self, root, ns, ns_map):
        """
        Detects if the M13 'ID Resource' field can be found in the XML content.
        Takes as input the byte representation of the XML content produced
        by the FileUpload.read() method of FastAPI.
        Uses the schemas defined by Links.
        Returns a list with the detected results (unique values).
        """

        results = []

        # Create namespace-aware path expressions
        # We are interested in <fileDesc> -> <publicationStmt> -> <idno type="identifier">
        if ns:
            filedesc_pubstmt_path = ".//ns:fileDesc//ns:publicationStmt"
            idno_identifier_path = ".//ns:idno[@type='identifier']"
        else:
            filedesc_pubstmt_path = ".//fileDesc//publicationStmt"
            idno_identifier_path = ".//idno[@type='identifier']"

        # 1) Gather all <publicationStmt> under <fileDesc>
        for pubstmt in root.xpath(filedesc_pubstmt_path, namespaces=ns_map):
            # Find all <idno type="identifier"> elements
            idno_elems = pubstmt.xpath(idno_identifier_path, namespaces=ns_map)
            for id_el in idno_elems:
                if id_el.text:
                    results.append(id_el.text.strip())

        # Return unique results
        return list(set(results))


class DOIDetector(Detector):
    """
    This class is a detector for the M14 'DOI' field.
    According to the description, it looks for:
      1) <fileDesc>
      2) <publicationStmt>
      3) <idno type="DOI">

    It extracts the text of each matching <idno> element, which is the unique
    string assigned to an electronic document.

    It returns a list of unique DOI strings.
    """
    def __init__(self):
        self.field = 'doi'
        super().__init__()

    def detect(self, root, ns, ns_map):
        """
        Detects if the M14 'DOI' field can be found in the XML content.
        Takes as input the byte representation of the XML content produced
        by the FileUpload.read() method of FastAPI.
        Uses the schemas defined by Links.
        Returns a list with the detected results (unique values).
        """

        results = []

        # Create namespace-aware path expressions
        # We are interested in <fileDesc> -> <publicationStmt> -> <idno type="DOI">
        if ns:
            filedesc_pubstmt_path = ".//ns:fileDesc//ns:publicationStmt"
            idno_doi_path = ".//ns:idno[@type='DOI']"
        else:
            filedesc_pubstmt_path = ".//fileDesc//publicationStmt"
            idno_doi_path = ".//idno[@type='DOI']"

        # 1) Gather all <publicationStmt> under <fileDesc>
        for pubstmt in root.xpath(filedesc_pubstmt_path, namespaces=ns_map):
            # Find all <idno type="DOI"> elements
            idno_elems = pubstmt.xpath(idno_doi_path, namespaces=ns_map)
            for id_el in idno_elems:
                if id_el.text:
                    results.append(id_el.text.strip())

        # Return unique results
        return list(set(results))


class PublicationDateDetector(Detector):
    """
    This class is a detector for the M15 'Publication date' field.
    According to the description, it looks for:
      1) <fileDesc><publicationStmt>
      2) <sourceDesc><biblFull><publicationStmt>
    and extracts the text of the <date> element, which represents
    the publication date of the digital resource.

    It returns a list of unique date strings.
    """
    def __init__(self):
        self.field = 'publication_date'
        super().__init__()

    def detect(self, root, ns, ns_map):
        """
        Detects if the M15 'Publication date' field can be found in the XML content.
        Takes as input the byte representation of the XML content produced
        by the FileUpload.read() method of FastAPI.
        Uses the schemas defined by Links.
        Returns a list with the detected results (unique values).
        """

        results = []

        # Create namespace-aware path expressions
        # We are interested in:
        #   1) <fileDesc><publicationStmt><date>
        #   2) <sourceDesc><biblFull><publicationStmt><date>
        if ns:
            filedesc_pubstmt_path = ".//ns:fileDesc//ns:publicationStmt"
            sourcedesc_pubstmt_path = ".//ns:sourceDesc//ns:biblFull//ns:publicationStmt"
            date_path = ".//ns:date"
        else:
            filedesc_pubstmt_path = ".//fileDesc//publicationStmt"
            sourcedesc_pubstmt_path = ".//sourceDesc//biblFull//publicationStmt"
            date_path = ".//date"

        # 1) Gather all <publicationStmt> under <fileDesc>, excluding those under <sourceDesc> if needed
        for pubstmt in root.xpath(filedesc_pubstmt_path, namespaces=ns_map):
            parent = pubstmt.getparent()
            # If you'd like to exclude <publicationStmt> under <sourceDesc> within <fileDesc>, do so:
            if parent is not None and parent.tag.endswith('sourceDesc'):
                continue

            date_elems = pubstmt.xpath(date_path, namespaces=ns_map)
            for date_el in date_elems:
                if date_el.text:
                    results.append(date_el.text.strip())

        # 2) Gather all <publicationStmt> under <sourceDesc><biblFull>
        for pubstmt in root.xpath(sourcedesc_pubstmt_path, namespaces=ns_map):
            date_elems = pubstmt.xpath(date_path, namespaces=ns_map)
            for date_el in date_elems:
                if date_el.text:
                    results.append(date_el.text.strip())

        # Return unique results
        return list(set(results))


class PublicationPlaceDetector(Detector):
    """
    This class is a detector for the M16 'Publication place' field.
    According to the description, it looks for:
      1) <fileDesc><publicationStmt>
      2) <sourceDesc><biblFull><publicationStmt>
    and extracts the text of the <pubPlace> element, which represents
    the name of the place where the resource was published.

    It returns a list of unique place strings.
    """
    def __init__(self):
        self.field = 'publication_place'
        super().__init__()

    def detect(self, root, ns, ns_map):
        """
        Detects if the M16 'Publication place' field can be found in the XML content.
        Takes as input the byte representation of the XML content produced
        by the FileUpload.read() method of FastAPI.
        Uses the schemas defined by Links.
        Returns a list with the detected results (unique values).
        """

        results = []

        # Create namespace-aware path expressions
        # We are interested in:
        #   1) <fileDesc><publicationStmt><pubPlace>
        #   2) <sourceDesc><biblFull><publicationStmt><pubPlace>
        if ns:
            filedesc_pubstmt_path = ".//ns:fileDesc//ns:publicationStmt"
            sourcedesc_pubstmt_path = ".//ns:sourceDesc//ns:biblFull//ns:publicationStmt"
            pubplace_path = ".//ns:pubPlace"
        else:
            filedesc_pubstmt_path = ".//fileDesc//publicationStmt"
            sourcedesc_pubstmt_path = ".//sourceDesc//biblFull//publicationStmt"
            pubplace_path = ".//pubPlace"

        # 1) Gather all <publicationStmt> under <fileDesc>, excluding those under <sourceDesc> if needed
        for pubstmt in root.xpath(filedesc_pubstmt_path, namespaces=ns_map):
            parent = pubstmt.getparent()
            # Exclude <publicationStmt> under <sourceDesc> if you need to avoid duplication
            if parent is not None and parent.tag.endswith('sourceDesc'):
                continue

            # Find all <pubPlace> elements
            pubplace_elems = pubstmt.xpath(pubplace_path, namespaces=ns_map)
            for pp_el in pubplace_elems:
                if pp_el.text:
                    results.append(pp_el.text.strip())

        # 2) Gather all <publicationStmt> under <sourceDesc><biblFull>
        for pubstmt in root.xpath(sourcedesc_pubstmt_path, namespaces=ns_map):
            # Find all <pubPlace> elements
            pubplace_elems = pubstmt.xpath(pubplace_path, namespaces=ns_map)
            for pp_el in pubplace_elems:
                if pp_el.text:
                    results.append(pp_el.text.strip())

        # Return unique results
        return list(set(results))


class IssuingAuthorityDetector(Detector):
    """
    This class is a detector for the M17 'Issuing Authority' field.
    According to the description, it looks for:
      1) <fileDesc>
      2) <publicationStmt>
      3) <authority>

    It extracts the text of each matching <authority> element, representing
    a person or agency responsible for making the resource available
    (other than a publisher or distributor).

    It returns a list of unique authority names.
    """
    def __init__(self):
        self.field = 'issuing_authority'
        super().__init__()

    def detect(self, root, ns, ns_map):
        """
        Detects if the M17 'Issuing Authority' field can be found in the XML content.
        Takes as input the byte representation of the XML content produced
        by the FileUpload.read() method of FastAPI.
        Uses the schemas defined by Links.
        Returns a list with the detected results (unique values).
        """

        results = []

        # Create namespace-aware path expressions
        # We are interested in <fileDesc><publicationStmt><authority>
        if ns:
            filedesc_pubstmt_path = ".//ns:fileDesc//ns:publicationStmt"
            authority_path = ".//ns:authority"
        else:
            filedesc_pubstmt_path = ".//fileDesc//publicationStmt"
            authority_path = ".//authority"

        # Gather all <publicationStmt> under <fileDesc>
        for pubstmt in root.xpath(filedesc_pubstmt_path, namespaces=ns_map):
            # Find all <authority> elements
            authority_elems = pubstmt.xpath(authority_path, namespaces=ns_map)
            for auth_el in authority_elems:
                if auth_el.text:
                    results.append(auth_el.text.strip())

        # Return unique results
        return list(set(results))


class AvailableInDetector(Detector):
    """
    This class is a detector for the M18 'Available in' field.
    According to the description, it looks for:
      1) <fileDesc>
      2) <publicationStmt>
      3) <availability>
      4) <p>

    It extracts the text content from <p> elements inside <availability>,
    which provide information about the resource's availability, usage restrictions,
    copyright status, or license.

    It returns a list of unique strings.
    """
    def __init__(self):
        self.field = 'available_in'
        super().__init__()

    def detect(self, root, ns, ns_map):
        """
        Detects if the M18 'Available in' field can be found in the XML content.
        Takes as input the byte representation of the XML content produced
        by the FileUpload.read() method of FastAPI.
        Uses the schemas defined by Links.
        Returns a list with the detected results (unique values).
        """

        results = []

        # Create namespace-aware path expressions
        # We are interested in <fileDesc><publicationStmt><availability><p>
        if ns:
            filedesc_pubstmt_path = ".//ns:fileDesc//ns:publicationStmt"
            availability_path = ".//ns:availability"
            p_path = ".//ns:p"
        else:
            filedesc_pubstmt_path = ".//fileDesc//publicationStmt"
            availability_path = ".//availability"
            p_path = ".//p"

        # 1) Gather all <publicationStmt> under <fileDesc>
        for pubstmt in root.xpath(filedesc_pubstmt_path, namespaces=ns_map):
            # Find all <availability> elements
            availability_elems = pubstmt.xpath(availability_path, namespaces=ns_map)
            for avail_el in availability_elems:
                # Within each <availability>, find <p> elements
                p_elems = avail_el.xpath(p_path, namespaces=ns_map)
                for p_el in p_elems:
                    if p_el.text:
                        results.append(p_el.text.strip())

        # Return unique results
        return list(set(results))


class DataLinkedResourcesDetector(Detector):
    """
    This class is a detector for the M19 'Data/Linked resources' field.
    According to the description, it looks for:
      1) <fileDesc>
      2) <publicationStmt>
      3) <listRef>
      4) <ref ...>
         (examples include type="external-image", "external-doc", "internal-image", "internal-text")
      5) <desc>

    It extracts the text content of each <desc> element inside <ref>, which
    typically contains the "title" or description of the linked resource.

    It returns a list of unique strings (the text of those <desc> elements).
    """
    def __init__(self):
        self.field = 'data_linked_resources'
        super().__init__()

    def detect(self, root, ns, ns_map):
        """
        Detects if the M19 'Data/Linked resources' field can be found in the XML content.
        Takes as input the byte representation of the XML content produced
        by the FileUpload.read() method of FastAPI.
        Uses the schemas defined by Links.
        Returns a list with the detected results (unique values).
        """

        results = []

        # Create namespace-aware path expressions
        # We are interested in <fileDesc><publicationStmt><listRef><ref><desc>
        if ns:
            filedesc_pubstmt_path = ".//ns:fileDesc//ns:publicationStmt"
            listref_path = ".//ns:listRef"
            ref_path = ".//ns:ref"
            desc_path = ".//ns:desc"
        else:
            filedesc_pubstmt_path = ".//fileDesc//publicationStmt"
            listref_path = ".//listRef"
            ref_path = ".//ref"
            desc_path = ".//desc"

        # 1) Find all <publicationStmt> under <fileDesc>
        for pubstmt in root.xpath(filedesc_pubstmt_path, namespaces=ns_map):
            # 2) Within each <publicationStmt>, look for <listRef>
            listref_elems = pubstmt.xpath(listref_path, namespaces=ns_map)
            for listref_el in listref_elems:
                # 3) Within each <listRef>, look for <ref>
                ref_elems = listref_el.xpath(ref_path, namespaces=ns_map)
                for ref_el in ref_elems:
                    # 4) Within each <ref>, look for <desc>
                    desc_elems = ref_el.xpath(desc_path, namespaces=ns_map)
                    for desc_el in desc_elems:
                        if desc_el.text:
                            results.append(desc_el.text.strip())

        # Return unique results
        return list(set(results))


class EditorialDetector(Detector):
    """
    This class is a detector for the M20 'Editorial' field.
    According to the description, it looks for:
      1) <fileDesc>
      2) <notesStmt><note>
      3) <note type="editorial">

    It extracts the text content of each <note> element whose type="editorial",
    providing an editorial note or annotation about the resource.

    It returns a list of unique editorial notes.
    """
    def __init__(self):
        self.field = 'editorial'
        super().__init__()

    def detect(self, root, ns, ns_map):
        """
        Detects if the M20 'Editorial' field can be found in the XML content.
        Takes as input the byte representation of the XML content produced
        by the FileUpload.read() method of FastAPI.
        Uses the schemas defined by Links.
        Returns a list with the detected results (unique values).
        """

        results = []

        # Create namespace-aware path expressions
        # We are interested in <fileDesc><notesStmt><note type="editorial">
        if ns:
            filedesc_path = ".//ns:fileDesc"
            notesstmt_path = ".//ns:notesStmt"
            editorial_note_path = ".//ns:note[@type='editorial']"
        else:
            filedesc_path = ".//fileDesc"
            notesstmt_path = ".//notesStmt"
            editorial_note_path = ".//note[@type='editorial']"

        # 1) Find all <fileDesc> elements
        for filedesc_el in root.xpath(filedesc_path, namespaces=ns_map):
            # 2) Within each <fileDesc>, look for <notesStmt>
            notesstmt_elems = filedesc_el.xpath(notesstmt_path, namespaces=ns_map)
            for notesstmt_el in notesstmt_elems:
                # 3) Within each <notesStmt>, look for <note type="editorial">
                editorial_notes = notesstmt_el.xpath(editorial_note_path, namespaces=ns_map)
                for note_el in editorial_notes:
                    if note_el.text:
                        results.append(note_el.text.strip())

        # Return unique results
        return list(set(results))


class OriginalEditionDetector(Detector):
    """
    This class is a detector for the M21 'Original edition' field.
    According to the description, it looks for:
      1) <fileDesc>
      2) <notesStmt><note>
      3) <note type="original-edition">

    It extracts the text content of each <note> element whose type="original-edition",
    providing a note or annotation about the original edition of the resource.

    It returns a list of unique notes.
    """
    def __init__(self):
        self.field = 'original_edition'
        super().__init__()

    def detect(self, root, ns, ns_map):
        """
        Detects if the M21 'Original edition' field can be found in the XML content.
        Takes as input the byte representation of the XML content produced
        by the FileUpload.read() method of FastAPI.
        Uses the schemas defined by Links.
        Returns a list with the detected results (unique values).
        """


        results = []

        # Create namespace-aware path expressions
        # We are interested in <fileDesc><notesStmt><note type="original-edition">
        if ns:
            filedesc_path = ".//ns:fileDesc"
            notesstmt_path = ".//ns:notesStmt"
            original_edition_note_path = ".//ns:note[@type='original-edition']"
        else:
            filedesc_path = ".//fileDesc"
            notesstmt_path = ".//notesStmt"
            original_edition_note_path = ".//note[@type='original-edition']"

        # 1) Find all <fileDesc> elements
        for filedesc_el in root.xpath(filedesc_path, namespaces=ns_map):
            # 2) Within each <fileDesc>, look for <notesStmt>
            notesstmt_elems = filedesc_el.xpath(notesstmt_path, namespaces=ns_map)
            for notesstmt_el in notesstmt_elems:
                # 3) Within each <notesStmt>, look for <note type="original-edition">
                original_edition_notes = notesstmt_el.xpath(original_edition_note_path, namespaces=ns_map)
                for note_el in original_edition_notes:
                    if note_el.text:
                        results.append(note_el.text.strip())

        # Return unique results
        return list(set(results))


class LicenceDetector(Detector):
    """
    This class is a detector for the Licence field.
    """
    def __init__(self):
        self.field = 'licence'
        super().__init__()

    def detect(self, root, ns, ns_map):
        """
        Detects if the Licence field can be found in the XML content.
        Takes as input the parsed XML root (e.g. from lxml) and the same ns, ns_map logic.
        Returns a list with the detected results.
        """
        results = []

        # Creazione dei percorsi XPath per namespace e non-namespace
        if ns:
            # Se ci sono namespace
            licence_path = ".//ns:fileDesc//ns:sourceDesc//ns:biblFull//ns:publicationStmt//ns:availability//ns:licence"
        else:
            # Se non ci sono namespace
            licence_path = ".//fileDesc//sourceDesc//biblFull//publicationStmt//availability//licence"

        # Cerca gli elementi <licence> nel path specificato
        licence_elements = root.xpath(licence_path, namespaces=ns_map)

        # Estrae il testo (se presente) da ciascun elemento <licence>
        for licence in licence_elements:
            if licence.text:
                results.append(licence.text.strip())

        # Ritorna la lista dei risultati, rimuovendo eventuali duplicati
        return list(set(results))
    

class VolumeDetector(Detector):
    """
    This class is a detector for the Volume field.
    """
    def __init__(self):
        self.field = 'volume'
        super().__init__()

    def detect(self, root, ns, ns_map):
        """
        Detects if the Volume field can be found in the XML content.
        Looks for <note type="volume"> under:
            <fileDesc><sourceDesc><biblFull><notesStmt>
        """
        results = []

        # Percorsi XPath con e senza namespace
        if ns:
            volume_path = ".//ns:fileDesc//ns:sourceDesc//ns:biblFull//ns:notesStmt//ns:note[@type='volume']"
        else:
            volume_path = ".//fileDesc//sourceDesc//biblFull//notesStmt//note[@type='volume']"

        # Cerca gli elementi <note type="volume">
        volume_elements = root.xpath(volume_path, namespaces=ns_map)

        # Aggiunge il testo di ogni <note type="volume"> alla lista dei risultati
        for volume in volume_elements:
            if volume.text:
                results.append(volume.text.strip())

        # Rimuove duplicati e restituisce i risultati
        return list(set(results))


class TotalPagesDetector(Detector):
    """
    This class is a detector for the Total Pages field.
    """
    def __init__(self):
        self.field = 'total_pages'
        super().__init__()

    def detect(self, root, ns, ns_map):
        """
        Detects if the Total Pages field can be found in the XML content.
        Looks for <note type="pages"> under:
            <fileDesc><sourceDesc><biblFull><notesStmt>
        """
        results = []

        # Percorsi XPath con e senza namespace
        if ns:
            pages_path = ".//ns:fileDesc//ns:sourceDesc//ns:biblFull//ns:notesStmt//ns:note[@type='pages']"
        else:
            pages_path = ".//fileDesc//sourceDesc//biblFull//notesStmt//note[@type='pages']"

        # Cerca gli elementi <note type="pages">
        pages_elements = root.xpath(pages_path, namespaces=ns_map)

        # Aggiunge il testo di ogni <note type="pages"> alla lista dei risultati
        for page in pages_elements:
            if page.text:
                results.append(page.text.strip())

        # Rimuove duplicati e restituisce i risultati
        return list(set(results))


class FormatDetector(Detector):
    """
    This class is a detector for the Format field.
    """
    def __init__(self):
        self.field = 'format'
        super().__init__()

    def detect(self, root, ns, ns_map):
        """
        Detects if the Format field can be found in the XML content.
        Looks for <note type="format"> under:
            <fileDesc><sourceDesc><biblFull><notesStmt>
        """
        results = []

        # Percorsi XPath con e senza namespace
        if ns:
            format_path = ".//ns:fileDesc//ns:sourceDesc//ns:biblFull//ns:notesStmt//ns:note[@type='format']"
        else:
            format_path = ".//fileDesc//sourceDesc//biblFull//notesStmt//note[@type='format']"

        # Cerca gli elementi <note type="format">
        format_elements = root.xpath(format_path, namespaces=ns_map)

        # Aggiunge il testo di ogni <note type="format"> alla lista dei risultati
        for fmt in format_elements:
            if fmt.text:
                results.append(fmt.text.strip())

        # Rimuove duplicati e restituisce i risultati
        return list(set(results))
    

class TotalDocumentsDetector(Detector):
    """
    Detector for M26 - Total documents.
    Looks for <note type="documents"> under:
        <fileDesc><sourceDesc><biblFull><notesStmt>
    """
    def __init__(self):
        self.field = 'total_documents'
        super().__init__()

    def detect(self, root, ns, ns_map):
        results = []

        # Percorso XPath con/senza namespace
        if ns:
            xpath_expr = ".//ns:fileDesc//ns:sourceDesc//ns:biblFull//ns:notesStmt//ns:note[@type='documents']"
        else:
            xpath_expr = ".//fileDesc//sourceDesc//biblFull//notesStmt//note[@type='documents']"

        elements = root.xpath(xpath_expr, namespaces=ns_map)

        for el in elements:
            if el.text:
                results.append(el.text.strip())

        return list(set(results))
    

class DigitalArchiveNameDetector(Detector):
    """
    Detector for M27 - Digital archive name.
    Looks for <note type="repository"> under:
        <fileDesc><noteStmt><note>
    """
    def __init__(self):
        self.field = 'digital_archive_name'
        super().__init__()

    def detect(self, root, ns, ns_map):
        results = []

        # Percorso XPath con/senza namespace
        if ns:
            xpath_expr = ".//ns:fileDesc//ns:notesStmt//ns:note[@type='repository']"
        else:
            xpath_expr = ".//fileDesc//notesStmt//note[@type='repository']"

        elements = root.xpath(xpath_expr, namespaces=ns_map)

        for el in elements:
            if el.text:
                results.append(el.text.strip())

        return list(set(results))
    

class PrintArchiveNameDetector(Detector):
    """
    Detector for M28 - Print archive name.
    Looks for <note type="repository"> under:
        <fileDesc><noteStmt><note>
    (Stesso percorso di DigitalArchiveNameDetector, ma con significato diverso)
    """
    def __init__(self):
        self.field = 'print_archive_name'
        super().__init__()

    def detect(self, root, ns, ns_map):
        results = []

        # Percorso XPath con/senza namespace
        if ns:
            xpath_expr = ".//ns:fileDesc//ns:notesStmt//ns:note[@type='repository']"
        else:
            xpath_expr = ".//fileDesc//notesStmt//note[@type='repository']"

        elements = root.xpath(xpath_expr, namespaces=ns_map)

        for el in elements:
            if el.text:
                results.append(el.text.strip())

        return list(set(results))
    

class DigitalArchiveCodeDetector(Detector):
    """
    Detector for M29 - Digital archive code.
    Looks for <note type="archival-code"> under:
        <fileDesc><noteStmt><note>
    """
    def __init__(self):
        self.field = 'digital_archive_code'
        super().__init__()

    def detect(self, root, ns, ns_map):
        results = []

        # Percorso XPath con/senza namespace
        if ns:
            xpath_expr = ".//ns:fileDesc//ns:notesStmt//ns:note[@type='archival-code']"
        else:
            xpath_expr = ".//fileDesc//notesStmt//note[@type='archival-code']"

        elements = root.xpath(xpath_expr, namespaces=ns_map)

        for el in elements:
            if el.text:
                results.append(el.text.strip())

        return list(set(results))
    

class PrintArchiveCodeDetector(Detector):
    """
    Detector for M30 - Print archive code.
    Looks for <note type="archival-code"> under:
        <fileDesc><noteStmt><note>
    """
    def __init__(self):
        self.field = 'print_archive_code'
        super().__init__()

    def detect(self, root, ns, ns_map):
        results = []
        
        # Percorso XPath con/senza namespace
        if ns:
            xpath_expr = ".//ns:fileDesc//ns:notesStmt//ns:note[@type='archival-code']"
        else:
            xpath_expr = ".//fileDesc//notesStmt//note[@type='archival-code']"

        elements = root.xpath(xpath_expr, namespaces=ns_map)
        for el in elements:
            if el.text:
                results.append(el.text.strip())

        return list(set(results))
    

class DigitalArchiveURLDetector(Detector):
    """
    Detector for M31 - Digital archive URL.
    Looks for <ref target="url"> under:
        <fileDesc><noteStmt><note>
    """
    def __init__(self):
        self.field = 'digital_archive_url'
        super().__init__()

    def detect(self, root, ns, ns_map):
        results = []

        # Percorso XPath con/senza namespace
        # Cerchiamo un tag <ref> con attributo target="url"
        if ns:
            xpath_expr = ".//ns:fileDesc//ns:notesStmt//ns:note//ns:ref[@target='url']"
        else:
            xpath_expr = ".//fileDesc//notesStmt//note//ref[@target='url']"

        elements = root.xpath(xpath_expr, namespaces=ns_map)
        for el in elements:
            # Il contenuto potrebbe essere testo (es. l'URL stesso) o l'attributo "target".
            # In genere, l'URL è spesso messo in un attributo 'href' o simile; 
            # ma qui, ipotizziamo che <ref> contenga del testo.
            if el.text:
                results.append(el.text.strip())

        return list(set(results))
    

class EncodingTextDetector(Detector):
    """
    Detector for M32 - Encoding text.
    Looks for <p> under:
        <encodingDesc><p><p>
    (Significa che all'interno di <encodingDesc> possono esserci uno o più <p> 
     con informazioni sulla codifica del testo.)
    """
    def __init__(self):
        self.field = 'encoding_text'
        super().__init__()

    def detect(self, root, ns, ns_map):
        results = []

        # Percorso XPath con/senza namespace
        # Qui assumiamo che i <p> siano direttamente (o nidificati) sotto <encodingDesc>.
        # Se hai bisogno di esattamente due <p> annidati, potresti cambiare l'XPath.
        if ns:
            xpath_expr = ".//ns:encodingDesc//ns:p"
        else:
            xpath_expr = ".//encodingDesc//p"

        elements = root.xpath(xpath_expr, namespaces=ns_map)
        for el in elements:
            if el.text:
                results.append(el.text.strip())

        return list(set(results))
    

class TextRecordingDetector(Detector):
    """
    Detector for M33 - Text recording.
    Looks for <p> under:
        <encodingDesc><samplingDecl>
    """
    def __init__(self):
        self.field = 'text_recording'
        super().__init__()

    def detect(self, root, ns, ns_map):
        results = []

        # Percorso XPath con/senza namespace
        if ns:
            xpath_expr = ".//ns:encodingDesc//ns:samplingDecl//ns:p"
        else:
            xpath_expr = ".//encodingDesc//samplingDecl//p"

        elements = root.xpath(xpath_expr, namespaces=ns_map)
        for el in elements:
            if el.text:
                results.append(el.text.strip())

        return list(set(results))
    

class LanguageDetector(Detector):
    """
    Detector for M34 - Language.
    Looks for <language ident="ISO-code-lang1"> under:
        <profileDesc><langUsage>
    """
    def __init__(self):
        self.field = 'language'
        super().__init__()

    def detect(self, root, ns, ns_map):
        results = []

        # Percorso XPath con/senza namespace
        if ns:
            xpath_expr = ".//ns:profileDesc//ns:langUsage//ns:language[@ident='ISO-code-lang1']"
        else:
            xpath_expr = ".//profileDesc//langUsage//language[@ident='ISO-code-lang1']"

        elements = root.xpath(xpath_expr, namespaces=ns_map)
        for el in elements:
            if el.text:
                results.append(el.text.strip())

        return list(set(results))
    

class AbstractDetector(Detector):
    """
    Detector for M35 - Abstract.
    Looks for <p> under:
        <profileDesc><abstract>
    """
    def __init__(self):
        self.field = 'abstract'
        super().__init__()

    def detect(self, root, ns, ns_map):
        results = []

        # Percorso XPath con/senza namespace
        if ns:
            xpath_expr = ".//ns:profileDesc//ns:abstract//ns:p"
        else:
            xpath_expr = ".//profileDesc//abstract//p"

        elements = root.xpath(xpath_expr, namespaces=ns_map)
        for el in elements:
            if el.text:
                results.append(el.text.strip())

        return list(set(results))
    

class KeywordDetector(Detector):
    """
    Detector for M36 - Keyword.
    Looks for <term xml:lang="ISO-code-lang1"> under:
        <profileDesc><textClass><keywords>
    """
    def __init__(self):
        self.field = 'keyword'
        super().__init__()

    def detect(self, root, ns, ns_map):
        results = []

        # Percorso XPath con/senza namespace
        if ns:
            xpath_expr = ".//ns:profileDesc//ns:textClass//ns:keywords//ns:term[@xml:lang='ISO-code-lang1']"
        else:
            xpath_expr = ".//profileDesc//textClass//keywords//term[@xml:lang='ISO-code-lang1']"

        elements = root.xpath(xpath_expr, namespaces=ns_map)
        for el in elements:
            if el.text:
                results.append(el.text.strip())

        return list(set(results))
    

class RevisionChangesDetector(Detector):
    """
    Detector for M37 - Revision changes.
    Looks for <change who="..."> under:
        <revisionDesc>
    Then collects text from <date> and <desc> children if present.
    """
    def __init__(self):
        self.field = 'revision_changes'
        super().__init__()

    def detect(self, root, ns, ns_map):
        results = []

        # Percorso XPath con/senza namespace
        if ns:
            xpath_expr = ".//ns:revisionDesc//ns:change"
        else:
            xpath_expr = ".//revisionDesc//change"

        changes = root.xpath(xpath_expr, namespaces=ns_map)

        for change_el in changes:
            # Cerchiamo i sotto-elementi <date> e <desc>
            date_el = change_el.find('./date', namespaces=ns_map)
            desc_el = change_el.find('./desc', namespaces=ns_map)

            date_text = date_el.text.strip() if (date_el is not None and date_el.text) else ""
            desc_text = desc_el.text.strip() if (desc_el is not None and desc_el.text) else ""

            # Se c'è almeno uno dei due, costruiamo un'unica stringa
            if date_text or desc_text:
                # Esempio di concatenazione "YYYY-MM-DD: Descrizione revisione"
                combined = f"{date_text}: {desc_text}".strip(" :")
                results.append(combined)

        return list(set(results))