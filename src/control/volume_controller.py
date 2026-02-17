import platform
import subprocess


class VolumeController:
    def __init__(self):
        self.os_name = platform.system()

        if self.os_name == "Windows":
            self._init_windows()
        elif self.os_name == "Linux":
            self._init_linux()
        elif self.os_name == "Darwin":
            self._init_macos()
        else:
            raise NotImplementedError(f"Unsupported OS: {self.os_name}")

    # ---------------- WINDOWS ----------------
    def _init_windows(self):
        from ctypes import POINTER, cast
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_,
            CLSCTX_ALL,
            None
        )
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))

    def _set_windows(self, percent: int):
        scalar = percent / 100.0
        self.volume.SetMasterVolumeLevelScalar(scalar, None)

    # ---------------- LINUX ----------------
    def _init_linux(self):
        import pulsectl

        self.pulse = pulsectl.Pulse("gesture-volume-control")
        self.sink = self.pulse.sink_list()[0]

    def _set_linux(self, percent: int):
        self.pulse.volume_set_all_chans(self.sink, percent / 100.0)

    # ---------------- MACOS ----------------
    def _init_macos(self):
        # uses osascript via subprocess
        pass

    def _set_macos(self, percent: int):
        subprocess.run(
            ["osascript", "-e", f"set volume output volume {percent}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    # ---------------- PUBLIC API ----------------
    def set_volume(self, percent: int):
        percent = max(0, min(100, int(percent)))

        if self.os_name == "Windows":
            self._set_windows(percent)
        elif self.os_name == "Linux":
            self._set_linux(percent)
        elif self.os_name == "Darwin":
            self._set_macos(percent)
