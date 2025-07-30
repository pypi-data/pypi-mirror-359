class Base():
    def __init__(self, dict_data):
        self.raw_data = dict_data
        self.continent = dict_data.get("continent", "")
        self.country = dict_data.get("country", "")
        self.owner = dict_data.get("owner", "")
        self.isp = dict_data.get("isp", "")
        self.zipcode = dict_data.get("zipcode", "")
        self.timezone = dict_data.get("timezone", "")
        self.accuracy = dict_data.get("accuracy", "")
        self.source = dict_data.get("source", "")
        self.areacode = dict_data.get("areacode", "")
        self.asnumber = dict_data.get("asnumber", "")

    def to_dict(self):
        return {
            "continent": self.continent,
            "country": self.country,
            "owner": self.owner,
            "isp": self.isp,
            "zipcode": self.zipcode,
            "timezone": self.timezone,
            "accuracy": self.accuracy,
            "source": self.source,
            "areacode": self.areacode,
            "asnumber": self.asnumber
        }

class BaseSingleArea(Base):
    def __init__(self, dict_data):
        super().__init__(dict_data)
        self.lat = dict_data.get("lat", "")
        self.lng = dict_data.get("lng", "")
        self.radius = dict_data.get("radius", "")
        self.prov = dict_data.get("prov", "")
        self.city = dict_data.get("city", "")

    def to_dict(self):
        return {
            "continent": self.continent,
            "country": self.country,
            "owner": self.owner,
            "isp": self.isp,
            "zipcode": self.zipcode,
            "timezone": self.timezone,
            "accuracy": self.accuracy,
            "source": self.source,
            "areacode": self.areacode,
            "asnumber": self.asnumber,
            "lat": self.lat,
            "lng": self.lng,
            "radius": self.radius,
            "prov": self.prov,
            "city": self.city
        }

class Area():
    def __init__(self, address, lat, lng, radius, prov, city, district):
        self.address = address
        self.lat = lat
        self.lng = lng
        self.radius = radius
        self.prov = prov
        self.city = city
        self.district = district
    
    def to_dict(self):
        return {
            "address": self.address,
            "lat": self.lat,
            "lng": self.lng,
            "radius": self.radius,
            "prov": self.prov,
            "city": self.city,
            "district": self.district
        }

class BaseMultiArea(Base):
    def __init__(self, dict_data):
        super().__init__(dict_data)
        self.multiAreas = []
        for area in dict_data.get("multiAreas", []):
            self.multiAreas.append(Area(area.get("address", ""),
                                        area.get("lat", ""),
                                        area.get("lng", ""),
                                        area.get("radius", ""),
                                        area.get("prov", ""),
                                        area.get("city", ""),
                                        area.get("district", "")).to_dict()
                                        )

class City(BaseSingleArea):
    def __init__(self, dict_data):
        super().__init__(dict_data)
    



class CityV6(BaseSingleArea):
    def __init__(self, dict_data):
        super().__init__(dict_data)
        # patch it, coverage
        self.prov = dict_data.get("province", "")

class District(City):
    def __init__(self, dict_data):
        super().__init__(dict_data)
        self.district = dict_data.get("district", "")
    
    def to_dict(self):
        return {
            "continent": self.continent,
            "country": self.country,
            "owner": self.owner,
            "isp": self.isp,
            "zipcode": self.zipcode,
            "timezone": self.timezone,
            "accuracy": self.accuracy,
            "source": self.source,
            "areacode": self.areacode,
            "asnumber": self.asnumber,
            "lat": self.lat,
            "lng": self.lng,
            "radius": self.radius,
            "prov": self.prov,
            "city": self.city,
            "district": self.district
        }

class DistrictV6(District):
    def __init__(self, dict_data):
        super().__init__(dict_data)
        self.currency_code = dict_data.get("currency_code", "")
        self.currency_name = dict_data.get("currency_name", "")

class Street(BaseMultiArea):
    def __init__(self, dict_data):
        super().__init__(dict_data)
        self.consistency = dict_data.get("consistency", "")
        self.correctness = dict_data.get("correctness", "")

    def to_dict(self):
        return {
            "continent": self.continent,
            "country": self.country,
            "owner": self.owner,
            "isp": self.isp,
            "zipcode": self.zipcode,
            "timezone": self.timezone,
            "accuracy": self.accuracy,
            "source": self.source,
            "areacode": self.areacode,
            "asnumber": self.asnumber,
            "multiAreas": [area.to_dict() for area in self.multiAreas],
            "consistency": self.consistency,
            "correctness": self.correctness
        }

