DOMAIN="ha_ems_local"
LOGGER_NAME = "custom_components.ha_ems_local"

DEVICE_TYPE_MAP = [
    (1, 49, "inverter/storage"),
    (50, 54, "meter"),
    (55, 79, "charger"),
    (80, 109, "battery"),
    (110, 139, "plug"),
    (141, 145, "ac coupler"),
    (150, 155, "heater"),
    (156, 160, "relay"),
]
def get_device_type_name(device_type: int) -> str:
    for start, end, name in DEVICE_TYPE_MAP:
        if start <= device_type <= end:
            return name
    return "device"