import geoip2.database
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def get_location(ip_address):
    """根据 IP 地址获取地理位置信息"""
    location = 'unknown'
    if ip_address not in ['unknown', '127.0.0.1']:
        try:
            with geoip2.database.Reader(settings.GEOIP_PATH) as reader:
                response = reader.city(ip_address)
                city = response.city.name or 'unknown'
                region = response.subdivisions.most_specific.name or 'unknown'
                country = response.country.name or 'unknown'
                location = f"{country}, {region}, {city}"
        except geoip2.errors.AddressNotFoundError:
            logger.warning(f"IP {ip_address} 未找到位置信息")
        except Exception as e:
            logger.error(f"GeoIP 查询失败: {e}")
    return location