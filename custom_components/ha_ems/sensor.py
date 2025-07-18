import asyncio
import logging
import re
from datetime import datetime

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from .hub import MyIntegrationHub
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def split_value_unit(s):
    """
    将类似 "239kwh"、"953w" 或纯数值（如 "123"）的字符串拆分为数值和单位
    :param s: 输入字符串
    :return: (数值, 单位)
    """
    # 正则表达式匹配数值部分（整数/小数）和可选的单位部分（非数字）
    pattern = r'^(-?\d+\.?\d*)(\D*)$'
    match = re.fullmatch(pattern, str(s))

    if not match:
        return s, None

    value = float(match.group(1))
    unit_part = match.group(2).strip()  # 去除单位部分的前后空白
    unit = unit_part if unit_part else ''  # 单位可能为空
    return value, unit


class AeccSensor(SensorEntity):
    """自定义传感器实体"""

    def __init__(self, hub: MyIntegrationHub, device, name, key, unit=None, field_name=None):
        super().__init__()
        self.device = device
        self.hub = hub
        self.pf = "sensor"
        self._key = key
        self.field_name = field_name
        self._name = name
        self._unique_id = self._generate_unique_id()
        #  使用unit  目前未开启 开启 self._unit = unit即可
        self._unit = unit
        self._state = None
        if name == 'plant_name':
            _LOGGER.debug(f"创建传感器实体: name{self._name}; unique_id: {self._unique_id}")
            _LOGGER.debug(f"创建传感器实体: hub.device_data{hub.device_data}; hub.plants: {hub.plants}")
            self._attributes = {
                "cur_plant": hub.senceId,
                "cur_ctl_device_sn": hub.cur_ctl_devices,
                "data": hub.total_data,
                "devices": hub.device_data,
                "plants": hub.plants,
            }
        self._attributes = {}
        _LOGGER.debug(f"创建传感器实体: {self.device}")
        # 注册到hub
        hub.add_entity(self)

    def _generate_unique_id(self):
        device_sn = re.sub(r"[^a-z0-9]", "", self.device.device_sn.lower())

        key = self._key.replace('_', ' ').lower()
        # _LOGGER.info(f"aecc_{device_sn}_{key}：：：：：{self._name}：：：{self._key}")
        return f"aecc_cloud_{device_sn}_{key}"

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return f"{self._name}"

    @property
    def native_value(self):
        return self._state

    @property
    def native_unit_of_measurement(self):
        if self._unit and self._unit == "":
            return self._unit
        return None

    @property
    def extra_state_attributes(self):
        return self._attributes

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.device.device_sn)},
            "name": self.device.device_sn,
            "model": self.device.icon_type,
            "manufacturer": "AECC",
        }

    def update_data(self, new_data, device_info, ai):
        # _LOGGER.debug(f"更新实体: {self._name}, hass={self.hass}")
        # 解析嵌套数据示例
        # _LOGGER.warning(new_data)
        v = new_data.get(self._key)
        # u = new_data.get(self._unit)
        # _LOGGER.warning(f"{self._key},{v}")

        if self._key == "aiSystemStatus":
            # _LOGGER.info(f"获取到AI模式数据: {ai}")
            if ai and ai['antiRefluxSet'] == 1:
                if ai['powerTimeSetVos']:
                    match ai['powerTimeSetVos'][0]['mode']:
                        case 0:
                            self._state = "peak"
                        case 1:
                            self._state = "trough"
                        case 2:
                            self._state = "negative electricity price"
                        case 3:
                            self._state = "intelligent linkage"
                        case 4:
                            self._state = "Guardian Mode"
                elif ai['powerMode'] == 1:
                    self._state = "zero feed"
                elif ai['powerMode'] == 0:
                    self._state = "intelligent linkage"
            else:
                self._state = "disable"
            self._unit = ""
        if self._key == "plant_name":
            # _LOGGER.info(f"获取到AI模式数据: {ai}")
            self._state = self.hass.data[DOMAIN]['cur_plant_name']
            self._unit = ""
        else:
            if v:
                _LOGGER.debug(f"未解析:{self._key}：{v}")
                yz = split_value_unit(v)
                _LOGGER.debug(f"解析后：{self._key},{yz}")

                # 分离处理单位和数值
                if yz[0]:
                    self._state = yz[0]
                if self._unit:
                    self._unit = yz[1]
                # 替换 总负载功率=负载功率+家庭功率+充电桩功率
                if self._key == "totalLoadPower":
                    self._state = split_value_unit(new_data.get("homePower"))[0] + \
                                  split_value_unit(new_data.get("loadPower"))[0] + \
                                  split_value_unit(new_data.get("chargerTotalPower"))[0]
                    self._unit = "W"
                if self._key == "batPower":
                    self._state = -(split_value_unit(new_data.get("batPower"))[0] * new_data.get("batWorkMode"))
                    self._unit = "W"
            elif v is None:
                for k, mp in device_info.items():
                    _LOGGER.debug(f"设备信息sn&key：{self._key},{k}")
                    if self._key.startswith(k):
                        _LOGGER.debug(f"设备信息更新：{self.field_name},{v}")
                        if self.field_name is None:
                            v = mp.get(self._name)
                        else:
                            v = mp.get(self.field_name)

                        if v:
                            yz = split_value_unit(v)
                            _LOGGER.debug(f"解析后：{self._key},{yz}")
                            # 分离处理单位和数值
                            if yz[0] is not None:
                                self._state = yz[0]
                                self._unit = yz[1]
                        elif self._key.endswith("as"):
                            self._state = self.device.device_name
                        break

            else:
                self._state = 0
        self.async_write_ha_state()
        if not hasattr(self, "hass") or self.hass is None:
            _LOGGER.debug("实体未完成初始化，跳过状态更新")
            return

        # _LOGGER.info(self.device)
        if self.device:
            attrs = {
                "deviceSn": self.device.device_sn,
                "iconType": self.device.icon_type,
                "dtc": self.device.device_code_type,
                "plantId": self.hub.senceId,
            }
        else:
            attrs = {
                "plantId": self.hub.senceId,
            }

        if self._key == "plant_name":
            self._attributes = {
                "cur_plant": self.hub.senceId,
                "cur_ctl_device_sn": self.hub.cur_ctl_devices,
                "last_updated": datetime.now().isoformat(),
                "data": self.hub.total_data,
                "devices": self.hub.device_data,
                "plants": self.hub.plants,
                "energy_data_year": self.hub.energy_data_year,
                "energy_data_total": self.hub.energy_data_total,
                "energy_data_month": self.hub.energy_data_month,
                "energy_data_day": self.hub.energy_data_day,
                "attrs": attrs,
            }
        else:
            self._attributes = {
                "last_updated": datetime.now().isoformat(),
                "attrs": attrs,
            }


async def async_setup_entry(hass, config_entry, async_add_entities):
    # _LOGGER.info(f"加载 sensor实体 开始：{hass.data[DOMAIN]['device_manager'].entities["sensor"]}")
    # 创建传感器实体
    sensors = hass.data[DOMAIN]['device_manager'].entities["sensor"]
    # 根据电站senceId 获取电站下所有设备
    async_add_entities(sensors)
    _LOGGER.info(f"加载 sensor实体 完成：{hass.data[DOMAIN]['device_manager'].entities["sensor"]}")
    return True
