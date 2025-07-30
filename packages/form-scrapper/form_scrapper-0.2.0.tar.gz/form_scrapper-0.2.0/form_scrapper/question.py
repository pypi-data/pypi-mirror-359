from form_scrapper.config import Config

class Question:
    def __init__(self, raw_data):
        self.raw = raw_data
        self.id = self.get_question_id()
        self.text = self.get_question_text()
        self.type_code = self.get_question_type_code()
        self.type = (Config.QUESTION_TYPES).get(self.type_code, f"Unknown ({self.type_code})")
        self.required = self.is_required()
        self.options = self.get_options()

    def get_question_id(self):
        return self.raw[0]

    def get_question_text(self):
        try:
            return self.raw[1] or (self.raw[17][1] if len(self.raw) > 17 and self.raw[17] else "N/A")
        except:
            return "N/A"

    def get_question_type_code(self):
        return self.raw[3]

    def is_required(self):
        try:
            return self.raw[4][0][2] is True
        except:
            return False

    def get_options(self):
        try:
            if self.type_code in [2, 3, 4]:  # Types with options
                return [opt[0] for opt in self.raw[4][0][1] if opt]
            return []
        except:
            return []

    def to_dict(self):
        return {
            "Question ID": self.id,
            "Question Text": self.text,
            "Question Type": self.type,
            "Is Required": self.required,
            "Options": self.options
        }

    def __str__(self):
        info = self.to_dict()
        return "\n".join(f"{key}: {value}" for key, value in info.items())