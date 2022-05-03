

class User:

    def __init__(self, response):
        self.response = response

    @property
    def id(self):
        return self.response.id

    @property
    def fn(self):
        return self.response.first_name

    @property
    def ln(self):
        return self.response.last_name

    @property
    def full_name(self):
        return f"{self.fn} {self.ln}"

    def __format__(self, format_spec: str):
        format_spec = format_spec.replace(
            'fn', self.fn
        ).replace(
            'ln', self.ln
        ).replace(
            "full_name", self.full_name
        ).replace(
            'id', f"{self.id}"
        )

        if format_spec.startswith('@'):
            return f'@id{self.id} ({format_spec[1:]})'
        return format_spec
