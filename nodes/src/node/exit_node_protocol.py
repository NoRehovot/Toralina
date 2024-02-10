from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def make_request_to_end_point(url, headers=None, data=None):
    request = Request(url, headers=headers or {}, data=data)
    try:
        with urlopen(request, timeout=10) as response:
            print(response.status)
            return response.read(), response
    except HTTPError as error:
        print(error.status, error.reason)
    except URLError as error:
        print(error.reason)
    except TimeoutError:
        print("Request timed out")