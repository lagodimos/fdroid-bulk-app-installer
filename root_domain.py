from urllib.parse import urlparse

def root_domain(url: str):
    domain = urlparse(url).netloc
    domain = domain.split(".")
    domain = domain[-2] + "." + domain[-1]

    return domain
