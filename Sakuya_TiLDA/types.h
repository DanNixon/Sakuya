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
  NOTIFICATION_EMAIL
};

/**
 * Stores data for a notification.
 */
struct notification_t
{
  ntype_t type;
  char *name;
  char *timestamp;

  char *old_state;
  char *new_state;

  int8_t change_importance;
};

/**
 * Data type for notification linked lists.
 */
struct nlist_t
{
  notification_t *notification;
  nlist_t *next;
};

#endif //_SAKUYA_TYPES_H
