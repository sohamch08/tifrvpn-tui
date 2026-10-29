#!/usr/bin/env python3
"""Read one Google Authenticator migration QR locally; never log its contents."""

import base64
import argparse
import hashlib
import hmac
import struct
import sys
import time
from urllib.parse import parse_qs, urlsplit


def fields(data):
    offset = 0

    def varint():
        nonlocal offset
        value = 0
        for shift in range(0, 70, 7):
            if offset >= len(data):
                raise ValueError("Incomplete export QR.")
            byte = data[offset]
            offset += 1
            value |= (byte & 127) << shift
            if not byte & 128:
                return value
        raise ValueError("Invalid export QR.")

    while offset < len(data):
        tag = varint()
        number, wire = tag >> 3, tag & 7
        if not number:
            raise ValueError("Invalid export QR.")
        if wire == 0:
            value = varint()
        elif wire in (1, 2, 5):
            size = varint() if wire == 2 else (8 if wire == 1 else 4)
            if size > len(data) - offset:
                raise ValueError("Incomplete export QR.")
            value = data[offset:offset + size]
            offset += size
        else:
            raise ValueError("Unsupported export QR format.")
        yield number, value


def decode_export(text):
    uri = urlsplit(text)
    if uri.scheme != "otpauth-migration" or uri.netloc != "offline":
        raise ValueError("Show the Google Authenticator export QR, selecting only TIFR.")
    encoded = parse_qs(uri.query).get("data", [""])[0].replace(" ", "+")
    if not encoded or len(encoded) > 32000:
        raise ValueError("Invalid export QR.")
    try:
        payload = list(fields(base64.b64decode(encoded + "=" * (-len(encoded) % 4), validate=True)))
    except Exception:
        raise ValueError("Could not decode this export QR.") from None
    accounts = [value for number, value in payload if number == 1]
    if len(accounts) != 1 or any(number == 3 and value > 1 for number, value in payload):
        raise ValueError("Export only the TIFR entry, then scan the new QR.")
    account = dict(fields(accounts[0]))
    if not isinstance(account.get(1), bytes) or not account[1]:
        raise ValueError("The export contains no setup key.")
    algorithms = {1: "SHA1", 2: "SHA256", 3: "SHA512"}
    digits = {1: 6, 2: 8}
    if account.get(6) != 2 or account.get(4) not in algorithms or account.get(5) not in digits:
        raise ValueError("This export is not a supported time-based authenticator entry.")
    return {
        "secret": base64.b32encode(account[1]).decode().rstrip("="),
        "name": account.get(2, b"").decode("utf-8"),
        "issuer": account.get(3, b"").decode("utf-8"),
        "algorithm": algorithms[account[4]], "digits": digits[account[5]], "period": 30,
    }


