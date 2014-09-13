Serial Protocol
===============

Message delimiter: ```#```

Notification: ```N|type|summary|timestamp|prev_status|status|change_score```
- ```type```: Notification type, index from ```ntype_t``` enum
- ```summary```: Textual summary
- ```timestamp```: Textual timestamp
- ```prev_status```: Textual previous status (if applicable, empty string if not)
- ```status```: Textual current status (if applicable, empty string if not)
- ```change_score```: Signed integer representing how "good" the difference in ```prev_status``` and ``status``` is

LED: ```L|id|r|g|b```
- ```id```: ID of LED to use (1 or 2, 0 for all)
- ```r, g, b```: Intensity of each colour channel
