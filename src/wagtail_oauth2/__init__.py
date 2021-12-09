import pkg_resources

try:
    __version__ = pkg_resources.get_distribution("wagtail_oauth2").version
except pkg_resources.DistributionNotFound:
    # Read the docs does not support poetry and cannot install the package
    __version__ = None
