from enum import Enum, unique

@unique
class QueryState(int, Enum):
    NONE = 0
    SEARCHING_LOCAL = 1
    SEARCHING_INTERNET = 2
    PENDING = 3
    SUCCESS = 4
    ERROR = 5

class QuerySession:
    def __init__(self, state: QueryState = QueryState.NONE, result: any = None):
        self.state = state
        self.result = result

class Query:
    def __init__(self, query: str):
        self.query = query