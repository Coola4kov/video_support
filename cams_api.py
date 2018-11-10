import requests

import secret as s
import errors


class CamsApi:

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.token = None
        self.camera_url = 'http://cams.ufanet.ru/api/v3/cameras/{}/token'
        self.auth_url = 'http://cams.ufanet.ru/api/v3/auth/login-jwt'
        self._auth()

    def _auth(self):
        logpass = dict([('username', self.username), ('password', self.password)])
        r = requests.post(self.auth_url, json=logpass)
        if r.status_code == 400:
            raise errors.UserNotAvailable(self.username)
        r.raise_for_status()
        self.token = r.json()['token']

    def get_server(self, number: str) -> str:
        headers = {'Authorization': 'JWT {}'.format(self.token)}
        r = requests.get(self.camera_url.format(number), headers=headers)
        if r.status_code == 404:
            raise errors.NoneCameraWarning(number)
        elif r.status_code == 500:
            raise errors.CameraNotAvailableWarning(number)
        r.raise_for_status()
        return r.json()['server']


if __name__ == '__main__':
    try:
        test = CamsApi(s.username, s.password)
        print(test.get_server("0"))
    except requests.exceptions.HTTPError as e:
        print(e)
    except errors.CameraNotAvailableWarning as e:
        print(e)
    except errors.NoneCameraWarning as e:
        print(e)
    except errors.UserNotAvailable as e:
        print(e)
