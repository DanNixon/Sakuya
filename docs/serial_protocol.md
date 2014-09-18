Serial Protocol
===============

Message delimiter: ```;```

Notification: ```N|type|bitmap_id|summary|timestamp```
- ```type```: Notification type
- ```bitmap_id```: Integer ID of bitmap to be shown
- ```summary```: Textual summary
- ```timestamp```: Textual timestamp

LED: ```L|id|r|g|b```
- ```id```: ID of LED to use (1 or 2, 0 for all)
- ```r, g, b```: Intensity of each colour channel

Notification Types
------------------

- 0=Ticket
- 1=Build
- 2=Calendar
- 3=Email

Bitmaps
-------

- 0=Sakuya 1
- 1=Sakuya 2
- 2=Yuuka
- 3=Shiki
- 4=Flan
- 5=Patchy 1
- 6=Patchy 2
