from enum import Enum
import glob
import logging
import serial
from serial.serialutil import SerialException
import time


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

    def auto_connect(self, baud=115200):
        """
        Attempts to find a TiLDA on any available serial port.

        @param baud Baud rate to connect at
        """

        ports = glob.glob('/dev/tty[A-Za-z]*')

        for port in ports:
            try:
                self.connect(port, baud)
            except SerialException:
                continue

            if self.ping():
                return
            else:
                self.release()

        raise RuntimeError('TiLDA not found on any port')

    def connect(self, port='ttyACM0', baud=115200):
        """
        Connects to a TiLDA on the given port at a given baud rate.

        @param port Serail port to connect over
        @param baud Baud rate to connect at
        """

        self._port = port
        self._baud = baud

        logging.getLogger(__name__).debug('Opening serial port %s at baud rate %d', port, baud)
        self._port = serial.Serial(port=port,
                                   baudrate=baud,
                                   timeout=1)

        # AFAIK PySerial calls open() in the constructor now, but I'll keep this to be sure port is open
        if not self._port.isOpen():
            self._port.open()

        if not self._port.isOpen():
            raise RuntimeError('Port is not open')

        if not self.ping():
            raise RuntimeError('TiLDA not found on open port')

    def release(self):
        """
        Disconnects the active serial connection.
        """

        if self._port is not None:
            logging.getLogger(__name__).debug('Closing serial port')
            self._port.close()
            self._port = None

    def ping(self):
        """
        Attempts to ping the TiLDA on the active serial port
        """

        logging.getLogger(__name__).debug('Pinging serial port')

        self._send_message('P')
        data = self._port.read(size=12);
        self._port.flushInput()
        logging.getLogger(__name__).debug('Ping data: %s', str(data))

        ping_good = str(data) == 'SAKUYA_TILDA'
        logging.getLogger(__name__).debug('Ping result: %s', str(ping_good))

        return ping_good

    def _send_message(self, message):
        """
        Sends a message to the port.

        @param message Raw message to send
        """

        port_message = message + self._message_delimiter + self._serial_eol
        logging.getLogger(__name__).debug('Serial message: %s', port_message)

        try:
            self._port.write(port_message.encode())
        except SerialException:
            logging.getLogger(__name__).warning('Failed to write to serial port!')
            self.release()
            self.auto_connect(self._baud)
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
