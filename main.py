import requests, bs4, os
from ebooklib import epub

Table_Of_Contents_URL = 'https://www.parahumans.net/table-of-contents/'

def establish_ebook():
    book = epub.EpubBook()
    book.set_identifier('MaggieHolt')
    book.set_language('en')
    book.add_author('Wildbow')
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    style = 'BODY {color:white;}'
    nav_css = epub.EpubItem(uid='style_nav', file_name='style/nav.css',
                            media_type='text/css', content=style)
    book.add_item(nav_css)
    return book

class Ward:
    def __init__(self):
        toc_elements = self.get_toc_elements()
        arc_data = self.get_arc_data(toc_elements)
        self.arc_list = self.get_arc_list(arc_data)
        ebook_list = self.compile_full_ebook_list()
        book.spine = ['nav'] + ebook_list
        self.define_ebook_toc()
        epub.write_epub('ward.epub', book, {})


    def get_toc_elements(self):
        res = requests.get(Table_Of_Contents_URL)
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        raw_element_list = soup.select('#main p')
        return raw_element_list
    
    def get_arc_data(self, toc_elements):
        result = []
        for iteration, element in enumerate(toc_elements):
            if 'Arc' in str(element):
                arc_element = element
                target_index = iteration +  1
                url_element = toc_elements[target_index]
                result.append((arc_element, url_element))
        return result
            
    def get_arc_list(self, arc_data):
        arc_list = []
        for arc in arc_data:
            arc_element = arc[0]
            url_element = arc[1]
            arc_index = arc_data.index(arc)
            arc_list.append(self.Arc(arc_element, url_element, arc_index))
        return arc_list
                 
    def compile_full_ebook_list(self):
        full_ebook_list = []
        for arc in self.arc_list:
            for ebook in arc.ebook_list:
                full_ebook_list.append(ebook)
        return full_ebook_list
        
        
    def define_ebook_toc(self):
        toc = []
        for arc in self.arc_list:
            toc.append(arc.toc_item)
        book.toc = tuple(toc)


    class Arc:
        def __init__(self, arc_element, url_element, arc_index):
            self.arc_element = str(arc_element)
            self.url_element = str(url_element)
            self.index = arc_index
            self.title = self.get_arc_title()
            self.url_list = self.get_url_list()
            self.title_list = self.get_title_list()
            self.chapter_list = self.get_chapter_list()
            self.ebook_list = self.get_ebook_list()
            self.toc_item = epub.Section(self.title), tuple(self.ebook_list)
            print(f'{self.title} completed')


        def get_arc_title(self):
            target_index = self.arc_element.index('Arc')
            arc_element_draft = self.arc_element[target_index:]
            target_index_2 = arc_element_draft.find('<')
            return arc_element_draft.split('<')[0]
        
        def get_url_list(self): 
            url_list = []
            url_element_split = self.url_element.split('\n')
            for url_element in url_element_split:
                if 'https://' in url_element:
                    target_index = url_element.index('https://')
                    url_draft = url_element[target_index:]
                    target_index_2 = url_draft.index('"')
                    url = url_draft[:target_index_2]
                    url_list.append(url)
            return url_list
        
        def get_title_list(self):
            title_list = []
            url_element_split = self.url_element.split('\n')
            for url_element in url_element_split:
                if 'https://' in url_element:
                    split_1 = url_element.split('<')
                    for substring in split_1:
                        split_2 = substring.split('>')
                        for sub_substring in split_2:
                            if '.' in sub_substring and 'https://' not in sub_substring:
                                title_list.append(sub_substring)
            return title_list
        
        def get_chapter_list(self):
            chapter_list = []
            for i, url in enumerate(self.url_list):
                chapter = self.Chapter(url, self.title_list[i])
                chapter_list.append(chapter)
            return chapter_list
        
        def get_ebook_list(self):
            ebook_list = []
            for chapter in self.chapter_list:
                  ebook_list.append(chapter.ebook)
            return ebook_list    


        class Chapter:
            def __init__(self, url, title):
                self.url = url
                self.title = title
                self.content = self.get_chapter_content(self.get_raw_elements())
                self.ebook = epub.EpubHtml(title=self.title,
                                           file_name=(self.title),
                                           lang='en')
                self.ebook.content = self.content
                book.add_item(self.ebook)


            def get_raw_elements(self):
                res = requests.get(self.url)
                res.raise_for_status()
                soup = bs4.BeautifulSoup(res.text, 'html.parser')
                raw_elements = soup.select('#main p')
                return raw_elements
            
            def get_chapter_content(self, raw_elements):
                title_element = f'<h1 class="entry-title">{self.title}</h1>'
                return title_element + self.trim_chapter(raw_elements)
            
            def trim_chapter(self, raw_elements):
                content = ''
                target_index = 2 if self.title == '1.8' else 1
                for element in raw_elements[target_index:]:
                    if 'Next Chapter' not in str(element):
                        content += str(element)
                    else:
                        break
                return content
                    
book = establish_ebook()
Ward()
        
    

