import requests

from secret import fusername, fpassword
import errors


class FlussApi:
    def __init__(self, hostname: str, username: str, password:str):
        self.username = username
        self.password = password
        self.auth = (username, password)
        self.api_url = 'http://{}/flussonic/api/'.format(hostname)
        self.stream_res_url = '{}stream_restart/'.format(self.api_url)

    def restart_stream(self, stream_name: str):
        r = requests.get(self.stream_res_url + stream_name, auth=self.auth)
        if r.status_code == 400:
            raise errors.StreamNotAvailable(stream_name)
        elif r.status_code == 401:
            raise errors.UserNotAvailable(self.username)
        r.raise_for_status()
        if 'true' in r.text:
            result = True
        else:
            result = False
        return result


if __name__ == '__main__':
    test = FlussApi('flussonic-1.cams.ufanet.ru', fusername, fpassword)
    print(test.restart_stream('001-107-004'))

