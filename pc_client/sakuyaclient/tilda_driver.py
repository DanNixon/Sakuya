import time
import serial
from enum import Enum


class NotificationTypes(Enum):
    """
    Used to identify a TiLDA notification type.
    """

    TICKET = 0
    BUILD = 1
    CALENDAR = 2
    EMAIL = 3


class Bitmaps(Enum):
    """
    Used to identify a bitmap for the GLCD.
    """

    SAKUYA_1 = 0
    SAKUYA_2 = 1
    YUUKA = 2
    SHIKI = 3
    FLAN = 4
    PATCHY_1 = 5
    PATCHY_2 = 6
    MARISA = 7
    SUIKA = 8


class TiLDADriver(object):

    def __init__(self, write_delay=0.1):
        """
        Creates a new TiLDA MKe serial driver.

        @param write_delay Time in seconds to wait after sending a serial message (default 0.1s)
        """

        self._port = None

        self._message_delimiter = ';'
        self._serial_eol = '\r\n'

        self._write_delay = write_delay

    def connect(self, port='ttyACM0', baud=115200):
        """
        Connects to a TiLDA on the given port at a given baud rate.

        @param port Serail port to connect over
        @param baud Baud rate to connect at
        @return True of successful connection
        """

        self._port = serial.Serial(port=port,
                                   baudrate=baud)

        # AFAIK PySerial calls open() in the constructor now, but I'll keep this to be sure port is open
        if not self._port.isOpen():
            self._port.open()

        return self._port.isOpen()

    def release(self):
        """
        Disconnects the active serial connection.
        """

        if self._port is not None:
            self._port.close()
            self._port = None

    def _send_message(self, message):
        """
        Sends a message to the port.

        @param message Raw message to send
        """

        port_message = message + self._message_delimiter + self._serial_eol

        self._port.write(port_message.encode())
        time.sleep(self._write_delay)

    def set_led(self, led_id, red, green, blue):
        """
        Sets an RGB LED on the TiLDA to a given colour.

        @param led_id ID of the LED (1 or 2)
        @param red Red intensity
        @param green Green intensity
        @param blue Blue intensity
        """

        message_format = 'L|%d|%d|%d|%d'
        message = message_format % (led_id, red, green, blue)
        self._send_message(message)

    def send_notification(self, notif_type, bitmap_id, summary, timestamp):
        """
        Sends a new notification to the TiLDA.

        @param notif_type Integer notfication type
        @param bitmap_id Integer bitmap ID
        @param summary Message to be shown
        @param timestamp Timestamp string
        """

        message_format = 'N|%d|%d|%s|%s'
        message = message_format % (notif_type, bitmap_id, summary, timestamp)
        self._send_message(message)

    def play_tone(self, frequencey, duration):
        """
        Plays a tone on the TiLDA peizo speaker.

        @param frequencey Frequencey of the tone to be played
        @param duration Time in ms to play the tone for
        """

        message_format = 'T|%d|%d'
        message = message_format % (frequencey, duration)
        self._send_message(message)
