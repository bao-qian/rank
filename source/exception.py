from source.utility import log_error


class NotExist(Exception):
    pass


class ErrorCode(Exception):
    def __init__(self, code, query):
        message = f'error code <{code}> for <{query}>'
        log_error(message)
        super().__init__(message)
        self.code = code
        self.query = query


class ErrorCode202(ErrorCode):
    # https://developer.github.com/v3/repos/statistics/
    pass


class ErrorCode451(ErrorCode):
    # https://developer.github.com/changes/2016-03-17-the-451-status-code-is-now-supported/
    pass
