from secret import fusername, fpassword


class FlussApi:
    def __init__(self, hostname: str, username: str, password:str):
        self.hostname = hostname
        self.username = username
        self.password = password

            