import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
from bs4 import BeautifulSoup
from crawlers.crawlers import SearchCrawler, RepositoryCrawler, BaseCrawler
from crawlers.cli import CliManager
from crawlers.enums import SearchType
from crawlers.parsers import SearchParser, RepositoryParser, BaseParser


class TestCliManager(unittest.TestCase):
    @patch('builtins.input', side_effect=["keyword1 keyword2", "proxy1 proxy2", "Repositories"])
    def test_parse_input_valid(self, mock_input):
        cli_manager = CliManager()
        cli_manager.parse_input()
        self.assertEqual(cli_manager.keywords, ["keyword1", "keyword2"])
        self.assertEqual(cli_manager.proxies, ["proxy1", "proxy2"])
        self.assertEqual(cli_manager.search_type, SearchType.REPOSITORIES)
    
    @patch('builtins.input', side_effect=["keyword1 keyword2", "proxy1 proxy2", "InvalidType"])
    def test_parse_input_invalid_type(self, mock_input):
        cli_manager = CliManager()
        with self.assertRaises(ValueError):
            cli_manager.parse_input()
    
    def test_arguments(self):
        cli_manager = CliManager()
        cli_manager.keywords = ["keyword1"]
        cli_manager.proxies = ["proxy1"]
        cli_manager.search_type = SearchType.ISSUES
        expected_arguments = {
            "keywords": ["keyword1"],
            "proxies": ["proxy1"],
            "type": SearchType.ISSUES
        }
        self.assertEqual(cli_manager.arguments, expected_arguments)


class TestParsers(unittest.TestCase):
    def setUp(self):
        self.html_content = """
        <html>
            <div class='search-title'><a href='/repo1'>Repo 1</a></div>
            <span class='author'><a>author1</a></span>
            <div class='Layout-sidebar'>
                <ul class='list-style-none'>
                    <li class='d-inline'><a class='Link--secondary'><span>Python</span><span>50%</span></a></li>
                </ul>
            </div>
        </html>
        """
        self.soup = BeautifulSoup(self.html_content, 'html.parser')
    
    def test_search_parser(self):
        parser = SearchParser(self.soup)
        results = parser.parse()
        expected_results = [{'url': 'https://github.com/repo1'}]
        self.assertEqual(results, expected_results)
    
    def test_repository_parser(self):
        parser = RepositoryParser(url="https://github.com/repo1", soup=self.soup)
        results = parser.parse()
        expected_results = {
            "url": "https://github.com/repo1",
            "owner": "author1",
            "language_stats": {"Python": "50%"}
        }
        self.assertEqual(results, expected_results)


class TestCrawlers(unittest.TestCase):
    @patch('requests.get')
    def test_base_crawler_parse(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <div class='search-title'><a href='/repo1'>Repo 1</a></div>
        </html>
        """
        mock_get.return_value = mock_response

        class MockParser(BaseParser):
            def parse(self):
                return [{"url": "https://github.com/repo1"}]

        crawler = BaseCrawler(proxies=["proxy1"])
        crawler.base_url = "https://github.com/search"
        crawler.parser = MockParser
        crawler.parse()
        expected_results = [{"url": "https://github.com/repo1"}]
        self.assertEqual(crawler.get_results(), expected_results)
    
    @patch('requests.get')
    def test_repository_crawler(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <span class='author'><a>author1</a></span>
            <div class='Layout-sidebar'>
                <ul class='list-style-none'>
                    <li class='d-inline'><a class='Link--secondary'><span>Python</span><span>50%</span></a></li>
                </ul>
            </div>
        </html>
        """
        mock_get.return_value = mock_response

        crawler = RepositoryCrawler(url="https://github.com/repo1", proxies=["proxy1"])
        crawler.parse()
        expected_results = {
            "url": "https://github.com/repo1",
            "owner": "author1",
            "language_stats": {"Python": "50%"}
        }
        self.assertEqual(crawler.get_results(), expected_results)

    @patch('requests.get')
    def test_search_crawler(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <div class='search-title'><a href='/repo1'>Repo 1</a></div>
        </html>
        """
        mock_get.return_value = mock_response

        crawler = SearchCrawler(keywords=["keyword1"], type=SearchType.REPOSITORIES, proxies=["proxy1"])
        crawler.parse()
        expected_results = [{
            "url": "https://github.com/repo1",
            'owner': None, 
            'language_stats': {}
        }]
        self.assertEqual(crawler.get_results(), expected_results)


if __name__ == '__main__':
    unittest.main()