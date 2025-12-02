"""
camera_handler.py

Handler léger pour capturer des images depuis une caméra et détecter des QR codes en continu.
Version simplifiée: ne reconnaît que deux types de payloads dans le QR code :
 - adresse e-mail (type "EMAIL")
 - suite de chiffres (type "NUMERIC")

Dépendances:
- opencv-python (cv2)
- numpy
"""
from typing import Callable, List, Optional, Tuple, Dict, Any
import threading
import time
import re

import cv2
import numpy as np

_email_re = re.compile(r'^[A-Za-z0-9._%+\-]+@(?:epitech\.eu|epitech\.digital)$', re.IGNORECASE)
_digits_re = re.compile(r'^13081410\d*$')
class CameraHandler:
    """
    Capture vidéo + détection continue de QR codes (filtrés: email / digits).

    Usage basique:
        cam = CameraHandler(camera_index=0)
        cam.start()
        data = cam.wait_for_qr(timeout=5)  # bloque jusqu'à détection ou timeout
        cam.stop()
    """
    def __init__(
        self,
        camera_index: int = 0,
        width: int = 640,
        height: int = 480,
        fps: int = 30,
        use_thread: bool = True,
        decode_interval: float = 0.0,
    ) -> None:
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.fps = fps
        self.use_thread = use_thread
        self.decode_interval = float(decode_interval)

        self._cap: Optional[cv2.VideoCapture] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.RLock()

        self._latest_frame: Optional[np.ndarray] = None
        self._latest_qr: List[Dict[str, Any]] = []
        self._callbacks: List[Callable[[List[Dict[str, Any]], np.ndarray], None]] = []

        # Condition pour wait_for_qr
        self._qr_condition = threading.Condition(self._lock)

        # Simplifié: on utilise uniquement OpenCV QRCodeDetector
        self._cv_detector = cv2.QRCodeDetector()

    # --- ouverture et fermeture ---
    def start(self, reopen: bool = False) -> None:
        with self._lock:
            if self._cap is None or reopen:
                self._cap = cv2.VideoCapture(self.camera_index, cv2.CAP_ANY)
                self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                self._cap.set(cv2.CAP_PROP_FPS, self.fps)
            if not self._cap.isOpened():
                raise RuntimeError(f"Impossible d'ouvrir la caméra index={self.camera_index}")

            self._stop_event.clear()
            if self.use_thread:
                if self._thread is None or not self._thread.is_alive():
                    self._thread = threading.Thread(target=self._capture_loop, daemon=True)
                    self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
        with self._lock:
            if self._cap is not None:
                try:
                    self._cap.release()
                except Exception:
                    pass
                self._cap = None

    def is_running(self) -> bool:
        return not self._stop_event.is_set() and self._cap is not None and self._cap.isOpened()

    # --- lecture et callbacks ---
    def register_callback(self, fn: Callable[[List[Dict[str, Any]], np.ndarray], None]) -> None:
        with self._lock:
            self._callbacks.append(fn)

    def unregister_callback(self, fn: Callable[[List[Dict[str, Any]], np.ndarray], None]) -> None:
        with self._lock:
            if fn in self._callbacks:
                self._callbacks.remove(fn)

    def read(self) -> Tuple[Optional[np.ndarray], List[Dict[str, Any]]]:
        with self._lock:
            frame = None if self._latest_frame is None else self._latest_frame.copy()
            qr = list(self._latest_qr)
        return frame, qr

    def wait_for_qr(self, timeout: Optional[float] = None) -> Optional[List[Dict[str, Any]]]:
        end = None if timeout is None else (time.time() + timeout)
        with self._qr_condition:
            while True:
                if self._latest_qr:
                    return list(self._latest_qr)
                now = time.time()
                if end is not None and now >= end:
                    return None
                remaining = None if end is None else (end - now)
                self._qr_condition.wait(timeout=remaining)

    # --- capture ---
    def capture_once(self) -> None:
        with self._lock:
            if self._cap is None:
                raise RuntimeError("Camera non ouverte. Appelez start().")
        self._do_capture_cycle()

    def _capture_loop(self) -> None:
        while not self._stop_event.is_set():
            cycle_start = time.time()
            self._do_capture_cycle()
            if self.decode_interval > 0:
                elapsed = time.time() - cycle_start
                to_sleep = max(0.0, self.decode_interval - elapsed)
                if to_sleep > 0:
                    time.sleep(to_sleep)

    def _do_capture_cycle(self) -> None:
        with self._lock:
            if self._cap is None or not self._cap.isOpened():
                return
            ret, frame = self._cap.read()
            if not ret or frame is None:
                time.sleep(0.01)
                return
            self._latest_frame = frame

        qr_list = self._decode_frame(frame)

        with self._lock:
            self._latest_qr = qr_list
            if qr_list:
                with self._qr_condition:
                    self._qr_condition.notify_all()
                for cb in list(self._callbacks):
                    try:
                        cb(qr_list, frame)
                    except Exception:
                        pass

    # --- décodage QR (simplifié: email / numeric only) ---
    def _decode_frame(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        qr_results: List[Dict[str, Any]] = []
        try:
            detector = self._cv_detector
            # prefer detectAndDecodeMulti si disponible
            if hasattr(detector, 'detectAndDecodeMulti'):
                retval, decoded_info, points, _ = detector.detectAndDecodeMulti(frame)
                if retval and decoded_info:
                    for info, pts in zip(decoded_info, points):
                        if not info:
                            continue
                        info = info.strip()
                        typ = None
                        if _email_re.match(info):
                            typ = 'EMAIL'
                        elif _digits_re.match(info):
                            typ = 'NUMERIC'
                        else:
                            continue  # on ignore les autres contenus
                        polygon = [{'x': float(p[0]), 'y': float(p[1])} for p in pts.reshape((-1, 2))]
                        xs = pts[:, 0]; ys = pts[:, 1]
                        rect = {'left': int(xs.min()), 'top': int(ys.min()), 'width': int(xs.max()-xs.min()), 'height': int(ys.max()-ys.min())}
                        qr_results.append({'data': info, 'type': typ, 'rect': rect, 'polygon': polygon})
                    return qr_results
            # fallback single decode
            data, pts, _ = detector.detectAndDecode(frame)
            if data:
                data = data.strip()
                if _email_re.match(data):
                    typ = 'EMAIL'
                elif _digits_re.match(data):
                    typ = 'NUMERIC'
                else:
                    return []
                polygon = []
                rect = {}
                if pts is not None:
                    pts = np.array(pts).reshape((-1, 2))
                    polygon = [{'x': float(p[0]), 'y': float(p[1])} for p in pts]
                    xs = pts[:, 0]; ys = pts[:, 1]
                    rect = {'left': int(xs.min()), 'top': int(ys.min()), 'width': int(xs.max()-xs.min()), 'height': int(ys.max()-ys.min())}
                qr_results.append({'data': data, 'type': typ, 'rect': rect, 'polygon': polygon})
        except Exception:
            pass
        return qr_results