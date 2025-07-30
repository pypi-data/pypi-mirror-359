# 儿童机器人通信协议规范

## 概述

本协议设计用于PC端与儿童机器人硬件设备之间的双向数据通信，支持视觉识别、语音识别、传感器数据、状态监控等功能的数据交换。

## 协议格式

### 基础格式
```
[类型:内容#校验]\n
```

- **类型**: 2字符消息类型标识
- **内容**: 数据内容，多个字段用`|`分隔，每个字段格式为`key:value`
- **校验**: 简单累加校验值（内容字符ASCII码累加取模256）
- **结束**: 换行符`\n`

### 示例
```
[VC:g:three|p:stand#131]
[SN:temp:25.6|humi:60.2|light:800|dist:15.3#251]
```

## 消息类型定义

### PC → 设备端

| 类型 | 名称 | 格式 | 说明 |
|------|------|------|------|
| VC | 视觉识别结果 | `[VC:g:{手势}|p:{姿态}#{校验}]` | 发送手势和姿态识别结果 |
| SP | 语音识别结果 | `[SP:text:{文本}#{校验}]` | 发送语音转文字结果 |
| CM | 控制命令 | `[CM:cmd:{命令}|param:{参数}#{校验}]` | 发送控制指令 |

### 设备端 → PC

| 类型 | 名称 | 格式 | 说明 |
|------|------|------|------|
| SN | 传感器数据 | `[SN:temp:{温度}|humi:{湿度}|light:{光照}|dist:{距离}#{校验}]` | 发送传感器读数 |
| ST | 状态信息 | `[ST:bat:{电池}|mode:{模式}|err:{错误}#{校验}]` | 发送设备状态 |
| HB | 心跳包 | `[HB:ts:{时间戳}#{校验}]` | 设备在线检测 |

## 详细说明

### 1. 视觉识别结果 (VC)

**用途**: PC端将摄像头识别的手势和姿态发送给设备

**格式**: `[VC:g:{gesture}|p:{pose}#{checksum}]`

**字段说明**:
- `g`: 手势识别结果 (zero/one/two/three/four/five/none)
- `p`: 姿态识别结果 (stand/left_hand_up/right_hand_up/both_hands_up/none)

**示例**:
```
[VC:g:three|p:stand#131]
[VC:g:none|p:both_hands_up#156]
```

### 2. 语音识别结果 (SP)

**用途**: PC端将语音识别的文字结果发送给设备

**格式**: `[SP:text:{text}#{checksum}]`

**字段说明**:
- `text`: 语音转换的文字内容

**示例**:
```
[SP:text:你好机器人#202]
[SP:text:向前走#168]
```

### 3. 控制命令 (CM)

**用途**: PC端向设备发送控制指令

**格式**: `[CM:cmd:{command}|param:{parameter}#{checksum}]`

**字段说明**:
- `cmd`: 命令类型 (status/move/speak/led等)
- `param`: 命令参数

**示例**:
```
[CM:cmd:move|param:forward#185]
[CM:cmd:led|param:red#142]
[CM:cmd:status|param:check#178]
```

### 4. 传感器数据 (SN)

**用途**: 设备端向PC发送传感器数据

**格式**: `[SN:temp:{温度}|humi:{湿度}|light:{光照}|dist:{距离}#{checksum}]`

**字段说明**:
- `temp`: 温度值 (°C, 保留1位小数)
- `humi`: 湿度值 (%, 保留1位小数)
- `light`: 光照强度 (0-1023)
- `dist`: 距离值 (cm, 保留1位小数)

**示例**:
```
[SN:temp:25.6|humi:60.2|light:800|dist:15.3#251]
[SN:temp:23.1|humi:55.8|light:650|dist:22.7#223]
```

### 5. 状态信息 (ST)

**用途**: 设备端向PC发送设备状态

**格式**: `[ST:bat:{电池}|mode:{模式}|err:{错误}#{checksum}]`

**字段说明**:
- `bat`: 电池电量 (0-100%)
- `mode`: 工作模式 (auto/manual/sleep/等)
- `err`: 错误信息 (none表示无错误)

**示例**:
```
[ST:bat:85|mode:auto|err:none#168]
[ST:bat:20|mode:sleep|err:low_battery#201]
```

### 6. 心跳包 (HB)

**用途**: 设备端定期发送，用于连接状态检测

**格式**: `[HB:ts:{timestamp}#{checksum}]`

**字段说明**:
- `ts`: Unix时间戳

**示例**:
```
[HB:ts:1704067200#89]
[HB:ts:1704067205#94]
```

## 校验机制

使用简单累加校验：
1. 对"类型:内容"部分的每个字符求ASCII码
2. 累加所有ASCII码值
3. 对256取模得到校验值

```python
def calculate_checksum(data: str) -> str:
    return str(sum(ord(c) for c in data) % 256)

# 示例
content = "VC:g:three|p:stand"
checksum = str(sum(ord(c) for c in content) % 256)  # = "131"
```

## 通信流程

### 正常工作流程

1. **设备启动**: 设备发送状态信息和首次心跳
2. **周期性数据**: 设备每2秒发送传感器数据，每5秒发送心跳
3. **PC响应**: PC接收数据并定期发送视觉/语音识别结果
4. **命令控制**: PC根据需要发送控制命令
5. **状态监控**: 通过心跳包监控设备在线状态

### 错误处理

1. **校验失败**: 忽略错误消息，等待重传
2. **格式错误**: 记录错误日志，继续处理其他消息
3. **超时检测**: 超过10秒未收到心跳则认为设备离线
4. **重连机制**: 设备离线后自动尝试重新连接

## 实现示例

### Python实现

参考项目中的`kid_protocol.py`文件，提供了完整的协议编解码实现。

### 使用方法

```python
from kid_protocol import KidProtocol
from kid_serial import SerialIO

# 初始化
serial = SerialIO("COM5")
protocol = KidProtocol(serial)

# 发送视觉识别结果
protocol.send_vision_result("three", "stand")

# 接收消息
message = protocol.receive_message()
if message and message.msg_type == "SN":
    sensor_data = protocol._decode_sensor(message.content)
    print(f"温度: {sensor_data['temperature']}°C")
```

## 扩展性

协议支持方便的扩展：
1. **新消息类型**: 添加2字符类型标识和对应处理函数
2. **新字段**: 在现有消息中添加新的key:value字段
3. **版本兼容**: 可通过消息类型或字段来实现版本控制

## 性能特点

- **紧凑**: 协议开销小，数据传输效率高
- **可读**: 文本格式，便于调试和监控
- **可靠**: 包含校验机制，保证数据完整性
- **灵活**: 支持不同类型数据的统一传输 