def current_code(account, timestamp=None):
    secret = account["secret"]
    key = base64.b32decode(secret + "=" * (-len(secret) % 8))
    step = int(time.time() if timestamp is None else timestamp) // account["period"]
    digest = hmac.new(key, struct.pack(">Q", step), getattr(hashlib, account["algorithm"].lower())).digest()
    offset = digest[-1] & 15
    value = int.from_bytes(digest[offset:offset + 4], "big") & 0x7fffffff
    return str(value % 10 ** account["digits"]).zfill(account["digits"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", action="store_true", help="use a local QR image without starting the webcam")
    args = parser.parse_args()

    import numpy as np
    import zxingcpp
    from PySide6.QtCore import QTimer, Qt
    from PySide6.QtGui import QImage, QPixmap
    from PySide6.QtMultimedia import QCamera, QMediaCaptureSession, QMediaDevices, QVideoSink
    from PySide6.QtWidgets import (
        QApplication, QCheckBox, QFileDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget,
    )

    app = QApplication(sys.argv)

    class Scanner(QWidget):
        def __init__(self):
            super().__init__()
            self.account = None
            self.last_scan = 0
            self.copied = None
            self.setWindowTitle("TIFR — import Google Authenticator locally")
            self.resize(860, 700)
            layout = QVBoxLayout(self)
            intro = QLabel("On your phone: Google Authenticator → Transfer codes → Export → select only TIFR.\n"
                           "Use a local QR image or hold the QR toward the camera. Everything stays on this laptop.")
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
            self.key.setPlaceholderText("The setup key will appear here after a successful scan")
            layout.addWidget(self.key)
            show = QCheckBox("Reveal setup key in this window")
            show.toggled.connect(lambda checked: self.key.setEchoMode(
                QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password))
            layout.addWidget(show)
            self.copy = QPushButton("Copy setup key for KeePassXC (clears after 60 seconds)")
            self.copy.setEnabled(False)
            self.copy.clicked.connect(self.copy_key)
            layout.addWidget(self.copy)
            self.code = QLabel()
            self.code.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            layout.addWidget(self.code)
            instructions = QLabel("After scanning: KeePassXC → right-click TIFR → TOTP → Set up TOTP.\n"
                                  "Paste the setup key and match the displayed digits, period and algorithm.\n"
                                  "Compare the codes with your phone, then save the KeePassXC database.")
            instructions.setWordWrap(True)
            layout.addWidget(instructions)
            self.session = QMediaCaptureSession(self)
            self.sink = QVideoSink(self)
            self.session.setVideoSink(self.sink)
            self.sink.videoFrameChanged.connect(self.frame)
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.refresh_code)
            self.timer.start(1000)
            cameras = QMediaDevices.videoInputs() if not args.image else []
            if not cameras:
                self.preview.setText("Open the QR image using the button below")
                self.status.setText("Image mode: the webcam is off. No decoded setup keys are saved to files.")
                return
            self.camera = QCamera(cameras[0], self)
            formats = [fmt for fmt in cameras[0].videoFormats()
                       if 640 <= fmt.resolution().width() <= 1920]
            if formats:
                self.camera.setCameraFormat(max(formats, key=lambda fmt: fmt.resolution().width()))
            self.session.setCamera(self.camera)
            self.camera.errorOccurred.connect(lambda *_: self.status.setText("Camera error: " + self.camera.errorString()))
            self.camera.start()

        def open_image(self):
            if self.account:
                return
            if hasattr(self, "camera"):
                self.camera.stop()
            path, _ = QFileDialog.getOpenFileName(self, "Open Google Authenticator export QR", "",
                                                 "Images (*.png *.jpg *.jpeg *.webp *.bmp);;All files (*)")
            if not path:
                return
            image = QImage(path)
            if image.isNull():
                self.status.setText("Could not open this image. Select a PNG or JPEG containing the export QR.")
                return
            self.scan_image(image)
            if not self.account:
                self.status.setText("No supported single-entry export QR was found. Use the original full-resolution image and select only TIFR when exporting.")

        def frame(self, frame):
            if self.account or time.monotonic() - self.last_scan < 0.2:
                return
            self.last_scan = time.monotonic()
            image = frame.toImage()
            if image.isNull():
                return
            self.preview.setPixmap(QPixmap.fromImage(image).scaled(
                self.preview.size(), Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))
            self.scan_image(image)

        def scan_image(self, image):
            gray = image.convertToFormat(QImage.Format.Format_Grayscale8)
            pixels = np.frombuffer(gray.constBits(), dtype=np.uint8).reshape(
                gray.height(), gray.bytesPerLine())[:, :gray.width()]
            try:
                results = zxingcpp.read_barcodes(pixels, formats=zxingcpp.BarcodeFormat.QRCode)
                for result in results:
                    self.account = decode_export(result.text)
                    break
            except Exception:
                self.status.setText("Could not import this QR. Export only the TIFR entry from Google Authenticator and try again.")
                return
            if self.account:
                if hasattr(self, "camera"):
                    self.camera.stop()
                self.open_button.setEnabled(False)
                print("QR decoded locally; camera stopped. Complete the import in KeePassXC.", flush=True)
                self.preview.clear()
                self.preview.setText("QR scanned — camera is off")
                self.key.setText(self.account["secret"])
                self.copy.setEnabled(True)
                self.status.setText(
                    f"Account: {self.account['name']} | Issuer: {self.account['issuer']}\n"
                    f"Settings: {self.account['algorithm']}, {self.account['digits']} digits, {self.account['period']} seconds")
                self.refresh_code()

        def refresh_code(self):
            if self.account:
                remaining = self.account["period"] - int(time.time()) % self.account["period"]
                self.code.setText(f"Current code: {current_code(self.account)}   ({remaining} seconds remaining)")

        def copy_key(self):
            self.copied = self.account["secret"]
            app.clipboard().setText(self.copied)
            QTimer.singleShot(60000, self.clear_clipboard)

        def clear_clipboard(self):
            if self.copied and app.clipboard().text() == self.copied:
                app.clipboard().clear()
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


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        print("The local QR scanner could not start. No QR contents were logged.", file=sys.stderr)
        sys.exit(1)
