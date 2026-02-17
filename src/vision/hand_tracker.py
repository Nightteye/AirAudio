import cv2
import mediapipe as mp


class HandTracker:
    def __init__(
        self,
        max_hands: int = 1,
        detection_confidence: float = 0.7,
        tracking_confidence: float = 0.7
    ):
        self.mp_hands = mp.solutions.hands

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )

        self.drawer = mp.solutions.drawing_utils
        self.style_landmarks = mp.solutions.drawing_styles.get_default_hand_landmarks_style()
        self.style_connections = mp.solutions.drawing_styles.get_default_hand_connections_style()

    def process(self, frame_bgr):
        """Process a BGR frame and return MediaPipe results."""
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        return self.hands.process(frame_rgb)

    def draw(self, frame_bgr, hand_landmarks):
        """Draw landmarks and connections on the frame."""
        self.drawer.draw_landmarks(
            frame_bgr,
            hand_landmarks,
            self.mp_hands.HAND_CONNECTIONS,
            self.style_landmarks,
            self.style_connections
        )
