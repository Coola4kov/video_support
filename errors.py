class NoneCameraWarning(Exception):
    def __init__(self, camera_number: str):
        self.camera_number = camera_number

    def __str__(self):
        return 'Камера {} не найдена'.format(self.camera_number)


class CameraNotAvailableWarning(NoneCameraWarning):
    def __str__(self):
        return 'Камера {} не доступна'.format(self.camera_number)


class UserNotAvailable(Exception):
    def __init__(self, username: str):
        self.username = username

    def __str__(self):
        return 'Не верные данные пользователя {}'.format(self.username)


class StreamNotAvailable(Exception):
    def __init__(self, stream_name: str):
        self.stream_name = stream_name

    def __str__(self):
        return 'Поток {} не доступен'.format(self.stream_name)

