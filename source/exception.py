from utility import log_error


class NotExist(Exception):
    pass


class ErrorCode(Exception):
    def __init__(self, code, query):
        message = f'error code <{code}> for <{query}>'
        log_error()
        super().__init__(message)
        self.code = code
        self.query = query


class ErrorCode202(ErrorCode):
    pass
