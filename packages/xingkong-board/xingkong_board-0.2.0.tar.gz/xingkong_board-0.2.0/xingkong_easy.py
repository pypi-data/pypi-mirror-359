"""xingkong_easy.py
===================
20 行即可玩转行空板！支持手势识别、语音控制
运行: python xingkong_easy.py COM5  (缺省 COM5)
"""

import sys
from kid_duplex_controller import XingKongController

def main():
    # 1) 创建控制器实例 (启用离线语音识别)
    port = sys.argv[1] if len(sys.argv) > 1 else "COM5"
    controller = XingKongController(port=port, offline_speech=True)
    
    # 2) 手势控制：1指开灯，2指开风扇，5指全关
    @controller.when_gesture
    def handle_gesture(gesture, _):
        if gesture == "one":
            controller.send("LED", "ON")      # 👆 开灯
            print("👆 1指 -> 开灯")
        elif gesture == "two":
            controller.send("FAN", "ON")      # ✌️ 开风扇
            print("✌️ 2指 -> 开风扇")
        elif gesture == "five":
            controller.send_multi(LED="OFF", FAN="OFF")  # 🖐️ 全关
            print("🖐️ 5指 -> 全关")
    
    # 3) 语音控制：中文指令
    @controller.when_speech
    def handle_speech(text):
        if "开灯" in text:
            controller.send("LED", "ON")
            controller.send("TTS", "好的，已开灯")
            print(f"🎤 {text} -> 开灯")
        elif "关灯" in text:
            controller.send("LED", "OFF") 
            controller.send("TTS", "好的，已关灯")
            print(f"🎤 {text} -> 关灯")
        elif "开风扇" in text:
            controller.send("FAN", "ON")
            controller.send("TTS", "风扇已开启")
            print(f"🎤 {text} -> 开风扇")
        elif "关风扇" in text:
            controller.send("FAN", "OFF")
            controller.send("TTS", "风扇已关闭") 
            print(f"🎤 {text} -> 关风扇")
        elif "你好" in text:
            controller.send("TTS", "你好，我是行空机器人！")
            print(f"🎤 {text} -> 打招呼")
    
    # 4) 传感器自动控制
    @controller.when_sensor
    def handle_sensor(data):
        temp = data.get("temp", 0)
        if temp > 30:
            controller.send("FAN", "ON")
            print(f"🌡️ 温度{temp}°C -> 自动开风扇")
        elif temp < 18:
            controller.send("HEAT", "ON")
            print(f"🌡️ 温度{temp}°C -> 自动开加热")
    
    # 5) 启动！
    print("=== 行空板简易控制 ===")
    print("👋 手势: 1指开灯, 2指开风扇, 5指全关")
    print("🎤 语音: '开灯', '关灯', '开风扇', '关风扇', '你好'") 
    print("🌡️ 传感器: 自动温控")
    print("按 Ctrl+C 退出\n")
    
    controller.start()
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\n程序已停止")

if __name__ == "__main__":
    main() 