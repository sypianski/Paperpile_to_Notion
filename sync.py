import bibtexparser
# import json
import os
import pickle
# import pprint
import requests

"""
TODO:
- Default icon for papers.
"""

ARCHIVE_PATH = 'archive.pk'
BIB_PATH = 'references.bib'
NOTION_TOKEN = os.environ['NOTION_TOKEN']
DATABASE_IDENTIFIER = os.environ['DATABASE_IDENTIFIER']


def notion_add_entry(
    title='',
    authors='',
    year='0',
    ref_id='',
    item_type=''
):
    # Ensure required fields are not empty
    if not title:
        raise ValueError("The 'title' parameter cannot be empty.")
    if not authors:
        raise ValueError("The 'authors' parameter cannot be empty.")
    if not ref_id:
        raise ValueError("The 'ref_id' parameter cannot be empty.")

    # Check if an entry with the same Reference ID already exists
    existing_page_id = notion_fetch_page(ref_id)
    if existing_page_id != -1:
        print(f"Entry with Reference ID '{ref_id}' already exists. Skipping creation.")
        return

    # Comment    

    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {
            'database_id': DATABASE_IDENTIFIER,
        },
        "properties": {
            'Reference ID': {
                'title': [{
                    'text': {
                        'content': ref_id,
                    }
                }]
            },
            'Authors': {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": authors,
                    }
                }],
            },
            'Year': {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": year,
                    }
                }],
            },
            'Title': {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": title,
                    }
                }],
            },
            'Item type': {
                "select": {
                    "name": item_type
                }
            },
        },
    }
    headers = {
        "Accept": "application/json",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {NOTION_TOKEN}"
    }
    response = requests.post(url, json=payload, headers=headers)


def notion_update_page(
    page_id,
    title='',
    authors='',
    year='0',
    ref_id='',
    item_type=''
):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {
        "parent": {
            'database_id': DATABASE_IDENTIFIER,
        },
        "properties": {
            'Reference ID': {
                'title': [{
                    'text': {
                        'content': ref_id,
                    }
                }]
            },
            'Authors': {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": authors,
                    }
                }],
            },
            'Year': {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": year,
                    }
                }],
            },
            'Title': {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": title,
                    }
                }],
            },
            'Item type': {
                "select": {
                    "name": item_type
                }
            },
        },
    }
    headers = {
        "Accept": "application/json",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {NOTION_TOKEN}"
    }
    response = requests.patch(url, json=payload, headers=headers)

def notion_fetch_page(ref_id):
    url = f"https://api.notion.com/v1/databases/{DATABASE_IDENTIFIER}/query"

    # list database pages
    payload = {
        "page_size": 1,
        "filter": {
            'property': 'Reference ID',
            'rich_text': {"equals": ref_id},
        },
    }
    headers = {
        "Accept": "application/json",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {NOTION_TOKEN}"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        response_data = response.json()

        if 'results' in response_data and len(response_data['results']) > 0:
            return response_data['results'][0]['id']
        else:
            return -1

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while querying the Notion API: {e}")
        return -1
    except KeyError as e:
        print(f"Unexpected response structure: missing key {e}")
        return -1
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return -1


import re

def clean_str(string):
    # Strip leading/trailing whitespace and replace newlines
    string = string.strip().replace('\n', ' ')
    
    # Dictionary of replacements for special characters
    replacements = {
        r'\\\"a': 'ä', r'\\\"e': 'ë', r'\\\"i': 'ï', r'\\\"o': 'ö', r'\\\"u': 'ü',
        r'\\\'a': 'á', r'\\\'e': 'é', r'\\\'i': 'í', r'\\\'o': 'ó', r'\\\'u': 'ú',
        r'\\\^a': 'â', r'\\\^e': 'ê', r'\\\^i': 'î', r'\\\^o': 'ô', r'\\\^u': 'û',
        r'\\\`a': 'à', r'\\\`e': 'è', r'\\\`i': 'ì', r'\\\`o': 'ò', r'\\\`u': 'ù'
    }
    
    # Perform replacements using regex
    for pattern, replacement in replacements.items():
        string = re.sub(pattern, replacement, string)

    # Remove curly braces
    string = string.replace('{', '').replace('}', '')

    # Improve quotes
    string = string.replace('``', '"')
    string = string.replace('\'\'', '"')

    return string


def main():

    # instantiate the parser
    parser = bibtexparser.bparser.BibTexParser()
    parser.ignore_nonstandard_types = True
    parser.homogenize_fields = False
    parser.interpolate_strings = False

    with open(BIB_PATH) as bib_file:
        bibliography = bibtexparser.load(bib_file, parser=parser)

    if os.path.exists(ARCHIVE_PATH):
        with open(ARCHIVE_PATH, 'rb') as archive_file:
            archive = pickle.load(archive_file)
    else:
        archive = []
    archive_ids = [e['ID'] for e in archive]

    # add each entry to notion database
    update_archive = False
    for entry in reversed(bibliography.entries):

        title = entry.get('title', '')
        title = clean_str(title)

        authors = entry.get('author', '').strip()
        if not authors:
            authors = "unknown author"  # Fallback value for missing authors
        else:
            authors = authors.replace(' and ', '; ')
            authors = clean_str(authors)

        year = entry.get('year', '')
        if not year:
            year = ""
        else:
            year = clean_str(year)
        
        item_type = entry.get('ENTRYTYPE', '')
        if not item_type:
            item_type = "unknown type"
        else:
            item_type = clean_str(item_type)

        ref_id = entry.get('ID')

        if ref_id not in archive_ids:  # New page
            notion_add_entry(
                title=title,
                authors=authors,
                year=year,
                ref_id=ref_id,
                item_type=item_type,  # Pass the type
            )
            update_archive = True
        else:  # Check if the entry has changed
            matching_entry = next((e for e in archive if e['ID'] == ref_id), None)
            if matching_entry:
                # Compare fields to detect changes
                if (
                    matching_entry.get('title', '') != title or
                    matching_entry.get('author', '').strip() != authors or
                    matching_entry.get('year', '').strip() != year or
                    matching_entry.get('type', '').strip() != item_type
                ):
                    print(f"Detected changes for ID {ref_id}:")
                    print(f"Title: {matching_entry.get('title', '')} != {title}")
                    print(f"Author: {matching_entry.get('author', '').strip()} != {authors}")
                    print(f"Year: {matching_entry.get('year', '').strip()} != {year}")
                    print(f"Type: {matching_entry.get('type', '').strip()} != {item_type}")
                    page_id = notion_fetch_page(ref_id)
                    if page_id != -1:
                        notion_update_page(
                            page_id=page_id,
                            title=title,
                            authors=authors,
                            year=year,
                            ref_id=ref_id,
                            item_type=item_type,
                        )
                        update_archive = True

    # only update the archive if necessary
    if update_archive:
        with open(ARCHIVE_PATH, 'wb') as archive_file:
            archive = [
                {
                    'ID': entry.get('ID'),
                    'title': entry.get('title', ''),
                    'author': entry.get('author', ''),
                    'year': entry.get('year', ''),
                    'type': entry.get('ENTRYTYPE', '')  # Include entry type
                }
                for entry in bibliography.entries
            ]
            pickle.dump(archive, archive_file)


if __name__ == "__main__":
    main()
