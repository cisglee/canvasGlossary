import os
import re
from typing import Union
from html import escape


import confuse
from bs4 import BeautifulSoup, Tag
from canvasapi import Canvas
from htmlmin import minify

base_path = os.path.dirname(os.path.realpath(__file__))
config = confuse.Configuration('canvasGlossary', __name__)
config.set_file(os.path.join(base_path, 'config_default.yaml'), base_for_paths=True)
API_URL = config['school']['url'].get()
API_KEY = config['school']['token'].get()


def retrieve_glossary(canvas: Canvas = None, course_id: Union[str, int] = None,
                      canvas_glossary_page: str = None) -> dict:
    """
    Retrieve the global glossary page from a Canvas course, and parse it into a dictionary of terms and definitions.

    If `canvas` is not provided, a new Canvas API object will be created using the default API URL and API key specified
    in the configuration file. If `course_id` is not provided, the default course ID from the configuration file will be
    used.

    Args:
        canvas (canvasapi.Canvas, optional): A Canvas API object for making API requests. If not provided, a new object
            will be created using the API URL and API key specified in the configuration file.
        course_id (Union[str, int], optional): The ID of the course containing the global glossary page. If not
            provided, the course ID from the configuration file will be used.
        canvas_glossary_page (str, optional): The title of the Canvas page containing the glossary. If not provided, the
            glossary page name from the configuration file will be used.

    Returns:
        dict: A dictionary of terms and definitions parsed from the global glossary page. If the page cannot be found,
            an empty dictionary is returned.

    Raises:
        ValueError: If `course_id` is not provided and the course id is not specified in the configuration file.

    Example:
        >>> canvas = Canvas(API_URL, API_KEY)
        >>> glossary = retrieve_glossary(canvas, course_id=12345)
        >>> print(glossary)
        {'Term 1': 'Definition 1', 'Term 2': 'Definition 2', ...}
    """
    if canvas is None:
        canvas = Canvas(API_URL, API_KEY)
        if course_id is None:
            course_id = config['course']['course_id'].get()
    elif course_id is None:
        course_id = config['course']['course_id'].get()
        if course_id is None:
            raise ValueError('Course ID not provided.')
    if canvas_glossary_page is None:
        canvas_glossary_page = config['course']['glossary_page'].get()
        if canvas_glossary_page is None:
            raise ValueError('Glossary page name not provided.')

    course = canvas.get_course(course_id)
    pages = course.get_pages()

    for page in pages:
        if page.title.lower() == canvas_glossary_page:
            return parse_html_glossary(page.edit().body)
    else:
        return {}


def set_tool_tips(canvas: Canvas = None, course_id: Union[str, int] = None, glossary_dict: dict = None,
                  canvas_glossary_page: str = None) -> None:
    """
    Adds tool tips to terms in HTML pages of a Canvas course, based on a glossary dictionary.

    If `canvas` is not provided, a new Canvas API object will be created using the default API URL and API key specified
    in the configuration file. If `course_id` is not provided, the default course ID from the configuration file will be
    used.
    If `glossary_dict` is not provided, the global glossary for the course will be retrieved using the
    `retrieve_glossary` function.

    This function looks through all pages in the course and enriches any text that matches a term from the glossary
    dictionary with a tool tip. If a term already has a tool tip and the description is different from the description
    in the glossary dictionary, the text in the HTML is updated.

    Args:
        canvas (canvasapi.Canvas, optional): A Canvas API object for making API requests. If not provided, a new object
            will be created using the default API URL and API key specified in the configuration file.
        course_id (Union[str, int], optional): The ID of the course to set tool tips for. If not provided, the default
            course ID from the configuration file will be used.
        glossary_dict (dict, optional): A dictionary of terms and definitions to use for setting tool tips. If not
            provided, the global glossary for the course will be retrieved using the `retrieve_glossary` function.
        canvas_glossary_page (str, optional): The title of the Canvas page containing the glossary. If not provided, the
            glossary page name from the configuration file will be used.

    Returns:
        None: This function does not return anything, but modifies the HTML content of pages in the course.

    Raises:
        ValueError: If `course_id` is not provided and the course id is not specified in the configuration file.
        ValueError: If `glossary_dict` is not provided and the Canvas glossary page is not specified in the
            configuration file.

    Example:
        >>> canvas = Canvas(API_URL, API_KEY)
        >>> glossary = {'Term 1': 'Definition 1', 'Term 2': 'Definition 2', ...}
        >>> set_tool_tips(canvas, course_id=12345, glossary_dict=glossary)
    """
    if canvas is None:
        canvas = Canvas(API_URL, API_KEY)
    if course_id is None:
        course_id = config['course']['course_id'].get()
        if course_id is None:
            raise ValueError('Course ID not provided.')
    if canvas_glossary_page is None:
        canvas_glossary_page = config['course']['glossary_page'].get()
    if glossary_dict is None:
        if canvas_glossary_page is None:
            raise ValueError('Glossary dictionary not provided and no glossary page specified in configuration '
                             'file.')
        glossary_dict = retrieve_glossary(canvas, course_id)

    course = canvas.get_course(course_id)
    pages = course.get_pages()

    updated_pages = 0
    for page in pages:
        if page.title.lower() == canvas_glossary_page:
            continue
        if page.edit().body is None:
            continue
        current_body = str(page.edit().body)
        new_body = enrich_html_with_glossary(str(page.edit().body), glossary_dict)
        if current_body != new_body:
            updated_pages += 1
            page.edit(body=new_body)

    print(f"Updated {updated_pages} pages.")


