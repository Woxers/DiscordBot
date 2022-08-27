from .page import Page

class PageList():
    def __init__(self):
        self.list = []
        self.index = 0

    def add_page(self, page: Page):
        self.list.append(page)
    
    def remove_page(self, arg):
        '''
            Remove page from PageList\n
            arg - Page or index
        '''
        if(type(arg) == int):
            self.list.pop(arg)
        elif(type(arg) == Page):
            self.list.remove(arg)
        else:
            raise TypeError(f'Type should be int or Page, received: {type(arg)}')

    def next_page(self):
        if (self.index < len(self.list) - 1):
            self.index += 1
        else:
            raise IndexError("This is the last page")
        
    def previous_page(self):
        if (self.index > 0):
            self.index -= 1
        else:
            raise IndexError("This is the first page")