from .enums import SearchType

class CliManager:
    '''
    Manager for parsing initial data from command line inputs
    :parse_input - main method of class. Receives 3 different inputs for 
        keywords, proxies and search_type initialization.
    '''
    
    def __init__(self):
        self.keywords = []
        self.proxies = []
        self.search_type = None

    def parse_input(self):
        keywords_input = input("Enter keywords (separated by space): ")
        proxies_input = input("Enter proxies (separated by space): ")
        search_type_input = input(f"Enter search type (Options: {', '.join(e.value for e in SearchType)}): ")

        #converting keywords and proxies strings to list of values
        self.keywords = keywords_input.split()
        self.proxies = proxies_input.split()

        #checking if inputet by user type is avaliable
        if SearchType.has_value(search_type_input):
            self.search_type = SearchType(search_type_input)
        else:
            raise ValueError(f"Invalid search type: {search_type_input}. Available types are: {', '.join(e.value for e in SearchType)}")
    
    @property
    def arguments(self):
        return {
            "keywords": self.keywords,
            "proxies": self.proxies,
            "type": self.search_type
        }