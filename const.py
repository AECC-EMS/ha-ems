DOMAIN = "ha_ems_cloud"
BASE_URL = "https://monitor.ai-ec.cloud:8443"
LOGGER_NAME = "custom_components.ha_ems"

DEVICE_TYPE_MAP = [
    (1, 49, "inverter.py/storage"),
    (50, 54, "meter"),
    (55, 79, "charg"),
    (80, 109, "battery"),
    (110, 139, "splug"),
    (141, 145, "ac coupler"),
    (150, 155, "sboost"),
    (156, 160, "relay"),
]
def get_device_type_name(device_type: int) -> str:
    for start, end, name in DEVICE_TYPE_MAP:
        if start <= device_type <= end:
            return name
    return "device"

PRIORITY_STRATEGY = {
    'local_available': 10,    # 本地可用时优先级最高
    'cloud_fallback': 5,      # 云端备用
    'disabled': 0             # 禁用状态
}