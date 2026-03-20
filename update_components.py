import urllib.request
import os
import re
import json

# This script fetches BaseUI's documentation, extracts sections for each component,
# and saves them as individual markdown files in a local "/components" directory.
# It also generates a components_index.json with structured metadata.

def fetch_url(url):
    """Fetch URL content with error handling"""
    print(f"Fetching {url}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return None

def parse_llms_txt(content):
    """Parse the llms.txt to extract component links from the Components section"""
    components = []
    
    # Find the Components section
    components_match = re.search(r'^## Components$', content, re.MULTILINE)
    if not components_match:
        print("Could not find Components section")
        return components
    
    # Find the next section (## Utilities or end of file)
    next_section = re.search(r'^## ', content[components_match.end():], re.MULTILINE)
    if next_section:
        components_section = content[components_match.end():components_match.end() + next_section.start()]
    else:
        components_section = content[components_match.end():]
    
    # Parse component links: [ComponentName](https://base-ui.com/react/components/component-name.md): Description
    link_pattern = re.compile(r'\[([^\]]+)\]\((https://base-ui\.com/react/components/([^)]+))\)')
    
    for match in link_pattern.finditer(components_section):
        name = match.group(1)
        url = match.group(2)
        slug = match.group(3).replace('.md', '')
        
        # Find description after the link
        desc_start = match.end()
        desc_match = re.search(r': ([^\n]+)', components_section[desc_start:])
        description = desc_match.group(1).strip() if desc_match else ""
        
        components.append({
            'name': name,
            'slug': slug,
            'url': url,
            'description': description
        })
    
    return components

def parse_component_page(content, component_info):
    """Parse a component page to extract props and data attributes"""
    props = []
    data_attributes = []
    
    # Extract props from the API reference table
    # Pattern: | propName | type | default | description |
    prop_pattern = re.compile(r'\*\*([a-zA-Z]+) Props:\*\*.*?\n\| Prop\s+\| Type\s+\|.*?\n((?:\|.*?\n)+)', re.DOTALL)
    prop_match = prop_pattern.search(content)
    
    if prop_match:
        table_content = prop_match.group(2)
        # Parse table rows: | propName | type | default | description |
        row_pattern = re.compile(r'\|\s*([a-zA-Z]+)\s*\|', re.MULTILINE)
        for row_match in row_pattern.finditer(table_content):
            prop_name = row_match.group(1)
            if prop_name not in ('Prop', '---') and prop_name.isalnum():
                props.append(prop_name)
    
    # Extract data attributes from the API reference table
    # Pattern: | data-attribute | type | description |
    data_attr_pattern = re.compile(r'\*\*([a-zA-Z]+) Data Attributes:\*\*.*?\n\| Attribute\s+\| Type\s+\|.*?\n((?:\|.*?\n)+)', re.DOTALL)
    data_match = data_attr_pattern.search(content)
    
    if data_match:
        table_content = data_match.group(2)
        # Parse table rows: | data-attr | type | description |
        row_pattern = re.compile(r'\|\s*(data-[a-z-]+)\s*\|', re.MULTILINE)
        for row_match in row_pattern.finditer(table_content):
            data_attributes.append(row_match.group(1))
    
    # If no props found with table parsing, try alternative patterns
    if not props:
        # Try finding prop names from the Props section
        alt_prop_pattern = re.compile(r'\|\s*([a-zA-Z]+)\s*\|\s*[^\s]+\s*\|', re.MULTILINE)
        found_props = set()
        for row_match in alt_prop_pattern.finditer(content):
            prop = row_match.group(1)
            if prop and prop[0].islower() and prop not in ('Prop', 'Type', 'Default', 'Description'):
                found_props.add(prop)
        props = sorted(list(found_props))
    
    return props, data_attributes

def main():
    url = "https://base-ui.com/llms.txt"
    components_dir = os.path.join(os.getcwd(), "components")
    index_file = os.path.join(os.getcwd(), "components_index.json")

    if not os.path.exists(components_dir):
        os.makedirs(components_dir)

    print(f"Fetching {url}...")
    content = fetch_url(url)
    if not content:
        print("Failed to fetch llms.txt")
        return

    # Parse components from llms.txt
    components = parse_llms_txt(content)
    print(f"Found {len(components)} components")
    
    # Generate .md files for each component and build index
    index_data = {"components": {}}
    count = 0
    
    for comp in components:
        slug = comp['slug']
        
        # Fetch component page
        page_content = fetch_url(comp['url'])
        if page_content:
            # Save as .md file
            file_path = os.path.join(components_dir, f"{slug}.md")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(page_content)
            print(f"Generated {slug}.md")
            count += 1
            
            # Parse props and data attributes
            props, data_attributes = parse_component_page(page_content, comp)
            
            # Add to index
            index_data["components"][slug] = {
                "name": comp['name'],
                "description": comp['description'],
                "url": comp['url'],
                "props": props,
                "dataAttributes": data_attributes
            }
        else:
            print(f"Failed to fetch {comp['name']}")

    print(f"Successfully generated {count} component files.")

    # Write components_index.json
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2)
    print(f"Generated components_index.json with {len(index_data['components'])} components")

if __name__ == "__main__":
    main()
