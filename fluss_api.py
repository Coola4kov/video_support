import time

import requests

from secret import fusername, fpassword
import errors


class FlussApi:
    def __init__(self, hostname: str, username: str, password: str, token=None):
        self.username = username
        self.password = password
        self.auth = (username, password)
        self.token = token
        self.hostname_url = 'http://{}/'.format(hostname)
        self.api_url = '{}flussonic/api/'.format(self.hostname_url)
        self.stream_res_url = '{}stream_restart/'.format(self.api_url)
        self.stream_status_url = '{}stream_health/'.format(self.api_url)
        self.archive_status_url = self.hostname_url + '{}/recording_status.json'

    def restart_stream(self, stream_name: str):
        r = requests.get(self.stream_res_url + stream_name, auth=self.auth)
        if r.status_code == 400 or r.status_code == 404:
            raise errors.StreamNotAvailable(stream_name)
        elif r.status_code == 401:
            raise errors.UserNotAvailable(self.username)
        r.raise_for_status()
        if 'true' in r.text:
            result = True
        else:
            result = False
        return result

    def check_stream(self, stream_name: str):
        r = requests.get(self.stream_status_url + stream_name, auth=self.auth)
        result = True
        if r.status_code == 401:
            raise errors.UserNotAvailable(self.username)
        elif r.status_code == 424:
            result = False
        else:
            r.raise_for_status()
        return result

    def camera_archive_status(self, stream_name: str):
        r = requests.get(self.archive_status_url.format(stream_name),
                         params={'token': self.token, 'from': int(time.time() - 300)})
        r.raise_for_status()
        temp_json = r.json()
        condition = {'dvr': False, 'jump': True, 'whole': False}
        if temp_json:
            condition['dvr'] = True
            if len(temp_json[0]['ranges']) == 1:
                condition['jump'] = False
                if temp_json[0]['ranges'][0]['duration'] > 290:
                    condition['whole'] = True
        return condition


if __name__ == '__main__':
    test = FlussApi('flussonic-1.cams.ufanet.ru', fusername, fpassword, '78a6f9d3d31f449c8ba0f242596e3be9')
    # print(test.restart_stream('001-060-005'))
    print('Состояние потока', test.check_stream('1475054931'))
    test.camera_archive_status('1475054931')
    print(test.camera_archive_status('1475054931'))
