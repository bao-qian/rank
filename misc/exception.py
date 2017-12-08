class NotExist(Exception):
    pass


class ErrorCode(Exception):
    def __init__(self, message, code, query):
        super().__init__(message)
        self.code = code
        self.query = query


class ErrorCode202(ErrorCode):
    pass
