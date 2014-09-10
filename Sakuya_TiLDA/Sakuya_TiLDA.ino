#include "U8glib.h"
#include "UniversalButtons.h"
#include "TiLDA_MKe.h"

#include "bitmaps.h"
#include "types.h"

TiLDA_MKe tilda;
display_t display = DISPLAY_IDLE;

void setup(void)
{
  SerialUSB.begin(115200);

  enable_backlight();

  // Set button callback
  tilda.buttons.setStateCycleCallback(&button_handler);
}

void loop()
{
  // See if there were any button changes
  tilda.buttons.poll();

  // Poll backlight timeout
  backlight_timeout(10000); //TODO: Temporary value

  // Display some text on the GLCD
  tilda.glcd.firstPage();
  do
  {
    //TODO
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
    case BUTTON_LEFT:
    case BUTTON_RIGHT:
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
    case BUTTON_LEFT:
      //TODO: Go to previous notification
      break;
    case BUTTON_RIGHT:
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