def parse_html_glossary(glossary_body: str) -> dict:
    """
    Parses a description list in HTML and returns a dictionary containing
    the terms as keys and the descriptions as values.

    Args:
        glossary_body (str): The HTML code containing the description list.

    Returns:
        dict: A dictionary containing the terms as keys and the descriptions
              as values.

    Example:
        html = '''
        <dl>
          <dt>Term 1</dt>
          <dd>Description 1</dd>
          <dt>Term 2</dt>
          <dd>Description 2</dd>
        </dl>
        '''
        data = parse_description_list(html)
        # {'Term 1': 'Description 1', 'Term 2': 'Description 2'}
    """
    glossary_body = minify(glossary_body, remove_comments=True, remove_empty_space=True)
    soup = BeautifulSoup(glossary_body, 'html.parser')
    dl = soup.find('dl')
    glossary_dict = {}
    for dt, dd in zip(dl.find_all('dt'), dl.find_all('dd')):
        glossary_dict[dt.text.strip()] = dd.text.strip()
    return glossary_dict


def enrich_html_with_glossary(page_body: str, glossary_dict: dict) -> str:
    """
    Given an HTML string and a dictionary of terms and their descriptions,
    adds a tooltip with the description to each term that appears in the HTML.
    If the term already has a tooltip and the description is different from
    the description in the dictionary, updates the tooltip text.

    Args:
        page_body (str): The HTML string to add tooltips to.
        glossary_dict (dict): A dictionary of terms and their descriptions.

    Returns:
        str: The modified HTML string with tooltips added.

    Examples:
        >>> html = '<p>The quick brown fox jumps over the lazy dog.</p>'
        >>> terms_dict = {'fox': 'A mammal of the Canidae family.'}
        >>> enrich_html_with_glossary(html, terms_dict)
        '<p>The quick brown <span title="A mammal of the Canidae family.">fox</span> jumps over the lazy dog.</p>'

        >>> html = '<p>The quick brown <span title="A mammal of the Canidae family.">fox</span> jumps over the lazy dog.</p>'
        >>> terms_dict = {'fox': 'An orange fruit.'}
        >>> enrich_html_with_glossary(html, terms_dict)
        '<p>The quick brown <span title="An orange fruit.">fox</span> jumps over the lazy dog.</p>'
    """
    soup = BeautifulSoup(page_body, 'html.parser')

    for term in glossary_dict.keys():
        pattern = re.compile(re.escape(term), re.I)
        for match in soup.find_all(string=pattern):
            parent = match.parent
            if parent.name == 'span':
                if parent.get('title') != glossary_dict[term]:
                    parent['title'] = glossary_dict[term]
                continue  # Skip if the tooltip is already set and the description is the same

            match_term = re.search(r'\b{}\b'.format(term), match, re.I).group()  # Find the exact match (case sensitive)

            title = escape(glossary_dict[term])[:512]  # Truncate the title to 63 characters
            tag = Tag(name="span", attrs=[("title", title), ("style", "border-bottom: 1px dotted #000")])
            tag.string = match_term
            ntag_text = str(parent).replace(match_term, str(tag))
            ntag = BeautifulSoup(ntag_text, 'html.parser')  # Parse the new tag to avoid encoding issues

            parent.replace_with(ntag)  # Replace the old tag with the new one
            print(ntag_text)
    return str(soup)


if __name__ == "__main__":
    set_tool_tips()
