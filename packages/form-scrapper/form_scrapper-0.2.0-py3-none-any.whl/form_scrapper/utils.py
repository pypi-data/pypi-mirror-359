from bs4 import BeautifulSoup
import requests
import regex
import json

def html_getter(url):
    """
    Fetches the HTML content of a given URL.

    Args:
        url (str): The URL to fetch the HTML content from.

    Returns:
        str: The HTML content of the page.
    """
    response = requests.get(url)
    return response.text

def get_question_list(html):
    """
    Extracts a list of questions from the HTML content.

    Args:
        html (str): The HTML content of the page.

    Returns:
        list: A list of questions extracted from the HTML.
    """
    soup = BeautifulSoup(html, 'html.parser')
    divs = soup.find_all('div', jsmodel="CP1oW")
    questions = []
    for div in divs:
        question = div.attrs['data-params']
        if question:
            questions.append(question)

    return questions

def parse_question(question):
    result = regex.search(r'\[(?:[^][]+|(?R))*]',question)
    return json.loads(result.group(0)) if result else None