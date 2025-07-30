from form_scrapper.question import Question
from form_scrapper.utils import html_getter, get_question_list, parse_question

class FormScrapper:
    def fetch_from_url(url):
        html = html_getter(url)

        questions = get_question_list(html)

        objs = []
        for question in questions:
            raw = parse_question(question)
            if raw:
                objs.append(Question(raw))

        dict = {}    
        for obj in objs:
            dict[obj.id] = obj.to_dict()

        return(dict)