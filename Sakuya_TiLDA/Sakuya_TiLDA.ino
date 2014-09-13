#include "U8glib.h"
#include "UniversalButtons.h"
#include "TiLDA_MKe.h"

#include "bitmaps.h"
#include "types.h"

#define SERIAL SerialUSB
#define BAUD 115200
#define SERIAL_COMMAND_BUF_LEN 200
#define SERIAL_DEBUG

#define BACKLIGHT_IDLE_TIMEOUT_MS 30000

TiLDA_MKe tilda;
display_t display = DISPLAY_IDLE;

void setup(void)
{
  SERIAL.begin(BAUD);

  enable_backlight();

  // Set button callback
  tilda.buttons.setStateCycleCallback(&button_handler);
}

void loop()
{
  // Process new messages from serial
  while(SERIAL.available())
  {
    char *data;
    read_in_data(&data, '#', SERIAL_COMMAND_BUF_LEN);

#ifdef SERIAL_DEBUG
    SERIAL.print("Got command data: ");
    SERIAL.println(data);
#endif

    switch(data[0])
    {
      case 'N':
        process_notification_message(data);
        break;
      case 'L':
        process_led_message(data);
        break;
      default:
        break;
    }
  }

  // See if there were any button changes
  tilda.buttons.poll();

  // Poll backlight timeout
  backlight_timeout(BACKLIGHT_IDLE_TIMEOUT_MS);

  // Display some text on the GLCD
  tilda.glcd.firstPage();
  do
  {
    //TODO

    tilda.glcd.drawBitmapP(0, 0, 8, 64, sakuya_1_bitmap);
  }
  while(tilda.glcd.nextPage());
}

/**
 * Basic handler for button state changes.
 */
void button_handler(buttonid_t id, uint32_t time)
{
  // Toggle backlight on pressing Light button
  if(id == BUTTON_LIGHT)
  {
    if(tilda.backlight())
      tilda.setBacklight(LCD_BACKLIGHT_OFF);
    else
      enable_backlight();
  }

  // Handle buttons for each mode
  // Enable backlight if the button is valid for that mode
  switch(display)
  {
    case DISPLAY_IDLE:
      if(handle_idle_buttons(id))
        enable_backlight();
      break;
    case DISPLAY_NOTIFICATIONS:
      if(handle_notification_buttons(id))
        enable_backlight();
      break;
    default:
      return;
  }
}

/**
 * Handles notifications for the idle display mode.
 *
 * @param id ID of button that was pressed
 */
bool handle_idle_buttons(buttonid_t id)
{
  switch(id)
  {
    case BUTTON_DOWN:
    case BUTTON_UP:
    case BUTTON_A:
      //TODO: Go to notification display
      break;
    default:
      return false;
  }

  return true;
}

/**
 * Handles notifications for the notification browse display mode.
 *
 * @param id ID of button that was pressed
 */
bool handle_notification_buttons(buttonid_t id)
{
  switch(id)
  {
    case BUTTON_DOWN:
      //TODO: Go to previous notification
      break;
    case BUTTON_UP:
      //TODO: Go to next notification
      break;
    case BUTTON_A:
      //TODO: Dismiss notification
      break;
    case BUTTON_B:
      //TODO: Go to idle display
      break;
    default:
      return false;
  }

  return true;
}

uint64_t backlight_on_time;

/**
 * Sets the time the backlight was enabled and enables it.
 */
void enable_backlight()
{
  tilda.setBacklight(LCD_BACKLIGHT_ON);
  backlight_on_time = millis();
}

/**
 * Checks to see if a given amount of time has passed since the backlight was turned on.
 *
 * Disables if time has passed.
 *
 * @param timeout Time in ms backlight should stay on for after last activity
 */
void backlight_timeout(uint64_t timeout)
{
  uint64_t delta_t = millis() - backlight_on_time;
  if(delta_t > timeout)
  {
    tilda.setBacklight(LCD_BACKLIGHT_OFF);
    backlight_on_time = 0;
  }
}

/**
 * Reads a section of data from the serial port up to either a given
 * delimiter or maximum size (whichever comes first).
 *
 * @param data Double pointer for data output
 * @param delimiter Character to stop at
 * @param buff_size Maximum number of characters to buffer
 */
uint8_t read_in_data(char **data, char delimiter, uint8_t buff_size)
{
  char buff[buff_size];
  char c;
  uint8_t i = 0;
  do
  {
    c = SERIAL.read();
    if(c == delimiter)
      break;

    buff[i] = c;
    i++;
  }
  while(SERIAL.available() && (i < buff_size));
  buff[i] = '\0';

  *data = (char *) malloc(i+1);
  memcpy(*data, buff, i+1);
}

/**
 * Processes a serial message to control the LEDs.
 *
 * @param data LED data
 */
bool process_led_message(char *data)
{
  char msg_type;
  uint8_t led_id, r, g, b;

  sscanf(data, "%c|%d|%d|%d|%d", &msg_type, &led_id, &r, &g, &b);

  if(msg_type != 'L')
    return false;

#ifdef SERIAL_DEBUG
  SERIAL.println("Got LED control message:");
  SERIAL.print("- LED ID: ");
  SERIAL.println(led_id);
  SERIAL.print("- R: ");
  SERIAL.println(r);
  SERIAL.print("- G: ");
  SERIAL.println(g);
  SERIAL.print("- B: ");
  SERIAL.println(b);
#endif

  if(led_id == 0)
    tilda.setLEDs(r, g, b);
  else
    tilda.setLED(led_id, r, g, b);

  return true;
}

/**
 * Processes a notification message.
 *
 * @param data Notification data
 */
void process_notification_message(char *data)
{
  //TODO
}
