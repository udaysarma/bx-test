from bs4 import BeautifulSoup
from urllib.parse import urljoin
from copy import deepcopy

class FormParser:
    def __init__(self, html_content, base_url=None):
        self.html_content = html_content
        self.base_url = base_url

    def strip_forms_and_inputs(self, forms):
        sforms = []
        for form in forms:
            sforms.append(self.strip_css_paths(form))
        return sforms

    def strip_css_paths(self, form):
        sform = deepcopy(form)
        sform.pop('css_path')
        for input in sform['inputs']:
            input.pop('css_path')
        return sform

    def get_css_path(self, element):
        """
        Generate a CSS path for a given BeautifulSoup element
        """
        path = []
        
        while element and element.name:
            # Build selector for current element
            selector = element.name
            
            # Add ID if present
            if element.get('id'):
                selector += f"#{element['id']}"
                path.append(selector)
                break  # ID is unique, so we can stop here
            
            # Add classes if present
            if element.get('class'):
                classes = '.'.join(element['class'])
                selector += f".{classes}"
            
            # Add attribute selectors for uniqueness if needed
            parent = element.parent
            if parent:
                siblings = parent.find_all(element.name, recursive=False)
                if len(siblings) > 1:
                    # Add nth-child selector if there are multiple siblings
                    index = siblings.index(element) + 1
                    selector += f":nth-child({index})"
            
            path.append(selector)
            element = element.parent
        
        return ' > '.join(reversed(path))

    def parse_forms_from_html(self, html_content, base_url=None):
        """
        Parse HTML content and extract form details including input names, action, and method
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        forms_data = []
        
        # Find all forms
        forms = soup.find_all('form')
        
        for i, form in enumerate(forms):
            form_info = {
                'form_index': i + 1,
                'action': form.get('action', ''),
                'method': form.get('method', 'GET').upper(),
                'id': form.get('id', ''),
                'class': form.get('class', []),
                'inputs': [],
                'css_path': self.get_css_path(form)
            }
            
            # Make action URL absolute if base_url provided
            if base_url and form_info['action']:
                form_info['action'] = urljoin(base_url, form_info['action'])
            
            # Find all form elements (input, select, textarea)
            form_elements = form.find_all(['input', 'textarea'])
            
            for element in form_elements:
                element_info = {
                    'tag': element.name,
                    'name': element.get('name', ''),
                    'type': element.get('type', ''),
                    'value': element.get('value', ''),
                    'id': element.get('id', ''),
                    'required': element.has_attr('required'),
                    'placeholder': element.get('placeholder', ''),
                    'css_path': self.get_css_path(element)
                }
                
                form_info['inputs'].append(element_info)
            
            forms_data.append(form_info)
        
        return forms_data
