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

nlist_t *notif_list_head;

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
 * @returns True if parsing was successful, false otherwise
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
 * @returns True if parsing was successful, false otherwise
 */
bool process_notification_message(char *data)
{
  size_t data_len = strlen(data);

  char msg_type;
  notification_t *notification = new notification_t;

  char summary[data_len];
  char timestamp[data_len];
  char old_state[data_len];
  char new_state[data_len];

  sscanf(data, "%c|%d|%[^'|']|%[^'|']|%[^'|']|%[^'|']|%d",
      &msg_type, &(notification->type), summary, timestamp, old_state, new_state, &(notification->change_score));

  if(msg_type != 'N')
    return false;

  notification->summary = new char[strlen(summary) + 1];
  memcpy(notification->summary, summary, strlen(summary) + 1);

  notification->timestamp = new char[strlen(timestamp) + 1];
  memcpy(notification->timestamp, timestamp, strlen(timestamp) + 1);

  notification->old_state = new char[strlen(old_state) + 1];
  memcpy(notification->old_state, old_state, strlen(old_state) + 1);

  notification->new_state = new char[strlen(new_state) + 1];
  memcpy(notification->new_state, new_state, strlen(new_state) + 1);

#ifdef SERIAL_DEBUG
  SERIAL.println("Got notification message:");
  SERIAL.print("- Type: ");
  SERIAL.println(notification->type);
  SERIAL.print("- Summary: ");
  SERIAL.println(notification->summary);
  SERIAL.print("- Timestamp: ");
  SERIAL.println(notification->timestamp);
  SERIAL.print("- Prev. status: ");
  SERIAL.println(notification->old_state);
  SERIAL.print("- Status: ");
  SERIAL.println(notification->new_state);
  SERIAL.print("- Change score: ");
  SERIAL.println(notification->change_score);
#endif

  notif_list_append(notification);
}

/**
 * Returns a pointer to the last node in the notifications linked list.
 *
 * @returns Tail node
 */
nlist_t *notif_list_tail()
{
  nlist_t *current = notif_list_head;

  while(current->next != NULL)
    current = current->next;

  return current;
}

/**
 * Appends a new notification to the linked list.
 *
 * @param notif Notification to append
 */
void notif_list_append(notification_t *notif)
{
  nlist_t *node = new nlist_t;
  node->notification = notif;
  node->next = NULL;

  if(notif_list_head)
  {
    nlist_t *tail = notif_list_tail();
    tail->next = node;
    node->prev = tail;
  }
  else
  {
    node->prev = NULL;
    notif_list_head = node;
  }
}

/**
 * Removes the notification from the linked list.
 *
 * @param notif Notification to remove
 * @returns True if removed successfully, false otherwise
 */
bool notif_list_remove(notification_t *notif)
{
  nlist_t *current = notif_list_head;

  while(current != NULL)
  {
    if(current->notification == notif)
      break;

    current = current->next;
  }

  if(!current)
    return false;

  if(current->prev)
  {
    current->prev->next = current->next;
  }
  else
  {
    current->prev = NULL;
    notif_list_head = current->next;
  }

  if(current->next)
    current->next->prev = current->prev;

  delete[] notif;
  delete[] current;

  return true;
}
