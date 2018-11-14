import requests
import logging


def send_request(method="get", url="", auth=("", ""), data="", header=None, timeout=20, files=""):
    response = ''
    try:
        if method.lower() == "get":
            response = requests.get(url, data, auth=auth, timeout=timeout)
        elif method.lower() == "put":
            response = requests.put(url, data, auth=auth, headers=header, timeout=timeout, files=files)
        elif method.lower() == "post":
            response = requests.post(url, data, auth=auth, headers=header, timeout=timeout)
        else:
            logging.warning("Method '{}' isn't supported".format(method))
        response.raise_for_status()
    # Handling the exceptions
    except requests.exceptions.HTTPError as err:
        logging.warning(err)
        # raise UserWarning(err)
    except requests.exceptions.Timeout:
        logging.warning("Host didn't responded in {} s, try different timing or different host".format(timeout))
        # raise UserWarning("Host didn't responded in {} s, try different timing or different host".format(timeout))
    except requests.exceptions.TooManyRedirects:
        logging.warning("Try different host, too many redirects")
        # raise UserWarning("Try different host, too many redirects")
    except requests.exceptions.RequestException as err:
        logging.warning(err)
        # raise UserWarning(err)
    finally:
        return response

