import requests

from cams_api import CamsApi
from fluss_api import FlussApi
import secret
import errors

if __name__ == '__main__':
    stream_name = '72261308ST-5'
    try:
        cams = CamsApi(secret.username, secret.password)
        server = cams.get_server(stream_name)
        fluss = FlussApi(server, secret.fusername, secret.fpassword)
        print(fluss.restart_stream(stream_name))
    except requests.exceptions.HTTPError as e:
        print(e)
    except errors.CameraNotAvailableWarning as e:
        print(e)
    except errors.NoneCameraWarning as e:
        print(e)
    except errors.UserNotAvailable as e:
        print(e)
    except errors.StreamNotAvailable as e:
        print(e)
