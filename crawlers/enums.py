from enum import Enum


class SearchType(Enum):
    REPOSITORIES = 'Repositories'
    ISSUES = 'Issues'
    WIKIS = 'Wikis'
    
    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_