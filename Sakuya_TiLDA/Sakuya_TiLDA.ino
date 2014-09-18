#include "U8glib.h"
#include "UniversalButtons.h"
#include "TiLDA_MKe.h"

#include "bitmaps.h"
#include "types.h"

#define SERIAL SerialUSB
#define BAUD 115200
#define SERIAL_COMMAND_BUF_LEN 400
#define SERIAL_DEBUG

#define BACKLIGHT_IDLE_TIMEOUT_MS 30000

TiLDA_MKe tilda;
display_t display = DISPLAY_IDLE;

nlist_t *notif_list_head;
nlist_t *current_display_notif;

void setup(void)
{
  SERIAL.begin(BAUD);

  enable_backlight();

  // Set button callback
  tilda.buttons.setStateCycleCallback(&button_handler);
}

void loop()
{
  bool new_notifications = false;

  // Process new messages from serial
  while(SERIAL.available())
  {
    char *data;
    read_in_data(&data, ';', SERIAL_COMMAND_BUF_LEN);

#ifdef SERIAL_DEBUG
    SERIAL.print("Got command data: ");
    SERIAL.println(data);
#endif

    switch(data[0])
    {
      case 'N':
        if(process_notification_message(data))
          new_notifications = true;
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

  // Switch to notifications if there are new ones
  if(new_notifications)
  {
    current_display_notif = notif_list_tail();
    display = DISPLAY_NOTIFICATIONS;
    enable_backlight();
  }

  // Make sure there are notifications before trying to display any
  if((display == DISPLAY_NOTIFICATIONS) && (!current_display_notif))
    display = DISPLAY_IDLE;

  // Display some text on the GLCD
  tilda.glcd.firstPage();
  do
    glcd_draw();
  while(tilda.glcd.nextPage());
}

/**
 * Basic handler for button state changes.
 */
void button_handler(buttonid_t id, uint32_t time)
{
  // Ignore short presses
  if(time < 100)
    return;

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
      display = DISPLAY_NOTIFICATIONS;
      if(!current_display_notif)
        current_display_notif = notif_list_tail();
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
  notification_t *current_notif = current_display_notif->notification;

  switch(id)
  {
    case BUTTON_DOWN:
      // Go to previous notification
      if(current_display_notif->prev)
        current_display_notif = current_display_notif->prev;
      break;

    case BUTTON_UP:
      // Go to next notification
      if(current_display_notif->next)
        current_display_notif = current_display_notif->next;
      break;

    case BUTTON_A:
      // Try to find a new notification to display
      if(current_display_notif->next)
        current_display_notif = current_display_notif->next;
      else if(current_display_notif->prev)
        current_display_notif = current_display_notif->prev;
      else
        display = DISPLAY_IDLE;

      notif_list_remove(current_notif);
      current_display_notif = NULL;
      break;

    case BUTTON_B:
      display = DISPLAY_IDLE;
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

  sscanf(data, "%c|%d|%d|%[^'|']|%[^'|']",
      &msg_type, &(notification->type), &(notification->bitmap_id), summary, timestamp);

  if(msg_type != 'N')
    return false;

  notification->summary = new char[strlen(summary) + 1];
  memcpy(notification->summary, summary, strlen(summary) + 1);

  notification->timestamp = new char[strlen(timestamp) + 1];
  memcpy(notification->timestamp, timestamp, strlen(timestamp) + 1);

#ifdef SERIAL_DEBUG
  SERIAL.println("Got notification message:");
  SERIAL.print("- Type: ");
  SERIAL.println(notification->type);
  SERIAL.print("- Bitmap ID: ");
  SERIAL.println(notification->bitmap_id);
  SERIAL.print("- Summary: ");
  SERIAL.println(notification->summary);
  SERIAL.print("- Timestamp: ");
  SERIAL.println(notification->timestamp);
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

  if(!current)
    return NULL;

  while(current->next)
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

  while(current)
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

/**
 * Update the GLCD.
 */
void glcd_draw()
{
  switch(display)
  {
    case DISPLAY_IDLE:
      draw_idle();
      break;

    case DISPLAY_NOTIFICATIONS:
      draw_notification(current_display_notif->notification);
      break;
  }
}

/**
 * Draws the idle/no notifications display.
 */
void draw_idle()
{
  tilda.glcd.drawBitmapP(0, 0, 8, 64, sakuya_1_bitmap);

  tilda.glcd.setFont(u8g_font_helvR12);

  tilda.glcd.drawStr(80, 22, "No");
  tilda.glcd.drawStr(75, 37, "New");
  tilda.glcd.drawStr(70, 52, "Alerts");
}

/**
 * Draws infor for a given notification.
 *
 * @param notif Notification to draw
 */
void draw_notification(notification_t *notif)
{
  // Draw graphic
  switch(notif->bitmap_id)
  {
    case 0:
      tilda.glcd.drawBitmapP(0, 0, 8, 64, sakuya_1_bitmap);
      break;
    case 1:
      tilda.glcd.drawBitmapP(0, 0, 8, 64, sakuya_2_bitmap);
      break;
    case 2:
      tilda.glcd.drawBitmapP(0, 0, 8, 64, yuuka_bitmap);
      break;
    case 3:
      tilda.glcd.drawBitmapP(0, 0, 8, 64, shiki_bitmap);
      break;
    case 4:
      tilda.glcd.drawBitmapP(0, 0, 8, 64, flan_bitmap);
      break;
    case 5:
      tilda.glcd.drawBitmapP(0, 0, 8, 64, patchy_1_bitmap);
      break;
    case 6:
      tilda.glcd.drawBitmapP(0, 0, 8, 64, patchy_2_bitmap);
      break;
  }

  // Draw title
  tilda.glcd.setFont(u8g_font_courR10);
  tilda.glcd.setFontPosTop();
  switch(notif->type)
  {
    case NOTIFICATION_TICKET:
      tilda.glcd.drawStr(64, 0, "Ticket");
      break;
    case NOTIFICATION_BUILD:
      tilda.glcd.drawStr(64, 0, "Build");
      break;
    case NOTIFICATION_CALENDAR:
      tilda.glcd.drawStr(64, 0, "Event");
      break;
    case NOTIFICATION_EMAIL:
      tilda.glcd.drawStr(64, 0, "Email");
      break;
  }

  // Draw summary
  tilda.glcd.setFont(u8g_font_6x10);
  tilda.drawWrappedStr(64, 10, 63, 50, notif->summary);

  // Draw timestamp
  tilda.glcd.setFont(u8g_font_5x7);
  tilda.glcd.setFontPosBaseline();
  tilda.glcd.drawStr(64, 64 + tilda.glcd.getFontDescent(), notif->timestamp);
}