class ResponseBase():
    def __init__(self, dict_data):
        self.code = dict_data.get("code")
        self.msg = dict_data.get("msg")
        self.data = dict_data.get("data")
        self.charge = dict_data.get("charge")
    
    def to_dict(self):
        return {
            "code": self.code,
            "msg": self.msg,
            "data": self.data,
            "charge": self.charge
        }

class ResponseLocation(ResponseBase):
    def __init__(self, dict_data):
        super().__init__(dict_data)
        self.ip = dict_data.get("ip")
        self.coordsys = dict_data.get("coordsys")
        self.area = dict_data.get("area")

    def to_dict(self):
        return {
            "code": self.code,
            "msg": self.msg,
            "data": self.data,
            "charge": self.charge,
            "ip": self.ip,
            "coordsys": self.coordsys,
            "area": self.area
        }

class ResponseLocationStreet(ResponseLocation):
    def __init__(self, dict_data):
        self.code = dict_data.get("code")
        self.msg = dict_data.get("msg")
        self.charge = dict_data.get("charge")
        self.area = dict_data.get("area")
        self.data = dict_data.get("data")
        if self.code == 'Success':
            self.data = Street(dict_data.get("data"))

    def to_dict(self):
        return {
            "code": self.code,
            "msg": self.msg,
            "charge": self.charge,
            "area": self.area,
            "data": self.data.to_dict()
        }

class ResponseASWhois(ResponseLocation):
    def __init__(self, dict_data):
        self.statuscode = dict_data.get("statuscode")
        self.ip = dict_data.get("ip")
        self.charge = dict_data.get("charge")
        self.statusdesc = dict_data.get("statusdesc")
        self.data = dict_data.get("data")
        if self.code == 'Success':
            self.data = ASWhois(dict_data.get("data"))
            # self.data.techinfo = ASWhoisTeachinfo(dict_data.get("data").get("techinfo"))
            # self.data.admininfo = ASWhoisTeachinfo(dict_data.get("data").get("admininfo"))
    def to_dict(self):
        return {
            "code": self.code,
            "msg": self.msg,
            "charge": self.charge,
            "statuscode": self.statuscode,
            "statusdesc": self.statusdesc,
            "data": self.data.to_dict()
        }

class ASWhois():
    def __init__(self, dict_data):
        self.range = dict_data.get("range", "")
        self.asn = dict_data.get("asn", "")
        self.asname = dict_data.get("asname", "")
        self.isp = dict_data.get("isp", "")
        self.areacode = dict_data.get("areacode", "")
        self.allocated = dict_data.get("allocated", "")
        self.type = dict_data.get("type", "")
        self.industry = dict_data.get("industry", "")
        self.techinfo = teachinfo(dict_data.get("techinfo", ""))
        self.admininfo = admininfo(dict_data.get("admininfo", ""))

    def to_dict(self):
        return {
            "range": self.range,
            "asn": self.asn,
            "asname": self.asname,
            "isp": self.isp,
            "areacode": self.areacode,
            "allocated": self.allocated,
            "type": self.type,
            "industry": self.industry,
            "techinfo": self.techinfo.to_dict(),
            "admininfo": self.admininfo.to_dict()
        }
    
class teachinfo():
    def __init__(self, dict_data):
        self.id = dict_data.get("id", "")
        self.name = dict_data.get("name", "")
        self.email = dict_data.get("email", "")
        self.address = dict_data.get("address", "")
        self.areacode = dict_data.get("areacode", "")
        self.phone = dict_data.get("phone", "")
        self.fax = dict_data.get("fax", "")
        self.update = dict_data.get("update", "")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "address": self.address,
            "areacode": self.areacode,
            "phone": self.phone,
            "fax": self.fax,
            "update": self.update
        }

class admininfo():
    def __init__(self, dict_data):
        self.id = dict_data.get("id", "")
        self.name = dict_data.get("name", "")
        self.email = dict_data.get("email", "")
        self.address = dict_data.get("address", "")
        self.areacode = dict_data.get("areacode", "")
        self.phone = dict_data.get("phone", "")
        self.fax = dict_data.get("fax", "")
        self.update = dict_data.get("update", "")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "address": self.address,
            "areacode": self.areacode,
            "phone": self.phone,
            "fax": self.fax,
            "update": self.update
        } 

class ResponseIPHost():
    def __init__(self, dict_data):
        self.code = dict_data.get("code")
        self.ip = dict_data.get("ip")
        self.charge = dict_data.get("charge")
        self.msg = dict_data.get("msg")
        self.data = dict_data.get("data")
        if self.code == 'Success':
            self.data = IPHost(dict_data.get("data"))

    def to_dict(self):
        return {
            "code": self.code,
            "ip": self.ip,
            "charge": self.charge,
            "msg": self.msg,
            "data": self.data
        }

