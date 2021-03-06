import requests

from cams_api import CamsApi
from fluss_api import FlussApi
import secret
import errors

if __name__ == '__main__':
    stream_name = '1541853609DUS542'
    try:
        cams = CamsApi(secret.username, secret.password)
        account_activity = cams.get_cameras_parameters(stream_name, 'contractActive')
        camera_token = cams.get_cameras_parameters(stream_name, 'token')
        server = cams.get_cameras_parameters(stream_name, 'server')
        fluss = FlussApi(server, secret.fusername, secret.fpassword, camera_token)
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

# TODO camera password check
# TODO camera actual model check
# TODO UGIN camera model fix
# TODO camera time fix
# TODO camera get to the right condition
# TODO assign camera name
# TODO flussonic archive status
