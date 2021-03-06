#ifndef _SAKUYA_TYPES_H
#define _SAKUYA_TYPES_H

/**
 * Represents display modes.
 */
enum display_t
{
  DISPLAY_IDLE,
  DISPLAY_NOTIFICATIONS
};

/**
 * Represents types of notifications.
 */
enum ntype_t
{
  NOTIFICATION_TICKET,
  NOTIFICATION_BUILD,
  NOTIFICATION_CALENDAR,
  NOTIFICATION_EMAIL,
  NOTIFICATION_GITHUB,
  NOTIFICATION_IRC
};

/**
 * Represents the current backlight mode.
 */
enum backlightmode_t
{
  BACKLIGHT_OFF,
  BACKLIGHT_ON_TIMEOUT,
  BACKLIGHT_ON
};

/**
 * Stores data for a notification.
 */
struct notification_t
{
  ntype_t type;
  uint8_t bitmap_id;
  char *summary;
  char *timestamp;
};

/**
 * Data type for notification linked lists.
 */
struct nlist_t
{
  notification_t *notification;
  nlist_t *next;
  nlist_t *prev;
};

#endif //_SAKUYA_TYPES_H
