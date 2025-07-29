from .sgfcmed_parallel import SGFCMedParallel
__all__ = ["SGFCMedParallel"]

def __version__():
    """Return the version of the simple_stats package."""
    return "0.0.1"

def describe():
    """Print a description of the package and its features."""
    description = (
        "String Grammar Fuzzy C-Medians Library\n"
        "Version: {}\n"
        "Features:\n"
        "   - fit()\n"
        "   - membership()\n"
        "   - prototypes()\n"
        "   - predict()\n"
    ).format(__version__())
    print(description)
