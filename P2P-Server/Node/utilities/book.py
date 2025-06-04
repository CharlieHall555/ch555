"""A helper class to make the storing of the local blockchain for display easier"""

class Book:
    def __init__(self, data: list, page_size: int):
        self.page_size = page_size
        self.pages = []

        # Make a copy to avoid mutating the original list
        data_copy = data[:]
        
        # Paginate the data
        for i in range(0, len(data_copy), page_size):
            page = data_copy[i:i + page_size]
            self.pages.append(page)
        
        self.length = len(self.pages)

    def get_page(self, page_number: int):
        if 0 <= page_number < self.length:
            return self.pages[page_number]
        else:
            raise IndexError(f"Page number {page_number} is out of range. Book has {self.length} pages.")