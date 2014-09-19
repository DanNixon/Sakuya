import pyserial


class TiLDADriver(object):

    def __init__(self):
        pass

    def connect(self, port='ttyACM0', baud=115200):
        """
        Connects to a TiLDA on the given port at a given baud rate.

        @param port Serail port to connect over
        @param baud Baud rate to connect at
        @return True of successful connection
        """

        return False

    def release(self):
        """
        Disconnects the active serial connection.
        """

        pass

    def set_led(self, led_id, red, green, blue):
        """
        Sets an RGB LED on the TiLDA to a given colour.

        @param led_id ID of the LED (1 or 2)
        @param reg Red intensity
        @param green Green intensity
        @param blue Blue intensity
        """

        pass

    def send_notification(self, notif_type, bitmap_id, message, timestamp):
        """
        Sends a new notification to the TiLDA.

        @param notif_type Integer notfication type
        @param bitmap_id Integer bitmap ID
        @param message Message to be shown
        @param timestamp Timestamp string
        """

        pass

    def play_tone(self, frequencey, time):
        """
        Plays a tone on the TiLDA peizo speaker.

        @param frequencey Frequencey of the tone to be played
        @param time Time in ms to play the tone for
        """

        pass