class IPHost():
    def __init__(self, dict_data):
        self.owner = dict_data.get("owner", "")
        self.asInfo = []
        for dto in dict_data.get("asInfo", []):
            self.asInfo.append(AsInfo(dto.get("asname", ""),
                                        dto.get("asnumber", ""),
                                        dto.get("isp", "")).to_dict())
            
    def to_dict(self):
        return {
            "owner": self.owner,
            "asInfo": self.asInfo
        }

class AsInfo():
    def __init__(self, asname, asnumber, isp):
        self.asname = asname
        self.asnumber = asnumber
        self.isp = isp
    
    def to_dict(self):
        return {
            "asname": self.asname,
            "asnumber": self.asnumber,
            "isp": self.isp
        }

class asInfo():
    def __init__(self, dict_data):
        for data in dict_data:
            self.asname = data.get("asname", "")
            self.asnumber = data.get("asnumber", "")
            self.isp = data.get("isp", "")
    
    def to_dict(self):
        return {
            "asname": self.asname,
            "asnumber": self.asnumber,
            "isp": self.isp
        }

class ResponseIPIndustry():
    def __init__(self, dict_data):
        self.status_code = dict_data.get("status_code")
        self.ip = dict_data.get("ip")
        self.charge = dict_data.get("charge")
        self.status_desc = dict_data.get("status_desc")
        self.data = dict_data.get("data")
        if self.status_code == 'Success':
            self.data = industry(dict_data.get("data"))

    def to_dict(self):
        return {
            "status_code": self.status_code,
            "ip": self.ip,
            "charge": self.charge,
            "status_desc": self.status_desc,
            "data": self.data
        }

class industry():
    def __init__(self, dict_data):
        self.industry = dict_data.get("industry", "")
    
    def to_dict(self):
        return {
            "industry": self.industry
        }



class ResponseIPv6scene():
    def __init__(self, dict_data):
        self.status_code = dict_data.get("status_code")
        self.ip = dict_data.get("ip")
        self.charge = dict_data.get("charge")
        self.status_desc = dict_data.get("status_desc")
        self.data = dict_data.get("data")
        if self.status_code == 'Success':
            self.data = scene(dict_data.get("data"))

    def to_dict(self):
        return {
            "status_code": self.status_code,
            "ip": self.ip,
            "charge": self.charge,
            "status_desc": self.status_desc,
            "data": self.data
        }

class ResponseIPv4scene():
    def __init__(self, dict_data):
        self.code = dict_data.get("code")
        self.ip = dict_data.get("ip")
        self.charge = dict_data.get("charge")
        self.msg = dict_data.get("msg")
        self.data = dict_data.get("data")
        if self.code == 'Success':
            self.data = scene(dict_data.get("data"))
        
    def to_dict(self):
        return {
            "code": self.code,
            "ip": self.ip,
            "charge": self.charge,
            "msg": self.msg,
            "data": self.data
        }

class scene():
    def __init__(self, dict_data):
        self.scene = dict_data.get("scene", "")

    def to_dict(self):
        return {
            "scene": self.scene
        }

class ResponseIPproxy():
    def __init__(self, dict_data):
        self.status_code = dict_data.get("status_code")
        self.ip = dict_data.get("ip")
        self.charge = dict_data.get("charge")
        self.status_desc = dict_data.get("status_desc")
        self.data = dict_data.get("data")
        if self.status_code == 'Success':
            self.data = ipproxy(dict_data.get("data"))

class ipproxy():
    def __init__(self, dict_data):
        self.proxy = dict_data.get("proxy", "")
        self.vpn = dict_data.get("vpn", "")
        self.tor = dict_data.get("tor", "")

class ResponseIPwhois():
    def __init__(self, dict_data):
        self.statuscode = dict_data.get("statuscode")
        self.ip = dict_data.get("ip")
        self.charge = dict_data.get("charge")
        self.statusdesc = dict_data.get("statusdesc")
        self.data = dict_data.get("data")
        if self.statuscode == 'Success':
            self.data = ipwhois(dict_data.get("data"))
    
    def to_dict(self):
        return {
            "statuscode": self.statuscode,
            "ip": self.ip,
            "charge": self.charge,
            "statusdesc": self.statusdesc,
            "data": self.data
        }

class ipwhois():
    def __init__(self, dict_data):
        self.range = dict_data.get("range", "")
        self.netname = dict_data.get("netname", "")
        self.areacode = dict_data.get("areacode", "")
        self.status = dict_data.get("status", "")
        self.owner = dict_data.get("owner", "")
        self.techinfo = teachinfo(dict_data.get("techinfo", ""))
        self.admininfo = admininfo(dict_data.get("admininfo", ""))

    def to_dict(self):
        return {
            "range": self.range,
            "netname": self.netname,
            "areacode": self.areacode,
            "status": self.status,
            "owner": self.owner,
            "techinfo": self.techinfo.to_dict(),
            "admininfo": self.admininfo.to_dict()
        }

