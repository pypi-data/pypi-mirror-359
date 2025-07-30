from awException.aiwenException import AwException
# from awModel.aiwenModels import *
import requests
import operator
import awEnum.CoordSys
import awEnum.MultiFlag
import awEnum.SceneLang
import awEnum.StreetSubType
from awModel import aiwenKey
from awModel.aiwenModels import *


class Client(object):

    def __init__(self, *args):
        if len(args) == 1 :
            self.key = args[0]
        self.baseUrl = 'https://api.ipplus360.com/'
        self.url = ''
        self.param_data = {}

    def street(self, ip, *args):
        self.url = self.baseUrl + 'ip/geo/v1/street/'
        coordsys = ""
        area = "";
        urlStr = "";
        StreetSubTypeName = awEnum.StreetSubType.StreetSubType.__name__
        CoordSysClassName = awEnum.CoordSys.CoordSys.__name__
        MultiFlagClassName = awEnum.MultiFlag.MultiFlag.__name__
        AiwenKeyClassName = aiwenKey.__name__
        for param in args:
            if  StreetSubTypeName in str(param):
                urlStr = awEnum.StreetSubType.StreetSubType(param).name.lower()
            if  CoordSysClassName in str(param):
                coordsys = awEnum.CoordSys.CoordSys(param).name
            if  MultiFlagClassName in str(param):
                area = awEnum.MultiFlag.MultiFlag(param).name
            if AiwenKeyClassName in str(param):
                self.key = param.key
        self.param_data = {
            "key": self.key,
            "ip":ip,
            "coordsys": coordsys,
            "area": area
        }
        # return self.getResult()
        response = requests.get(self.url + urlStr + "/", self.param_data)
        response.close()
        if response.status_code != 200:
            raise AwException(response.json().get("msg"))
        response_obj = ResponseLocationStreetPSI(response.json())
        return response_obj


    # IPv4 归属地 高精准-公安版
    # def ipGeoV1StreetPsi(self, ip, *args):
    #     self.url = self.baseUrl + 'ip/geo/v1/street/psi/'
    #     coordsys = ""
    #     area = "";
    #     CoordSysClassName = awEnum.CoordSys.CoordSys.__name__
    #     MultiFlagClassName = awEnum.MultiFlag.MultiFlag.__name__
    #     AiwenKeyClassName = aiwenKey.__name__
    #     for param in args:
    #         if  CoordSysClassName in str(param):
    #             coordsys = awEnum.CoordSys.CoordSys(param).name
    #         if  MultiFlagClassName in str(param):
    #             area = awEnum.MultiFlag.MultiFlag(param).name
    #         if AiwenKeyClassName in str(param):
    #             self.key = param.key
    #     self.param_data = {
    #         "key": self.key,
    #         "ip":ip,
    #         "coordsys": coordsys,
    #         "area": area
    #     }
    #     # return self.getResult()
    #     response = requests.get(self.url, self.param_data)
    #     response.close()
    #     if response.status_code != 200:
    #         raise AwException(response.json().get("msg"))
    #     response_obj = ResponseLocationStreetPSI(response.json())
    #     return response_obj
    #
    # # IPv4 归属地 高精准-商业版
    # def ipGeoV1StreetBiz(self, ip, *args):
    #     self.url = self.baseUrl + 'ip/geo/v1/street/biz/'
    #     coordsys = ""
    #     area = "";
    #     CoordSysClassName = awEnum.CoordSys.CoordSys.__name__
    #     MultiFlagClassName = awEnum.MultiFlag.MultiFlag.__name__
    #     AiwenKeyClassName = aiwenKey.__name__
    #     for param in args:
    #         if CoordSysClassName in str(param):
    #             coordsys = awEnum.CoordSys.CoordSys(param).name
    #         if MultiFlagClassName in str(param):
    #             area = awEnum.MultiFlag.MultiFlag(param).name
    #         if AiwenKeyClassName in str(param):
    #             self.key = param.key
    #     self.param_data = {
    #         "key": self.key,
    #         "ip": ip,
    #         "coordsys": coordsys,
    #         "area": area
    #     }
    #     response = requests.get(self.url, self.param_data)
    #     response.close()
    #     if response.status_code != 200:
    #         raise AwException(response.json().get("msg"))
    #     response_obj = ResponseLocationStreetBIZ(response.json())
    #     return response_obj

    # IPv4 归属地 区县级
    def district(self, ip, *args):
        self.url = self.baseUrl + 'ip/geo/v1/district/'
        coordsys = ""
        CoordSysClassName = awEnum.CoordSys.CoordSys.__name__
        AiwenKeyClassName = aiwenKey.__name__
        for param in args:
            if CoordSysClassName in str(param):
                coordsys = awEnum.CoordSys.CoordSys(param).name
            if AiwenKeyClassName in str(param):
                self.key = param.key
        self.param_data = {
            "key": self.key,
            "ip": ip,
            "coordsys": coordsys
        }
        return self.getResult()

    # IPv4 归属地 城市级
    def city(self, ip, *args):
        self.url = self.baseUrl + 'ip/geo/v1/city/'
        coordsys = ""
        CoordSysClassName = awEnum.CoordSys.CoordSys.__name__
        AiwenKeyClassName = aiwenKey.__name__
        for param in args:
            if CoordSysClassName in str(param):
                coordsys = awEnum.CoordSys.CoordSys(param).name
            if AiwenKeyClassName in str(param):
                self.key = param.key
        self.param_data = {
            "key": self.key,
            "ip": ip,
            "coordsys": coordsys
        }
        return self.getResult()

    # IPv6 归属地 区县级
    def district6(self, ip, *args):
        self.url = self.baseUrl + 'ip/geo/v1/ipv6/district/'
        coordsys = ""
        CoordSysClassName = awEnum.CoordSys.CoordSys.__name__
        AiwenKeyClassName = aiwenKey.__name__
        for param in args:
            if CoordSysClassName in str(param):
                coordsys = awEnum.CoordSys.CoordSys(param).name
            if AiwenKeyClassName in str(param):
                self.key = param.key
        self.param_data = {
            "key": self.key,
            "ip": ip,
            "coordsys": coordsys
        }
        return self.getResult()

    # IPv6 归属地 城市级
    def city6(self, ip, *args):
        self.url = self.baseUrl + 'ip/geo/v1/ipv6/'
        coordsys = ""
        CoordSysClassName = awEnum.CoordSys.CoordSys.__name__
        AiwenKeyClassName = aiwenKey.__name__
        for param in args:
            if CoordSysClassName in str(param):
                coordsys = awEnum.CoordSys.CoordSys(param).name
            if AiwenKeyClassName in str(param):
                self.key = param.key
        self.param_data = {
            "key": self.key,
            "ip": ip,
            "coordsys": coordsys
        }
        return self.getResult()

    # as Whois
    def whoisAS(self, ip, *args):
        self.url = self.baseUrl + 'as/info/v1/asWhois/'
        AiwenKeyClassName = aiwenKey.__name__
        for param in args:
            if AiwenKeyClassName in str(param):
                self.key = param.key
        self.param_data = {
            "key": self.key,
            "ip": ip
        }
        response = requests.get(self.url, self.param_data)
        response.close()
        if response.status_code != 200:
            raise AwException(response.json().get("msg"))
        response_obj = ResponseASWhois(response.json())
        return response_obj
        # return self.getResult()

    # IP宿主信息
    def host(self, ip, *args):
        self.url = self.baseUrl + 'ip/geo/v1/host/'
        AiwenKeyClassName = aiwenKey.__name__
        for param in args:
            if AiwenKeyClassName in str(param):
                self.key = param.key
        self.param_data = {
            "key": self.key,
            "ip": ip
        }
        response = requests.get(self.url, self.param_data)
        response.close()
        if response.status_code != 200:
            raise AwException(response.json().get("msg"))
        response_obj = ResponseIPHost(response.json())
        return response_obj

    # ip行业
    def industry(self, ip, *args):
        self.url = self.baseUrl + 'ip/info/v1/industry/'
        AiwenKeyClassName = aiwenKey.__name__
        for param in args:
            if AiwenKeyClassName in str(param):
                self.key = param.key
        self.param_data = {
            "key": self.key,
            "ip": ip
        }
        response = requests.get(self.url, self.param_data)
        response.close()
        if response.status_code != 200:
            raise AwException(response.json().get("msg"))
        response_obj = ResponseIPIndustry(response.json())
        return response_obj

    # IPv6应用场景
    def scene6(self, ip, *args):
        self.url = self.baseUrl + 'ip/info/v1/ipv6Scene/'
        AiwenKeyClassName = aiwenKey.__name__
        for param in args:
            if AiwenKeyClassName in str(param):
                self.key = param.key
        self.param_data = {
            "key": self.key,
            "ip": ip
        }
        response = requests.get(self.url, self.param_data)
        response.close()
        if response.status_code != 200:
            raise AwException(response.json().get("msg"))
        response_obj = ResponseIPv6scene(response.json())
        return response_obj

    # IPv4应用场景
    def scene(self, ip, *args):
        self.url = self.baseUrl + 'ip/info/v1/scene/'
        lang = ""
        SceneLangClassName = awEnum.SceneLang.SceneLang.__name__
        AiwenKeyClassName = aiwenKey.__name__
        for param in args:
            if AiwenKeyClassName in str(param):
                self.key = param.key
            if SceneLangClassName in str(param):
                lang = awEnum.SceneLang.SceneLang(param).name
        self.param_data = {
            "key": self.key,
            "ip": ip,
            "lang": lang
        }
        response = requests.get(self.url, self.param_data)
        response.close()
        if response.status_code != 200:
            raise AwException(response.json().get("msg"))
        response_obj = ResponseIPv4scene(response.json())
        return response_obj

    # ip代理
    def proxy(self, ip, *args):
        self.url = self.baseUrl + 'ip/info/v1/ipProxy/'
        AiwenKeyClassName = aiwenKey.__name__
        for param in args:
            if AiwenKeyClassName in str(param):
                self.key = param.key
        self.param_data = {
            "key": self.key,
            "ip": ip
        }
        response = requests.get(self.url, self.param_data)
        response.close()
        if response.status_code != 200:
            raise AwException(response.json().get("msg"))
        response_obj = ResponseIPproxy(response.json())
        return response_obj

    # IP WHOIS
    def whois(self, ip, *args):
        self.url = self.baseUrl + 'ip/info/v1/ipWhois/'
        AiwenKeyClassName = aiwenKey.__name__
        for param in args:
            if AiwenKeyClassName in str(param):
                self.key = param.key
        self.param_data = {
            "key": self.key,
            "ip": ip
        }
        response = requests.get(self.url, self.param_data)
        response.close()
        if response.status_code != 200:
            raise AwException(response.json().get("msg"))
        response_obj = ResponseIPwhois(response.json())
        return response_obj

    def getResult(self):
        response = requests.get(self.url, self.param_data)
        response.close()
        if response.status_code != 200:
            raise AwException(response.json().get("msg"))
        response_obj = ResponseLocationStreet(response.json())
        return response_obj
