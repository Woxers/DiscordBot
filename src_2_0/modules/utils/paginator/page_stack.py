from .page import Page

class PageStack():
    def __init__(self):
        self.stack = []

    def add(self, page: Page):
        self.stack.append(page)

    def get_last(self) -> Page:
        if (len(self.stack) > 0):
            return self.stack[-1]
        else:
            raise IndexError('PageStack is empty!')

    def previous(self):
        if (len(self.stack) > 1):
            self.stack.pop()
        else:
            raise IndexError("Can't remove last page from PageStack")