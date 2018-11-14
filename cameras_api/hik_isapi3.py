import logging
from time import localtime
import xml.etree.ElementTree as ET

from request_handler import send_request


def XmlChildCreator(top, tag, value=None):
    # function for creation of children in XML
    child = ET.SubElement(top, tag)
    if value:
        child.text = str(value)
    return child


#############################
#   CLASS HIKVISION         #
#############################
class HikCamera:
    def __init__(self, ip_add="", pswd="admin", login="admin"):
        # print ("######################################")
        # print ("working with camera= {}".format(ip_add))
        self.timeout = 10  # change the timeout of request here
        self.headers_xml = {'Content-Type': 'application/xml'}
        self.ip = ip_add
        self.pswd = pswd
        self.login = login
        self.auth = (login, pswd)
        self.model = ''
        self.SN = ''
        self.MAC = ''
        self.firmware = ''
        self.firmware_relis = ''
        self.users = []

    def _urlgen(self, url_path=""):
        # URL generator
        return "http://" + self.ip + url_path

    def device_info(self):
        # Get the device information
        url_di = self._urlgen("/ISAPI/System/deviceInfo")
        try:
            response_di = send_request("get", url=url_di, auth=self.auth)
            xmltree_di = ET.fromstring(response_di.text)
            self.model = xmltree_di[5].text
            self.SN = xmltree_di[6].text
            self.MAC = xmltree_di[7].text
            self.firmware = xmltree_di[8].text
            self.firmware_relis = xmltree_di[9].text
            logging.info("Device info received")
            return response_di
        except:
            logging.warning("Didn't get the device info")

    def device_ntp_update(self, address_format="ipaddress", host="81.30.199.67", port="123", sync_interval="10"):
        # update the NTP server
        # address_format = ipaddress or hostname

        # Generate the XML tree
        top = ET.Element("NTPServer", {"version": "2.0", "xmlns": "http://www.std-cgi.com/ver20/XMLSchema"})
        XmlChildCreator(top, "id", 1)
        XmlChildCreator(top, "addressingFormatType", address_format)
        if address_format == "ipaddress":
            XmlChildCreator(top, "ipAddress", str(host))
        elif address_format == "hostname":
            XmlChildCreator(top, "hostName", str(host))
        else:
            logging.warning("Wrong address_format in XML for device_ntp_update")
            return
        XmlChildCreator(top, "portNo", str(port))
        XmlChildCreator(top, "synchronizeInterval", str(sync_interval))

        # Generate the URL for request
        url_dntp_upd = self._urlgen("/ISAPI/System/time/ntpServers/1")

        try:
            response_dntp_upd = send_request("put", url_dntp_upd, data=ET.tostring(top, encoding="utf8", method="xml"),
                                             auth=self.auth, header=self.headers_xml)
            #            tree_dntp_upd = ET.fromstring(response_dntp_upd.text)
            #            if (tree_dntp_upd[1].text == "1"):
            logging.info("NTP changed")
            return response_dntp_upd

        except:
            logging.warning("NTP didn't change")

    def device_set_ntp_mode(self, timezone="+5"):
        # set camera to update through the NTP and timezone = +5 or +3
        t = localtime()
        # configure XML string

        top = ET.Element("Time", {"version": "2.0", "xmlns": "http://www.std-cgi.com/ver20/XMLSchema"})
        XmlChildCreator(top, "timeMode", "NTP")
        timeforxml = str(t.tm_year) + "-" + str(t.tm_mon) + "-" + str(t.tm_mday) + "T" + str(t.tm_hour) + ":"
        timeforxml += str(t.tm_min) + ":" + str(t.tm_sec)
        if timezone == "+5":
            timeforxml += "+05:00"
            XmlChildCreator(top, "timeZone", "CST-5:00:00")
        elif timezone == "+3":
            timeforxml += "+03:00"
            XmlChildCreator(top, "timeZone", "CST-3:00:00")
        else:
            logging.warning("Wrong time zone in device_set_ntp_mode")
            return
        XmlChildCreator(top, "localTime", timeforxml)

        url_dsnm = self._urlgen("/ISAPI/System/time")
        try:
            response_dsnm = send_request("put", url_dsnm, data=ET.tostring(top, encoding="utf8", method="xml"),
                                         auth=self.auth, header=self.headers_xml)
            logging.info("NTP mode set up and timezone {}".format(timezone))
            return response_dsnm
        except:
            logging.warning("NTP mode didn't change")

    def device_video_conf_change(self, resolution="HD", bitrate_type="VBR", bitrate=2048):
        # Configure video settings
        bitrate = str(bitrate)

        if (resolution == "HD"):
            width = "1280"
            height = "720"
        elif (resolution == "FullHD"):
            width = "1920"
            height = "1080"
        else:
            logging.warning("You've entered wrong resolution in device_video_conf_change, should be HD or FullHD")
            return False

        # configure XML string
        top = ET.Element("StreamingChannel", {"version": "2.0", "xmlns": "http://www.std-cgi.com/ver20/XMLSchema"})
        XmlChildCreator(top, "id", "1")
        XmlChildCreator(top, "channelName", "Camera 01")
        XmlChildCreator(top, "enabled", "true")
        Video = XmlChildCreator(top, "Video")
        XmlChildCreator(Video, "enabled", "true")
        XmlChildCreator(Video, "videoInputChannelID", "1")
        XmlChildCreator(Video, "videoCodecType", "H.264")
        XmlChildCreator(Video, "videoScanType", "progressive")
        XmlChildCreator(Video, "videoScanType", "progressive")
        XmlChildCreator(Video, "videoResolutionWidth", width)
        XmlChildCreator(Video, "videoResolutionHeight", height)

        if bitrate_type == "CBR":
            XmlChildCreator(Video, "videoQualityControlType", "CBR")
        elif bitrate_type == "VBR":
            XmlChildCreator(Video, "videoQualityControlType", "VBR")
            XmlChildCreator(Video, "vbrUpperCap", bitrate)
            XmlChildCreator(Video, "vbrLowerCap", "32")
        else:
            logging.warning("You've entered wrong bitrate_type in device_video_conf_change, should be CBR or VBR")
            return False

        XmlChildCreator(Video, "fixedQuality", "60")
        XmlChildCreator(Video, "maxFrameRate", "2500")
        XmlChildCreator(Video, "keyFrameInterval", "6000")
        XmlChildCreator(Video, "snapShotImageType", "JPEG")
        XmlChildCreator(Video, "H264Profile", "Main")
        XmlChildCreator(Video, "GovLength", "150")
        XmlChildCreator(Video, "PacketType", "PS")
        XmlChildCreator(Video, "PacketType", "RTP")
        XmlChildCreator(Video, "smoothing", "50")

        url_dvc = self._urlgen("/ISAPI/Streaming/channels/1")
        try:
            response_dvc = send_request("put", url_dvc, data=ET.tostring(top, encoding="utf8", method="xml"),
                                        auth=self.auth, header=self.headers_xml)
            if response_dvc.status_code == 200:
                logging.info("video configuration changed successfully")
                return True
            else:
                logging.warning("Video configuration wasn't changed")
                return False
        except:
            logging.warning("Video configuration wasn't changed")
            return False

    def device_osd_turnoff(self):
        top = ET.Element("channelNameOverlay", {"version": "2.0", "xmlns": "http://www.std-cgi.com/ver20/XMLSchema"})
        XmlChildCreator(top, "enabled", "false")
        XmlChildCreator(top, "positionX", "512")
        XmlChildCreator(top, "positionY", "64")

        url_dot = self._urlgen("/ISAPI/System/Video/inputs/channels/1/overlays/channelNameOverlay")

        try:
            response_dot = send_request("put", url_dot, data=ET.tostring(top, encoding="utf8", method="xml"),
                                        auth=self.auth, header=self.headers_xml)
            logging.info("OSD turned off")
            return response_dot
        except:
            logging.warning("OSD didn't turned off")

    def device_upnp_turnoff(self):
        top = ET.Element("UPnP", {"version": "2.0", "xmlns": "http://www.std-cgi.com/ver20/XMLSchema"})
        XmlChildCreator(top, "enabled", "false")

        url_dut = self._urlgen("/ISAPI/System/Network/UPnP")
        try:
            send_request("put", url_dut, data=ET.tostring(top, encoding="utf8", method="xml"),
                         auth=self.auth, header=self.headers_xml)
            logging.info("UPNP was turned off")
        except:
            logging.warning("UPNP wasn't turned off")

    def device_cloud_turnoff(self):
        top = ET.Element("EZVIZ", {"version": "2.0", "xmlns": "http://www.std-cgi.com/ver20/XMLSchema"})
        XmlChildCreator(top, "enabled", "false")
        XmlChildCreator(top, "registerStatus", "false")
        XmlChildCreator(top, "redirect", "false")

        url_dct = self._urlgen("/ISAPI/System/Network/EZVIZ")
        try:
            send_request("put", url_dct, data=ET.tostring(top, encoding="utf8", method="xml"),
                         auth=self.auth, header=self.headers_xml)
            logging.info("Cloud was turned off")
        except:
            logging.warning("Cloud wasn't turned off")


if __name__ == '__main__':
    d = HikCamera('10.0.215.53', 'mW2PZxvh')
    d.device_video_conf_change("FullHD", "VBR", 2048)
