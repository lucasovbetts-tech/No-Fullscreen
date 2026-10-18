"""
no_fullscreen.py - kicks browsers out of fullscreen instantly (Windows only).
No dependencies, just run:  python no_fullscreen.py
Stop with Ctrl+C.
"""
import ctypes
import ctypes.wintypes as wt
import time

DEBUG = True  # prints window info when focus/size changes; set False once working

# Use real pixel coordinates (fixes mismatches with 125%/150% display scaling)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

BROWSERS = {"chrome.exe", "msedge.exe", "firefox.exe", "brave.exe",
            "opera.exe", "vivaldi.exe"}

VK_F11 = 0x7A
KEYEVENTF_KEYUP = 0x0002
MONITOR_DEFAULTTONEAREST = 2
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
POLL = 0.1  # seconds between checks


class MONITORINFO(ctypes.Structure):
    _fields_ = [("cbSize", wt.DWORD), ("rcMonitor", wt.RECT),
                ("rcWork", wt.RECT), ("dwFlags", wt.DWORD)]


def process_name(hwnd):
    pid = wt.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    h = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
    if not h:
        return ""
    try:
        buf = ctypes.create_unicode_buffer(260)
        size = wt.DWORD(260)
        if kernel32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size)):
            return buf.value.rsplit("\\", 1)[-1].lower()
        return ""
    finally:
        kernel32.CloseHandle(h)


def window_info(hwnd):
    r = wt.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(r))
    mon = user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)
    mi = MONITORINFO(cbSize=ctypes.sizeof(MONITORINFO))
    user32.GetMonitorInfoW(mon, ctypes.byref(mi))
    return r, mi.rcMonitor, bool(user32.IsZoomed(hwnd))


def is_fullscreen(hwnd):
    if not hwnd:
        return False
    r, m, _ = window_info(hwnd)
    # Fullscreen = window exactly matches the monitor.
    # (Maximised windows overhang the edges by ~8px, so they never match.)
    return (r.left, r.top, r.right, r.bottom) == (m.left, m.top, m.right, m.bottom)


def press(vk):
    user32.keybd_event(vk, 0, 0, 0)
    user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)


def main():
    print("Watching for fullscreen browsers... (Ctrl+C to stop)")
    last = None
    while True:
        hwnd = user32.GetForegroundWindow()
        name = process_name(hwnd)
        if DEBUG and hwnd:
            r, m, zoomed = window_info(hwnd)
            state = (hwnd, name, (r.left, r.top, r.right, r.bottom), zoomed)
            if state != last:
                print(f"{name:15} window={state[2]} "
                      f"monitor={(m.left, m.top, m.right, m.bottom)} "
                      f"maximised={zoomed} fullscreen={is_fullscreen(hwnd)}")
                last = state
        if name in BROWSERS and is_fullscreen(hwnd):
            if DEBUG:
                print("  -> pressing F11")
            press(VK_F11)
            time.sleep(0.3)           # let the window resize before re-checking
        time.sleep(POLL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass