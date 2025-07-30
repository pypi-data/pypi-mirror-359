<div align="center">
  <a>
    <img src="https://github.com/user-attachments/assets/b5162036-5b17-4cf4-b0cb-8ec842a71bc6" width="200" alt="NB Logo">
  </a>
  <h1>NeteaseName</h1>
  <h3>网易昵称生成器！</h3>

  <p>
    <a href="https://www.python.org/">
      <img src="https://img.shields.io/badge/python->=3.10-blue?logo=python&style=flat-square" alt="Python Version">
    </a>
    <a href="https://nonebot.dev/">
      <img src="https://img.shields.io/badge/nonebot2->=2.4.2-blue?style=flat-square" alt="NoneBot Version">
    </a>
    <a href="LICENSE">
      <img src="https://img.shields.io/github/license/JohnRichard4096/nonebot_plugin_suggarchat?style=flat-square" alt="License">
    </a>
    <a href="https://qm.qq.com/q/PFcfb4296m">
      <img src="https://img.shields.io/badge/QQ%E7%BE%A4-1002495699-blue?style=flat-square" alt="QQ Group">
    </a>
  </p>
</div>

# 版权

* 本项目基于wangyupu的[NNG](https://github.com/wang-yupu/netease_mc_name_generator)

* 基于GPL v3.0协议进行开源。

# 快速开始

1. 安装依赖

  ```bash
  uv install nonebot_plugin_neteasename
  ```

2. 声明插件

  打开pyproject.toml文件，在[tool.nonebot]节点下添加如下内容：

  ```toml
  plugins = ["nonebot_plugin_neteasename"]
  ```

# 指令说明

```explaintext
/name
/网易昵称
```

获取随机生成的网易风格昵称

# 配置文件

我们使用`nonebot_plugin_localstore`管理存储，在插件配置目录下有个name_strus.json文件，里面是所有可能的昵称结构，你可以修改这个文件来修改昵称结构。
