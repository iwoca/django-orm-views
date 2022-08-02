

class CyclicDependencyError(Exception):
    """Raised if views depend on one another and cause a cyclic dependency"""


class InvalidViewDepencies(Exception):
    """Raised if the view dependency list contains 2 or more views with differing database attribute"""
