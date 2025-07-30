# Form Scraper

> A Python library to scrape public Google Forms and extract questions and their properties (type, required, options, etc.).

## Installation

```bash
pip install form-scrapper
````
or

```bash
git clone https://github.com/yannickRafael/form_scrapper.git
cd form_scraper
pip -r install requirements.txt
```

## Features

* Extract all questions from a public Google Form
* Detect question type (text, multiple choice, checkboxes, etc.)
* Identify required fields
* Retrieve options for multiple choice questions

## Example Usage

```python
from form_scrapper import FormScrapper

url = 'https://google.forms.url'
questions = FormScrapper.fetch_from_url(url)
```

## Output Example

```json
{
    '672397008': {
        'Question ID': 672397008, 
        'Question Text': 'Name', 
        'Question Type': 
        'Short answer', 
        'Is Required': True, 
        'Options': []
    },
    371108883: {
        'Question ID': 371108883, 
        'Question Text': 'Phone Number (optional)', 
        'Question Type': 'Short answer', 
        'Is Required': False, 
        'Options': []
    }
}
```

## Limitations

* Only works with **public** Google Forms (no login required)
* Not guaranteed to work if Google changes the internal form structure
* Does not submit forms — only reads them


## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

```