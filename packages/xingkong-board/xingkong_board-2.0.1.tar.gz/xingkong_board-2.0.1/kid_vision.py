"""kid_vision.py
=================
基于 MediaPipe 为儿童准备的视觉识别：
1. 手势 0~5 指
2. 姿态：stand / left_hand_up / right_hand_up / both_hands_up

依赖：
    pip install mediapipe opencv-python
"""

from __future__ import annotations

import cv2
import mediapipe as mp
from dataclasses import dataclass
from typing import Dict, Tuple, Optional


@dataclass
class VisionResult:
    gesture: Optional[str] = None
    pose: Optional[str] = None

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {"gesture": self.gesture, "pose": self.pose}


class KidVision:
    """手势 + 姿态识别，可按需启用。

    Args:
        enable_gesture: 是否启用手势识别（默认 True）
        enable_pose:    是否启用姿态识别（默认 False）
        model_complexity: 模型复杂度 0-2 (默认 0，最快)
        draw_landmarks: 是否绘制特征点（默认 False，性能优先）
        draw_connections: 是否绘制连接线（默认 False）
        landmark_style: 特征点样式配置（原生 MediaPipe 样式）
        connection_style: 连接线样式配置（原生 MediaPipe 样式）
    """

    def __init__(self, *, 
                 enable_gesture: bool = True, 
                 enable_pose: bool = False,
                 model_complexity: int = 0, 
                 draw_landmarks: bool = False,
                 draw_connections: bool = False,
                 landmark_style: Optional[dict] = None,
                 connection_style: Optional[dict] = None):
        
        self.enable_gesture = enable_gesture
        self.enable_pose = enable_pose
        self.draw_landmarks = draw_landmarks
        self.draw_connections = draw_connections
        
        # MediaPipe 原生绘制样式
        self.landmark_style = landmark_style or mp.solutions.drawing_styles.get_default_hand_landmarks_style()
        self.connection_style = connection_style or mp.solutions.drawing_styles.get_default_hand_connections_style()

        self.mp_hands = mp.solutions.hands if enable_gesture else None
        self.mp_pose = mp.solutions.pose if enable_pose else None

        # 只初始化被启用的模型以节省资源
        self.hands = None
        if enable_gesture and self.mp_hands:
            self.hands = self.mp_hands.Hands(
                static_image_mode=False, 
                max_num_hands=1,
                model_complexity=model_complexity,
                min_detection_confidence=0.3,   # 降低检测精度要求
                min_tracking_confidence=0.3     # 降低跟踪精度要求
            )

        self.pose = None
        if enable_pose and self.mp_pose:
            self.pose = self.mp_pose.Pose(
                model_complexity=model_complexity,
                min_detection_confidence=0.5, 
                min_tracking_confidence=0.5
            )

        self.drawer = mp.solutions.drawing_utils

    # ------------------ 公共 ------------------
    def run(self):
        """运行摄像头实时识别"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("⚠️ 摄像头无法打开")
            return
        
        # 设置合理的分辨率和帧率，平衡性能和效果
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        cap.set(cv2.CAP_PROP_FPS, 15)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            res = self.recognize(frame)
            
            # 显示识别结果
            self._put_text(frame, f"Gesture: {res.gesture}", (10, 20))
            if self.enable_pose:
                self._put_text(frame, f"Pose: {res.pose}", (10, 45))
            
            cv2.imshow("KidVision", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        cap.release()
        cv2.destroyAllWindows()

    def recognize(self, frame) -> VisionResult:
        """识别图像中的手势和姿态"""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        gesture = None
        pose_state = None

        # 手势识别
        if self.enable_gesture and self.hands:
            hand_res = self.hands.process(rgb)
            gesture = self._analyze_hand(hand_res, frame)

        # 姿态识别
        if self.enable_pose and self.pose:
            pose_res = self.pose.process(rgb)
            pose_state = self._analyze_pose(pose_res, frame)

        return VisionResult(gesture, pose_state)

    # ------------------ 手势 ------------------
    def _analyze_hand(self, result, frame) -> Optional[str]:
        """分析手势，返回手指数量对应的文字"""
        if not result.multi_hand_landmarks:
            return None
        
        hand_lms = result.multi_hand_landmarks[0]
        landmarks = hand_lms.landmark
        
        # 使用 MediaPipe 原生绘制方法
        if self.draw_landmarks or self.draw_connections:
            if self.draw_landmarks and self.draw_connections:
                # 完整绘制（特征点 + 连接线）
                self.drawer.draw_landmarks(
                    frame, hand_lms, self.mp_hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=self.landmark_style,
                    connection_drawing_spec=self.connection_style
                )
            elif self.draw_landmarks:
                # 只绘制特征点
                self.drawer.draw_landmarks(
                    frame, hand_lms, None,
                    landmark_drawing_spec=self.landmark_style
                )
            elif self.draw_connections:
                # 只绘制连接线
                self.drawer.draw_landmarks(
                    frame, hand_lms, self.mp_hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.connection_style
                )
        
        # 高性能手指计数 - 直接用归一化坐标比较
        tips = [4, 8, 12, 16, 20]  # 手指尖
        fingers = []
        
        # 拇指 (比较 x 坐标)
        if landmarks[tips[0]].x > landmarks[tips[0] - 1].x:
            fingers.append(1)
        else:
            fingers.append(0)
            
        # 其他四指 (比较 y 坐标)
        for i in range(1, 5):
            if landmarks[tips[i]].y < landmarks[tips[i] - 2].y:
                fingers.append(1)
            else:
                fingers.append(0)
        
        finger_count = sum(fingers)
        mapping = {0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}
        return mapping.get(finger_count, str(finger_count))

    # ------------------ 姿态 ------------------
    def _analyze_pose(self, result, frame) -> Optional[str]:
        """分析姿态"""
        if not result.pose_landmarks:
            return None
            
        # 使用 MediaPipe 原生绘制方法
        if self.draw_landmarks or self.draw_connections:
            pose_landmark_style = mp.solutions.drawing_styles.get_default_pose_landmarks_style()
            if self.draw_landmarks and self.draw_connections:
                self.drawer.draw_landmarks(
                    frame, result.pose_landmarks, self.mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=pose_landmark_style
                )
            elif self.draw_landmarks:
                self.drawer.draw_landmarks(
                    frame, result.pose_landmarks, None,
                    landmark_drawing_spec=pose_landmark_style
                )
            elif self.draw_connections:
                self.drawer.draw_landmarks(
                    frame, result.pose_landmarks, self.mp_pose.POSE_CONNECTIONS
                )
                
        lms = result.pose_landmarks.landmark
        h, _w, _ = frame.shape
        
        nose_y = lms[self.mp_pose.PoseLandmark.NOSE].y * h
        lwrist_y = lms[self.mp_pose.PoseLandmark.LEFT_WRIST].y * h
        rwrist_y = lms[self.mp_pose.PoseLandmark.RIGHT_WRIST].y * h
        
        left_up = lwrist_y < nose_y
        right_up = rwrist_y < nose_y
        
        if left_up and right_up:
            return "both_hands_up"
        if left_up:
            return "left_hand_up"
        if right_up:
            return "right_hand_up"
        return "stand"

    # ------------------ 工具 ------------------
    @staticmethod
    def _put_text(img, text: str, pos: Tuple[int, int]):
        """在图像上显示文字"""
        cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA) 