class ResponseLocationStreetPSI():
    def __init__(self, dict_data):
        self.code = dict_data.get("code")
        self.msg = dict_data.get("msg")
        self.ip = dict_data.get("ip")
        self.charge = dict_data.get("charge")
        self.area = dict_data.get("area")
        self.coordsys = dict_data.get("coordsys")
        self.data = dict_data.get("data")
        if self.code == 'Success' :
            self.data = streetPSI(dict_data.get("data"))

    def to_dict(self):
        return {
            "code": self.code,
            "msg": self.msg,
            "ip": self.ip,
            "charge": self.charge,
            "area": self.area,
            "coordsys": self.coordsys,
            "data": self.data
        }

class streetPSI():
    def __init__(self, dict_data):
        self.continent = dict_data.get("continent", "")
        self.country = dict_data.get("country", "")
        self.consistency = dict_data.get("consistency", "")
        self.correctness = dict_data.get("correctness", "")
        self.owner = dict_data.get("owner", "")
        self.isp = dict_data.get("isp", "")
        self.zipcode = dict_data.get("zipcode", "")
        self.timezone = dict_data.get("timezone", "")
        self.accuracy = dict_data.get("accuracy", "")
        self.source = dict_data.get("source", "")
        self.areacode = dict_data.get("areacode", "")
        self.asnumber = dict_data.get("asnumber", "")
        self.multiAreas = []
        for area in dict_data.get("multiAreas", []):
            self.multiAreas.append(Area(area.get("address", ""),
                                        area.get("lat", ""),
                                        area.get("lng", ""),
                                        area.get("radius", ""),
                                        area.get("prov", ""),
                                        area.get("city", ""),
                                        area.get("district", "")).to_dict())
        
    def to_dict(self):
        return {
            "continent": self.continent,
            "country": self.country,
            "consistency": self.consistency,
            "correctness": self.correctness,
            "owner": self.owner,
            "isp": self.isp,
            "zipcode": self.zipcode,
            "timezone": self.timezone,
            "accuracy": self.accuracy,
            "source": self.source,
            "areacode": self.areacode,
            "asnumber": self.asnumber,
            "multiAreas": self.multiAreas
        }

class ResponseLocationStreetBIZ():
    def __init__(self, dict_data):
        self.code = dict_data.get("code")
        self.msg = dict_data.get("msg")
        self.ip = dict_data.get("ip")
        self.charge = dict_data.get("charge")
        self.area = dict_data.get("area")
        self.coordsys = dict_data.get("coordsys")
        self.data = dict_data.get("data")
        if self.code == 'Success' :
            self.data = streetBIZ(dict_data.get("data"))

    def to_dict(self):
        return {
            "code": self.code,
            "msg": self.msg,
            "ip": self.ip,
            "charge": self.charge,
            "area": self.area,
            "coordsys": self.coordsys,
            "data": self.data
        }


class streetBIZ():
    def __init__(self, dict_data):
        self.continent = dict_data.get("continent", "")
        self.country = dict_data.get("country", "")
        self.consistency = dict_data.get("consistency", "")
        self.correctness = dict_data.get("correctness", "")
        self.owner = dict_data.get("owner", "")
        self.isp = dict_data.get("isp", "")
        self.zipcode = dict_data.get("zipcode", "")
        self.timezone = dict_data.get("timezone", "")
        self.accuracy = dict_data.get("accuracy", "")
        self.source = dict_data.get("source", "")
        self.areacode = dict_data.get("areacode", "")
        self.asnumber = dict_data.get("asnumber", "")
        self.multiAreas = []
        for area in dict_data.get("multiAreas", []):
            self.multiAreas.append(Area(area.get("address", ""),
                                        area.get("lat", ""),
                                        area.get("lng", ""),
                                        area.get("radius", ""),
                                        area.get("prov", ""),
                                        area.get("city", ""),
                                        area.get("district", "")).to_dict())
            
    def to_dict(self):
        return {
            "continent": self.continent,
            "country": self.country,
            "consistency": self.consistency,
            "correctness": self.correctness,
            "owner": self.owner,
            "isp": self.isp,
            "zipcode": self.zipcode,
            "timezone": self.timezone,
            "accuracy": self.accuracy,
            "source": self.source,
            "areacode": self.areacode,
            "asnumber": self.asnumber,
            "multiAreas": self.multiAreas
        }
