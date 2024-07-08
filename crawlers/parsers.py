
class BaseParser:
    """
    A base class for parsers that provides a common interface for parsing HTML content.
    """
    def __init__(self, soup) -> None:
        """
        Initialize the parser with a BeautifulSoup object.
        
        :param soup: BeautifulSoup object to parse.
        """
        self.soup = soup

    def parse(self):
        """
        Parse the HTML content.
        
        This method should be implemented by subclasses.
        
        :raises NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError()

    
class SearchParser(BaseParser):
    """
    A parser for extracting search results from GitHub search pages.
    """
    
    def parse(self):
        """
        Parse the links of search results from the BeautifulSoup object.
        
        :return: List of dictionaries containing the URLs of the search results.
        """
        results = []
        divs = self.soup.find_all('div', class_='search-title')
        for div in divs:
            a_tag = div.select_one('a')
            if a_tag and 'href' in a_tag.attrs:
                results.append({
                    "url": 'https://github.com' + a_tag.attrs['href']
                })
        return results
                

class RepositoryParser(BaseParser):
    """
    A parser for extracting details from GitHub repository pages.
    """
    
    def __init__(self, url, **kwargs) -> None:
        self.url = url
        super().__init__(**kwargs)
    
    def parse(self):
        """
        Parse the repository details(owner, language stats) from the BeautifulSoup object.
        
        :return: Dictionary containing the repository URL, owner, and language statistics.
        """
        return {
            "url": self.url,
            "owner": self.get_owner(),
            "language_stats": self.get_language_stats()
        }
    
    def get_owner(self):
        """
        Get the owner of the repository.
        
        :return: Owner of the repository as a string.
        """
        span = self.soup.select_one("span.author a")
        if span and span.text:
            return span.text.strip()
    
    def get_language_stats(self):
        """
        Get the language statistics of the repository.
        
        :return: Dictionary of language statistics.
        """
        langs = self.soup.select("div.Layout-sidebar ul.list-style-none li.d-inline a.Link--secondary")
        values = []
        for lang in langs:
            values.append([span.text.strip() for span in lang.select("span")])
        return dict(values)