Serial Protocol
===============

Message delimiter: ```;```

Ping: ```P```
- Should get response: ```SAKUYA_TILDA```
- ```SERIAL_DEBUG``` will likely need to be disabled when using this

Notification: ```N|type|bitmap_id|summary|timestamp```
- ```type```: Notification type
- ```bitmap_id```: Integer ID of bitmap to be shown
- ```summary```: Textual summary
- ```timestamp```: Textual timestamp

LED: ```L|id|r|g|b```
- ```id```: ID of LED to use (1 or 2, 0 for all)
- ```r, g, b```: Intensity of each colour channel

LCD Backlight: ```B|mode```
- ```mode```: Backlight mode

Tone: ```T|freq|duration```
- ```freq```: Frequency of tone to play
- ```duration```: Time in ms to play tone for

Notification Types
------------------

- 0=Ticket
- 1=Build
- 2=Calendar
- 3=Email
- 4=GitHub
- 5=IRC

Bitmaps
-------

- 0=Sakuya 1
- 1=Sakuya 2
- 2=Yuuka
- 3=Shiki 1
- 4=Flan
- 5=Patchy 1
- 6=Patchy 2
- 7=Marisa
- 8=Suika
- 9=Shiki 2
- 10=Komachi
- 11=Nitori

Backlight Modes
---------------

- 0=Off
- 1=On with timeout (will turn off 1 timeout interval after command issued)
- 2=On indefinitely
