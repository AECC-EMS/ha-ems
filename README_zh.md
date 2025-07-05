# HA-EMS Integration for Home Assistant

[English](./README.md) | [简体中文](./README_zh.md)
本指南将帮助你将 HA-EMS 插件集成到 HomeAssistant，并设置相应的自定义前端面板。

## 下载安装包
+ ✅ All in one  ZIP Package:  
[Download Here](https://cdn.shuoxd.com/Aecc/HA/aecc-ha.zip)

## 安装 `ha_ems_cloud`（云端插件）
## <font style="color:rgb(31, 35, 40);">安装前环境准备</font>
<font style="color:rgb(89, 99, 110);">已安装的Home Assistant 版本：</font>
+ <font style="color:rgb(89, 99, 110);">Core ≥ 2025.2.1</font>
+ <font style="color:rgb(89, 99, 110);">Operating System ≥ 13.0</font>
+ 

### 方法 3：通过[Samba](https://github.com/home-assistant/addons/tree/master/samba)<font style="color:rgb(31, 35, 40);"> </font><font style="color:rgb(31, 35, 40);">或</font><font style="color:rgb(31, 35, 40);"> </font>[<font style="color:rgb(9, 105, 218);">FTPS</font>](https://github.com/hassio-addons/addon-ftp)<font style="color:rgb(31, 35, 40);"> </font><font style="color:rgb(31, 35, 40);">手动安装</font>


将 `ha_ems_cloud.zip`解压后的文件夹，复制到 Home Assistant 的 `{homeassistant_work_dir}/config/custom_components` 文件夹下。</font>


## 配置
### 登录
[<font style="color:rgb(9, 105, 218);">设置 > 设备与服务 > 添加集成</font>](https://my.home-assistant.io/redirect/brand/?brand=xiaomi_home)<font style="color:rgb(31, 35, 40);"> > 搜索“</font>`HA-EMS CLOUD` > 下一步 > 请点击此处进行登录 > 使用AECC APP账号登录（如果没有AECC账号可以扫描下面二维码下载安装APP，注册账号和家庭）</font>


### 添加设备
登录成功后，会弹出会话框“选择家庭”。您可以选择需要添加的家庭，该家庭内的所有设备将导入 Home Assistant 。


## HA-EMS PANEL（可选）
> 如果你没有自定义页面的精力。我们提供了一个简易的页面，配置了基本的数据显示和开关功能。
```plain
{homeassistant_work_dir}/config
└── www/
   ├──  ha-ems-panel.mjs
```

### 安装步骤:
1. 复制文件夹内的 `ha-ems-panel.mjs`文件到<font style="color:rgb(31, 35, 40);">Home Assistant 的</font>:  
`config/www/`文件夹下。
2. 在 `configuration.yaml`中配置自定义页面:

```yaml
panel_custom:
  - name: ha-ems-panel
    sidebar_title: ems—panel #你的页面名
    sidebar_icon: mdi:chart-donut
    module_url: /local/ha-ems-panel.mjs
```
3. 保存配置文件并退出，重启Home Assistant.
4. 清除浏览器刷新缓存就可以看到页面了。
