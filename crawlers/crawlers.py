import requests
from bs4 import BeautifulSoup
import random
from .parsers import SearchParser, RepositoryParser, BaseParser
from .enums import SearchType
from concurrent.futures import ThreadPoolExecutor, as_completed


class BaseCrawler:
    """
    A base class for web crawlers that provides common functionality
    for sending requests and parsing responses.
    """
    
    base_url: str = ""
    error_message: str = ""
    results: list | dict
    parser: BaseParser
    
    def __init__(self, proxies):
        """
        Initialize the crawler with a list of proxy addresses.
        
        :param proxies: List of proxy addresses to use for requests.
        """
        self.proxies = proxies
        
    def get_proxy(self):
        """
        Initialize the crawler with a list of proxy addresses.
        
        :param proxies: List of proxy addresses to use for requests.
        """
        return {'http': random.choice(self.proxies)}
    
    def get_headers(self):
        """
        Get the headers to use for requests.
        
        :return: Dictionary of headers.
        """
        return {
            'Content-Type': "text/html",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def parse(self, **kwargs):
        """
        Send a GET request to the base URL with given parameters and parse the response.
        
        :param params: Dictionary of query parameters for the request.
        """
        response = requests.get(
            self.base_url,
            headers=self.get_headers(), 
            proxies=self.get_proxy(),
            **kwargs
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            self.parse_results(soup)
        else:
            print(f"{self.error_message}. Status code: {response.status_code}")
    
    def parse_results(self, soup):
        """
        Parse the results from the BeautifulSoup object.
        Uses initialized 'parser' class to extract needed data and sets it to results variable
        
        :param soup: BeautifulSoup object to parse.
        """
        if self.parser is None:
            raise NotImplementedError("parser class should be setted")
        self.results = self.parser(soup=soup).parse()
    
    def get_results(self):
        """
        Get the parsed results.
        
        :return: Parsed results as a list or dictionary.
        """
        return self.results


class RepositoryCrawler(BaseCrawler):
    """
    A crawler for GitHub repositories, inheriting from BaseCrawler.
    """
    error_message = "Failed to retrieve repository"
    
    def __init__(self, url, **kwargs):
        super().__init__(**kwargs)
        self.base_url = url
    
    def parse_results(self, soup):
        """
        Parse the results for the repository using parsers.RepositoryParser
        
        :param soup: BeautifulSoup object to parse.
        """
        self.results = RepositoryParser(url=self.base_url, soup=soup).parse()


class SearchCrawler(BaseCrawler):
    """
    A crawler for GitHub search results, inheriting from BaseCrawler.
    """
    base_url = "https://github.com/search"
    error_message = "Failed to retrieve search results"
    parser = SearchParser
    
    def __init__(self, keywords, type: SearchType, **kwargs):
        """
        Initialize the search crawler with keywords and search type.
        
        :param keywords: List of keywords to search for.
        :param type: Type of search (repositories, issues, wikis).
        """
        super().__init__(**kwargs)
        self.keywords = keywords
        self.search_type = type
        self.results = []

    def parse(self):
        """
        Perform the search query params and parse the results.
        """
        query = "+".join(self.keywords)
        super().parse(
            params={
                'q': query,
                'type': self.search_type.value.lower()
            }
        )

    def fetch_repo_details(self, url):
        """
        Fetch details for a specific repository URL using RepositoryCrawler
        
        :param url: URL of the repository to fetch details for.
        :return: Parsed repository details.
        """
        crawler = RepositoryCrawler(url=url, proxies=self.proxies)
        crawler.parse()
        return crawler.get_results()
        
    
    def parse_results(self, soup):
        """
        Parse the search results and, if the search type is repositories,
        fetch additional details for each repository.
        
        :param soup: BeautifulSoup object to parse.
        """
        super().parse_results(soup)
        
        if self.search_type != SearchType.REPOSITORIES:
            return
        
        new_results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {executor.submit(self.fetch_repo_details, repo['url']): repo['url'] for repo in self.results}
            for future in as_completed(future_to_url):
                result = future.result()
                if result:
                    new_results.append(result)
        
        self.results = new_results
       
        

    