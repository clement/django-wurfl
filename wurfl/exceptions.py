class NoMatch(Exception):
    """
    No match has been found for a user_agent search
    """
    pass
    
class ParseError(Exception):
    """
    An error has been detected while parsing a WURFL resource file
    """
    pass
