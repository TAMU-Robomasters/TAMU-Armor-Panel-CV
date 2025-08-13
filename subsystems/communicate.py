from ctypes import Structure, c_uint8, c_float, c_bool
import serial
from time import time, monotonic
from main import start_time, panels
serial_port = "/dev/ttyTHS0"
baudrate = 115200


def setup_serial_port():
    print('')  # spacer
    if not serial_port:
        print('[Communication]: Port=None so no communication')
        return None  # disable port
    else:
        print(f'[Communication]: Port={serial_port}')
        try:
            return serial.Serial(
                serial_port,
                baudrate=baudrate,
                timeout=.05,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
        except Exception as error:
            import subprocess
            # very bad hack but it works
            # FIXME
            subprocess.run(["bash", "-c", f"sudo -S chmod 777 '{serial_port}' <<<  \"$(cat \"$HOME/.pass\")\" ", ])
            return setup_serial_port()  # recursion until it works


#
# initialize
#
port = setup_serial_port()


# C++ struct
class MessageToEmbedded(Structure):
    _pack_ = 1
    _fields_ = [
        ("magic_number", c_uint8),
        ("X", c_float),
        ("Y", c_float),
        ("Z", c_float),
        ("capture_delay", c_uint8),
        ("status", c_uint8),
    ]


message_to_embedded = MessageToEmbedded(ord('a'), 0.0, 0.0, 0.0, 0, 0)


#
# main
#
def when_aiming_refreshes():
    global port
    capture_delay = (time()-start_time) * 1000
    print("monotonic", monotonic() * 1E3)
    print("time", time() * 1E3)
    # capture_delay = min(int(monotonic()*1000 - capture_time), 255) # max 255 ms delay
    # TODO: figure out how to get a good capture delay value automatically

    # Sending XYZ position (meters), time since frame capture, and status of target relative to front of camera plane
    if len(panels) < 1:
        message_to_embedded.X = message_to_embedded.Y = message_to_embedded.Z = 0.0
        message_to_embedded.status = 0
    else:
        message_to_embedded.X = float(panels[0].x)
        message_to_embedded.Y = float(panels[0].z)
        message_to_embedded.Z = float(panels[0].y)
        message_to_embedded.status = 1
    message_to_embedded.capture_delay = capture_delay
    print(
        #f'''msg({f"X:{message_to_embedded.X:.4f}".rjust(7)}, {f"Y:{message_to_embedded.Y:.4f}".rjust(7)}, {f"Z:{message_to_embedded.Z:.4f}".rjust(7)}, {f"delay:{message_to_embedded.capture_delay}"}ms, {f"status: {runtime.aiming.target_status.name}"})''',
        end=", ")

    try:
        port.write(bytes(message_to_embedded))
    except Exception as error:
        print(f"\n[Communication]: error when writing over UART: {error}")
        port = setup_serial_port()  # attempt re-setup


# overwrite function if port is None
if port is None:
    def when_aiming_refreshes():
        pass  # do nothing intentionally