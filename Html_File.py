class Html_File:
    def __init__(self, content: str, filename: str = "uploaded.html"):
        self.content = content
        self.filename = filename

    def __str__(self):
        return f"{self.filename}"

    def is_html(self):
        return self.filename.endswith(".html") or self.filename.endswith(".htm")

    def get_html(self):
        return self.content

    def set_html(self, html):
        self.content = html

    def get_html_filename(self):
        return self.filename
