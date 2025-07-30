"""kid_protocol.py
=================
极简双工通信协议 V2

格式：DEVICE:VALUE 或 DEVICE1:VALUE1|DEVICE2:VALUE2
"""

class SimpleProtocol:
    """超简单协议处理器"""
    
    @staticmethod
    def encode(device, value):
        """编码单个设备消息"""
        return f"{device}:{value}\n"
    
    @staticmethod
    def encode_multi(**devices):
        """编码多个设备消息"""
        segments = [f"{dev}:{val}" for dev, val in devices.items()]
        return "|".join(segments) + "\n"
    
    @staticmethod
    def decode(line):
        """解码消息，返回设备字典"""
        line = line.strip()
        if not line:
            return {}
            
        result = {}
        segments = line.split("|")
        
        for seg in segments:
            if ":" in seg:
                device, value = seg.split(":", 1)
                result[device.upper()] = value
                
        return result
    
    @staticmethod
    def has_device(line, device):
        """快速检查是否包含指定设备"""
        return device.upper() in line.upper()
    
    @staticmethod
    def get_value(line, device):
        """快速获取设备值"""
        data = SimpleProtocol.decode(line)
        return data.get(device.upper())


# 兼容旧协议的快速转换
class LegacyProtocol:
    """旧协议兼容层"""
    
    @staticmethod
    def from_legacy(legacy_msg):
        """从旧格式转换到新格式"""
        # [VC:g:one|p:stand#123] -> GESTURE:one|POSE:stand
        if legacy_msg.startswith('[') and legacy_msg.endswith(']'):
            content = legacy_msg[1:-1]
            if '#' in content:
                content = content.split('#')[0]
                
            if content.startswith('VC:'):
                payload = content[3:]
                parts = payload.split('|')
                result = {}
                for part in parts:
                    if ':' in part:
                        key, val = part.split(':', 1)
                        if key == 'g':
                            result['GESTURE'] = val
                        elif key == 'p':
                            result['POSE'] = val
                return SimpleProtocol.encode_multi(**result)
                
        return legacy_msg


# 测试代码
if __name__ == "__main__":
    # 测试编码
    print("=== 编码测试 ===")
    print(repr(SimpleProtocol.encode("LED", "ON")))
    print(repr(SimpleProtocol.encode_multi(TEMP=25.4, HUMI=60, LIGHT=350)))
    
    # 测试解码
    print("\n=== 解码测试 ===")
    line1 = "LED:ON"
    line2 = "TEMP:25.4|HUMI:60|LIGHT:350|DIST:12.3"
    
    print(f"'{line1}' -> {SimpleProtocol.decode(line1)}")
    print(f"'{line2}' -> {SimpleProtocol.decode(line2)}")
    
    # 测试快速检查
    print("\n=== 快速检查测试 ===")
    print(f"LED in '{line1}': {SimpleProtocol.has_device(line1, 'LED')}")
    print(f"TEMP in '{line2}': {SimpleProtocol.has_device(line2, 'TEMP')}")
    print(f"LED value in '{line1}': {SimpleProtocol.get_value(line1, 'LED')}")
    print(f"TEMP value in '{line2}': {SimpleProtocol.get_value(line2, 'TEMP')}") 