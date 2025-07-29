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
    """手势 + 姿态识别"""

    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_pose = mp.solutions.pose
        self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=1,
                                         min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.drawer = mp.solutions.drawing_utils

    # ------------------ 公共 ------------------
    def run(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("⚠️ 摄像头无法打开")
            return
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            res = self.recognize(frame)
            self._put_text(frame, f"G:{res.gesture}", (10, 20))
            self._put_text(frame, f"P:{res.pose}", (10, 45))
            cv2.imshow("KidVision", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

    def recognize(self, frame) -> VisionResult:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hand_res = self.hands.process(rgb)
        pose_res = self.pose.process(rgb)
        gesture = self._analyze_hand(hand_res, frame)
        pose_state = self._analyze_pose(pose_res, frame)
        return VisionResult(gesture, pose_state)

    # ------------------ 手势 ------------------
    def _analyze_hand(self, result, frame) -> Optional[str]:
        if not result.multi_hand_landmarks:
            return None
        hand_lms = result.multi_hand_landmarks[0]
        handedness_label = None
        if result.multi_handedness:
            handedness_label = result.multi_handedness[0].classification[0].label  # Left / Right
        self.drawer.draw_landmarks(frame, hand_lms, self.mp_hands.HAND_CONNECTIONS)

        tips = [4, 8, 12, 16, 20]
        x_list, y_list = [], []
        h, w, _ = frame.shape
        for lm in hand_lms.landmark:
            x_list.append(int(lm.x * w))
            y_list.append(int(lm.y * h))

        fingers = []
        # Thumb
        if handedness_label == "Right":
            fingers.append(1 if x_list[tips[0]] < x_list[tips[0]-1] else 0)
        elif handedness_label == "Left":
            fingers.append(1 if x_list[tips[0]] > x_list[tips[0]-1] else 0)
        else:
            fingers.append(0)
        # Other four fingers
        for idx in range(1, 5):
            fingers.append(1 if y_list[tips[idx]] < y_list[tips[idx]-2] else 0)
        count = sum(fingers)
        mapping = {0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}
        return mapping.get(count, str(count))

    # ------------------ 姿态 ------------------
    def _analyze_pose(self, result, frame) -> Optional[str]:
        if not result.pose_landmarks:
            return None
        self.drawer.draw_landmarks(frame, result.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
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
        cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA) 