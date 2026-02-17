import cv2

from vision.hand_tracker import HandTracker
from utils.smoothing import ExponentialSmoother, rate_limit
from control.volume_controller import VolumeController




CAMERA_INDEX = 0
WINDOW_NAME = "PC Volume Gesture Control"

# Mapping & safety parameters
TOP_MARGIN = 0.1
BOTTOM_MARGIN = 0.9
MAX_STEP = 5            # max volume change per frame
PINCH_THRESHOLD = 0.04  # pinch sensitivity


def map_y_to_volume(y_norm: float) -> int:
    """
    Map normalized Y (0 top → 1 bottom) to volume (0–100)
    with safety margins.
    """
    y_clamped = max(TOP_MARGIN, min(BOTTOM_MARGIN, y_norm))
    y_scaled = (y_clamped - TOP_MARGIN) / (BOTTOM_MARGIN - TOP_MARGIN)
    return int((1.0 - y_scaled) * 100)


def is_pinch(hand) -> bool:
    """
    Returns True if thumb and index finger are pinched.
    """
    thumb = hand.landmark[4]   # thumb tip
    index = hand.landmark[8]   # index finger tip

    dx = thumb.x - index.x
    dy = thumb.y - index.y
    distance = (dx ** 2 + dy ** 2) ** 0.5

    return distance < PINCH_THRESHOLD


def draw_volume_bar(frame, volume: int):
    h, w, _ = frame.shape
    bar_x = w - 60
    bar_top = int(h * 0.1)
    bar_bottom = int(h * 0.9)

    # Outline
    cv2.rectangle(frame, (bar_x, bar_top), (bar_x + 30, bar_bottom),
                  (255, 255, 255), 2)

    # Fill
    fill_height = int((volume / 100) * (bar_bottom - bar_top))
    cv2.rectangle(
        frame,
        (bar_x, bar_bottom - fill_height),
        (bar_x + 30, bar_bottom),
        (0, 255, 0),
        -1
    )

    # Label
    cv2.putText(
        frame,
        f"{volume}%",
        (bar_x - 20, bar_top - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )


def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError("ERROR: Webcam not accessible")

    tracker = HandTracker()
    smoother = ExponentialSmoother(alpha=0.3)

    # 🔊 System volume controller (OS-agnostic)
    volume_controller = VolumeController()

    volume = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = tracker.process(frame)

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            tracker.draw(frame, hand)

            if is_pinch(hand):
                raw_volume = map_y_to_volume(hand.landmark[8].y)
                smooth_volume = smoother.update(raw_volume)
                volume = int(rate_limit(smooth_volume, volume, MAX_STEP))

                # 🔊 APPLY REAL SYSTEM VOLUME
                volume_controller.set_volume(volume)

                cv2.putText(
                    frame,
                    "ACTIVE",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    3
                )
            else:
                cv2.putText(
                    frame,
                    "INACTIVE",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    3
                )

        draw_volume_bar(frame, volume)
        cv2.imshow(WINDOW_NAME, frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
