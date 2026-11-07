"""Expected failures that applications can handle without exiting."""


class VPNError(RuntimeError):
    def __init__(self, message, *, returncode=1):
        super().__init__(message)
        self.returncode = returncode


class ConfigurationError(VPNError):
    pass


class CredentialError(VPNError):
    pass


class AuthenticationError(VPNError):
    pass


class NetworkManagerError(VPNError):
    pass


class ProfileNotFound(NetworkManagerError):
    pass


class ConnectionBusy(NetworkManagerError):
    """A tunnel is already changing state and cannot be connected again."""
