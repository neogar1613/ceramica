from utils.error_handlers import BaseErrorServer, RaisebleError


class SomeTestError(BaseErrorServer):
    """ """

class SomeRaisableError(RaisebleError):
    """ """

class UserExists(RaisebleError):
    """ """
