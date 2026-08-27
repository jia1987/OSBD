# 部署资源与要点

## 串口驱动
CP210x USB-UART 驱动（光源控制器/计米轮/放电检测用的 Pico 板）:
https://www.silabs.com/software-and-tools/usb-to-uart-bridge-vcp-drivers?tab=downloads

## IO 卡 (WENYU_EIO16P)
- DLL: `WENYU_EIO16P.dll`, 必须位于工作目录 `_rc/` 下。
- 卡只有 **8 路物理输出 (ch0~ch7)**:
  - ch0~ch3: 光源频闪触发
  - ch4 (默认): 声光报警输出, 可在 `config/config.json` 的
    `IOCard.WarningChannel` 中按实际接线调整
  - ch0: 放电检测中断输入
- 没有 IO 卡时程序可正常启动, 光源触发/放电输入/报警输出功能降级不可用。

## 相机
- 海康 MVS 客户端与运行库 (MVS_Win_STD_*.zip), 相机通过 USB3 连接。
- 无相机时可在 设置→摄像头 中把读取模式改为「图片」或「视频」做演示。

## 授权
- `config/pub_key` + `config/license` 存在时启用机器码授权校验,
  缺失时程序以提示方式跳过校验(开发/验收环境)。

## 目录
- `yolo.onnx`: 缺陷检测 YOLO 模型 (非 Intel 平台)
- `yolo_openvino_model/`: OpenVINO IR 模型 (Intel 平台)
- `icon/`: 界面图标
