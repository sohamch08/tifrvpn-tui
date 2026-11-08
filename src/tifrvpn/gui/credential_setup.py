"""Interactive credential setup; dialogs open only when setup is called."""

from PySide6.QtWidgets import QApplication, QInputDialog, QLineEdit, QMessageBox

from ..credentials import read_login, recipient_key, save_password


def setup(password_file, database, entry, recipient, *, on_progress=None):
    _app = QApplication.instance() or QApplication(
        []
    )  # Keep Qt alive through all dialogs.
    if password_file.exists() or password_file.is_symlink():
        answer = QMessageBox.question(
            None,
            "TIFR OTP setup",
            f"Replace the encrypted password file?\n{password_file}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return 130
    recipient = recipient_key(recipient)
    while True:
        password, accepted = QInputDialog.getText(
            None,
            "TIFR OTP — encrypt KeePassXC password",
            f"Enter the MASTER PASSWORD for this KeePassXC database:\n{database}\n\n"
            "It will be verified locally, then encrypted with your GPG key.\n"
            "This is the database password, not your TIFR VPN password.",
            QLineEdit.EchoMode.Password,
        )
        if not accepted:
            return 130
        try:
            read_login(password, database, entry)
        except RuntimeError as error:
            QMessageBox.warning(None, "Could not verify database password", str(error))
            continue
        break
    save_password(password, password_file, recipient)
    password = None
    if on_progress is not None:
        on_progress(
            f"Verified the TOTP entry and saved the GPG-encrypted database password: {password_file}"
        )
    QMessageBox.information(
        None,
        "TIFR OTP ready",
        "The encrypted password file is ready.\n\nRun tifr-otp to get the current code.",
    )
    return 0
