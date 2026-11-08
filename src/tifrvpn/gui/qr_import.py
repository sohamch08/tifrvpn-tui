"""Local webcam/image importer; scanning starts only when run is called."""

import time

import numpy as np
import zxingcpp
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtMultimedia import (
    QCamera,
    QMediaCaptureSession,
    QMediaDevices,
    QVideoSink,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..totp import current_code, decode_export


def run(*, image=False):
    app = QApplication.instance() or QApplication([])
    if not isinstance(app, QApplication):
        raise RuntimeError("The QR importer requires a QApplication instance.")
    clipboard = app.clipboard()

    class Scanner(QWidget):
        def __init__(self):
            super().__init__()
            self.account = None
            self.last_scan = 0
            self.copied = None
            self.setWindowTitle("TIFR — import Google Authenticator locally")
            self.resize(860, 700)
            layout = QVBoxLayout(self)
            intro = QLabel(
                "On your phone: Google Authenticator → Transfer codes → Export → select only TIFR.\n"
                "Use a local QR image or hold the QR toward the camera. Everything stays on this laptop."
            )
            intro.setWordWrap(True)
            layout.addWidget(intro)
            self.preview = QLabel("Starting webcam…")
            self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.preview.setMinimumSize(640, 360)
            layout.addWidget(self.preview, 1)
            self.open_button = QPushButton("Open QR image from this laptop…")
            self.open_button.clicked.connect(self.open_image)
            layout.addWidget(self.open_button)
            self.status = QLabel("No camera frames or setup keys are saved to files.")
            self.status.setWordWrap(True)
            layout.addWidget(self.status)
            self.key = QLineEdit()
            self.key.setReadOnly(True)
            self.key.setEchoMode(QLineEdit.EchoMode.Password)
            self.key.setPlaceholderText(
                "The setup key will appear here after a successful scan"
            )
            layout.addWidget(self.key)
            show = QCheckBox("Reveal setup key in this window")
            show.toggled.connect(
                lambda checked: self.key.setEchoMode(
                    QLineEdit.EchoMode.Normal
                    if checked
                    else QLineEdit.EchoMode.Password
                )
            )
            layout.addWidget(show)
            self.copy = QPushButton(
                "Copy setup key for KeePassXC (clears after 60 seconds)"
            )
            self.copy.setEnabled(False)
            self.copy.clicked.connect(self.copy_key)
            layout.addWidget(self.copy)
            self.code = QLabel()
            self.code.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            layout.addWidget(self.code)
            instructions = QLabel(
                "After scanning: KeePassXC → right-click TIFR → TOTP → Set up TOTP.\n"
                "Paste the setup key and match the displayed digits, period and algorithm.\n"
                "Compare the codes with your phone, then save the KeePassXC database."
            )
            instructions.setWordWrap(True)
            layout.addWidget(instructions)
            self.session = QMediaCaptureSession(self)
            self.sink = QVideoSink(self)
            self.session.setVideoSink(self.sink)
            self.sink.videoFrameChanged.connect(self.frame)
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.refresh_code)
            self.timer.start(1000)
            cameras = QMediaDevices.videoInputs() if not image else []
            if not cameras:
                self.preview.setText("Open the QR image using the button below")
                self.status.setText(
                    "Image mode: the webcam is off. No decoded setup keys are saved to files."
                )
                return
            self.camera = QCamera(cameras[0], self)
            formats = [
                fmt
                for fmt in cameras[0].videoFormats()
                if 640 <= fmt.resolution().width() <= 1920
            ]
            if formats:
                self.camera.setCameraFormat(
                    max(formats, key=lambda fmt: fmt.resolution().width())
                )
            self.session.setCamera(self.camera)
            self.camera.errorOccurred.connect(
                lambda *_: self.status.setText(
                    "Camera error: " + self.camera.errorString()
                )
            )
            self.camera.start()

        def open_image(self):
            if self.account:
                return
            if hasattr(self, "camera"):
                self.camera.stop()
            path, _ = QFileDialog.getOpenFileName(
                self,
                "Open Google Authenticator export QR",
                "",
                "Images (*.png *.jpg *.jpeg *.webp *.bmp);;All files (*)",
            )
            if not path:
                return
            image = QImage(path)
            if image.isNull():
                self.status.setText(
                    "Could not open this image. Select a PNG or JPEG containing the export QR."
                )
                return
            self.scan_image(image)
            if not self.account:
                self.status.setText(
                    "No supported single-entry export QR was found. Use the original full-resolution image and select only TIFR when exporting."
                )

        def frame(self, frame):
            if self.account or time.monotonic() - self.last_scan < 0.2:
                return
            self.last_scan = time.monotonic()
            image = frame.toImage()
            if image.isNull():
                return
            self.preview.setPixmap(
                QPixmap.fromImage(image).scaled(
                    self.preview.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            self.scan_image(image)

        def scan_image(self, image):
            gray = image.convertToFormat(QImage.Format.Format_Grayscale8)
            pixels = np.frombuffer(gray.constBits(), dtype=np.uint8).reshape(
                gray.height(), gray.bytesPerLine()
            )[:, : gray.width()]
            try:
                results = zxingcpp.read_barcodes(
                    pixels, formats=zxingcpp.BarcodeFormats(zxingcpp.BarcodeFormat.QRCode)
                )
                for result in results:
                    self.account = decode_export(result.text)
                    break
            except Exception:  # noqa: BLE001 - Never expose authentication data from backend errors.
                self.status.setText(
                    "Could not import this QR. Export only the TIFR entry from Google Authenticator and try again."
                )
                return
            if self.account:
                if hasattr(self, "camera"):
                    self.camera.stop()
                self.open_button.setEnabled(False)
                print(
                    "QR decoded locally; camera stopped. Complete the import in KeePassXC.",
                    flush=True,
                )
                self.preview.clear()
                self.preview.setText("QR scanned — camera is off")
                self.key.setText(self.account["secret"])
                self.copy.setEnabled(True)
                self.status.setText(
                    f"Account: {self.account['name']} | Issuer: {self.account['issuer']}\n"
                    f"Settings: {self.account['algorithm']}, {self.account['digits']} digits, {self.account['period']} seconds"
                )
                self.refresh_code()

        def refresh_code(self):
            if self.account:
                remaining = (
                    self.account["period"] - int(time.time()) % self.account["period"]
                )
                self.code.setText(
                    f"Current code: {current_code(self.account)}   ({remaining} seconds remaining)"
                )

        def copy_key(self):
            if self.account is None:
                return
            self.copied = self.account["secret"]
            clipboard.setText(self.copied)
            QTimer.singleShot(60000, self.clear_clipboard)

        def clear_clipboard(self):
            if self.copied and clipboard.text() == self.copied:
                clipboard.clear()
            self.copied = None

        def closeEvent(self, event):
            if hasattr(self, "camera"):
                self.camera.stop()
            self.clear_clipboard()
            self.key.clear()
            self.account = None
            event.accept()

    window = Scanner()
    window.show()
    return app.exec()
