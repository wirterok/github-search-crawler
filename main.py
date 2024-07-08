from crawlers.crawlers import SearchCrawler
from crawlers.cli import CliManager
import json

if __name__ == "__main__":
    # input_data = {
    #     "keywords": ["openstack", "nova", "css"],
    #     "proxies": ["194.126.37.94:8080", "13.78.125.167:8080"],
    #     "type": "Repositories"
    # }
    
    cli = CliManager()
    cli.parse_input()
    
    crawler = SearchCrawler(**cli.arguments)
    crawler.parse()
    results = crawler.get_results()

    print(json.dumps(results, indent=2))
