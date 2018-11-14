import logging
import re


from .constant import *
from .request_handler import send_request


class DahuaCamera:
    def __init__(self, ip_add, pswd="admin", login="admin"):
        self.timeout = 10  # changer the timeout of request here
        self.headers_xml = {'Content-Type': 'application/xml'}
        self.ip = ip_add
        self.pswd = pswd
        self.login = login
        self.auth = (login, pswd)
        self.users = []

    def _urlgen(self, url_path=""):
        # URL generator
        return "http://{}{}".format(self.ip, url_path)

    def _cgi_response_config(self, part_of_path, set_conf=True):
        if set_conf:
            url = self._urlgen('{}{}'.format(CGI_SET_CONFIG, part_of_path))
        else:
            url = self._urlgen('{}{}'.format(CGI_GET_CONFIG, part_of_path))
        return send_request('get', url, self.auth, timeout=self.timeout)

    def _turn_off_proto(self, parameter=''):
        good = 'On host {} {} was turned off'.format(self.ip, parameter)
        bad = "On host {} {} wasn't turn off".format(self.ip, parameter)
        response = self._cgi_response_config("&{}=false".format(parameter))
        return self._response_ok_check(response, good, bad)

    def _multiple_config_apply(self, parameters, type_='video', displayed_name='resolution'):
        long_url = []
        good = 'On host {} video {} was changed'.format(self.ip, displayed_name)
        bad = "On host {} video {} wasn't changed".format(self.ip, displayed_name)
        if type_ == 'video':
            func = self._video_param_gen
        elif type_ == 'ntp':
            func = self._ntp_param_gen
        else:
            logging.warning("Wrong type passed in _multiple_config_apply, must be 'video' or 'ntp'")
            return False
        for i in parameters:
            self._multiple_param_append(long_url, func(i), parameters.get(i))
        response = self._cgi_response_config(''.join(long_url))
        return self._response_ok_check(response, good, bad)

    @staticmethod
    def _multiple_param_append(long_url=list(), parameter='', value=''):
        long_url.append('&{}={}'.format(parameter, value))

    @staticmethod
    def _video_param_gen(parameter=''):
        return 'Encode[0].MainFormat[0].Video.{}'.format(parameter)

    @staticmethod
    def _ntp_param_gen(parameter=''):
        return 'NTP.{}'.format(parameter)

    @staticmethod
    def _response_ok_check(response, good_notif='', bad_notif=''):
        ex_status = False
        if response and response.status_code == 200 and re.search(r"OK", response.text):
            logging.info(good_notif)
            ex_status = True
        else:
            logging.warning(bad_notif)
        return ex_status

    def check_osd_name(self, *args):
        """
        check if channel name matching passed.
        :param args: strings that represents possible title name
        :return:  True or False, True if title name found in args and False if not found or camera didn't respond
        """
        response = self._cgi_response_config('&name=ChannelTitle', False)
        if response and response.status_code == 200:
            r = re.search(r"Name=([\w. \t]+)", response.text)
            if r.group(1) in args:
                osd_present = True
            else:
                osd_present = False
        else:
            osd_present = False
        return osd_present

    def turnoff_bad_osd(self, *args):
        """
        turnoff OSD that matches passed strings
        :param args: strings that represents bad osd text, that shouldn't be there
        :return: bool, executed status
        """
        parameter = 'VideoWidget[0].ChannelTitle.EncodeBlend'
        ex_status = False
        if not self.check_osd_name(*args):
            logging.info("{} wasn't turn off".format(parameter))
        else:
            ex_status = self._turn_off_proto(parameter)
        return ex_status

    def turnoff_upnp(self):
        """
        Turn off UPNP on device
        :return: bool, executed status
        """
        return self._turn_off_proto('UPnP.Enable')

    def turnoff_p2p(self):
        """
        Turn off p2p parameter on device
        :return: bool, executed status
        """
        return self._turn_off_proto('T2UServer.Enable')

    def turnoff_multicast(self):
        """
        Turn off multicast parameter on device
        :return: bool, executed status
        """
        return self._turn_off_proto('Multicast.RTP[0].Enable') and self._turn_off_proto('Multicast.RTP[1].Enable')

    def change_video_resolution(self, resolution="HD"):
        """
        Method to change video_resolution on dahua cameras
        :param resolution: string value: 'HD' or 'FullHD'
        :return: bool, executed status
        """
        if resolution == 'FullHD':
            height = 1080
            width = 1920
        else:
            height = 720
            width = 1280
        parameters = {
            'resolution': '{}x{}'.format(height, width),
            'Height': height, 'Width': width
                     }
        return self._multiple_config_apply(parameters, 'video', 'resolution')

    def change_video_conf(self, bitrate=2048, bitrate_type='VBR', fps=25, gop=50, video_quality=4):
        """
        Method to change video_configuration
        :param bitrate: int value between 64 and 2048
        :param bitrate_type: string, VBR or CBR values
        :param fps: int value between 1 and 25
        :param gop: int value, eq to fps or more. gop//fps > 6
        :param video_quality: int value, between 1 and 6
        :return: bool, executed status
        """
        if bitrate > 4096 or bitrate < 63:
            logging.warning('Bitrate can be set-up between 64 and 4096. Default value will be set up.')
            bitrate = 2048
        if bitrate_type not in bitrate_types:
            logging.warning('Bitrate  type shall be VBR or CBR. Default value will be set up.')
            bitrate_type = 'VBR'
        if fps < 0 or fps > 25:
            logging.warning('FPS can be set-up between 1 and 25. Default value will be set up.')
            fps = 25
        if gop//fps > 6 or gop < fps:
            logging.warning('GOP shall be more and equal to FPS.  GOP to FPS shall not be more than 6/'
                            'Default value will be set up.')
            gop = fps*2
        if video_quality < 1 or video_quality > 6:
            logging.warning('FPS can be set-up between 1 and 6. Default value will be set up.')
            video_quality = 4
        parameters = {
            'BitRate': bitrate, 'FPS': fps, 'GOP': gop,
            'Quality': video_quality, 'BitRateControl': bitrate_type
                      }
        return self._multiple_config_apply(parameters, 'video', 'configuration')

    def set_yymmdd_time(self):
        response = self._cgi_response_config('&Locales.TimeFormat=dd-MM-yyyy HH:mm:ss', True)
        good = 'On host {} time format was changed'.format(self.ip)
        bad = "On host {} time format wasn't changed".format(self.ip)
        return self._response_ok_check(response, good, bad)

    def set_ntp_settings(self, host='81.30.199.67', port=123, sync_interval=10, time_zone="+5"):
        if time_zone == "+5":
            dahtz = "7"
        elif time_zone == "+3":
            dahtz = "3"
        else:
            logging.warning("Wrong time zone in set_ntp_settings. Default value will be set up.")
            dahtz = "7"
        if port < 0 or port > 65535:
            logging.warning("Wrong port in set_ntp_settings. Default value will be set up.")
            port = 123
        if sync_interval < 10 or sync_interval > 1440:
            logging.warning("Wrong sync_interval in set_ntp_settings. Default value will be set up.")
            sync_interval = 10
        parameters = {
            'Address': host,
            'Enable': 'true',
            'Port': str(port),
            'UpdatePeriod': str(sync_interval),
            'TimeZone': str(dahtz)
        }
        return self._multiple_config_apply(parameters, 'ntp', 'configuration')


if __name__ == '__main__':
    d = DahuaCamera('10.0.179.123', 'w55H5BZK')
    d.turnoff_bad_osd('spacecam.ru')
    d.turnoff_upnp()
    d.turnoff_p2p()
    d.turnoff_multicast()
    # d.change_video_resolution('FullHD')
    d.change_video_conf(2048)
    d.set_yymmdd_time()
    d.set_ntp_settings()
