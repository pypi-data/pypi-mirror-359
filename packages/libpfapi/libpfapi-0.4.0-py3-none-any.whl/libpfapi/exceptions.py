
class PFException(Exception):
    """
        Generic catch-all exception for the library
    """
    pass


class PFAPIException(PFException):
    """
        An error raised by the REST api (when connecting
        to the server anything that is not a 200 response)
    """
    pass


class PFModelException(PFException):
    """
        An exception for a given model. Something is not
        right even before calling the api.
    """
    pass
