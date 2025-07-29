class Error(Exception):
    pass


class DatabaseError(Error):
    pass


class NotSupportedError(DatabaseError):
    pass
