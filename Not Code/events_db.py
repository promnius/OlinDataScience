/**
* @file
* @brief header file for the fan controller database
*
* @note  the DB description:
*  To request a log point, send the MCC:    getlog type=T point=X nosgfx=false
*
*  where T can be: none priv pub key erasepriv erasepub erasekey
*
*  where X can be: 0 to (log_size-2)   (log_size is dependant on which log
*  you read, and is a #define in events_db.h)
*
*  The SGFx will receive a response similar to:
*  getlog point=1 type=priv nosgfx=false size=100 time=84636250 buffer=434D525F5F5869544F6D7475 event=1073741836
*
*  where 'size' is the number of log points currently in the log
*
*  where 'time' is the number of seconds since EPOCH.  Date/time convert
*  routines are located in rtc_helper.c/h
*
*  where 'buffer' is (currently) a 12 character array of U8's.  It is up to the
*  programmer to supply the data, and it may or may not be terminated.  While
*  it may contain human readable text, it is up to the programmer to decide
*  what goes in there and it may just be debug data.  The real information is
*  in 'event'.  This is a 32bit enum, as defined in events_db.h.  While you must
*  request log entries by location (private, public, or keypress), the enum is
*  unique. Similar to comments I have made on the MCC serial number, buffer is
*  sent as a series of HEX pairs.  Don't try to parse the DBapi string, but
*  rather just access the database itself
*
*  special use of erase:
*  As added protection, X will need to be 0xAA55 (decimal 43605)
*
*  nosgfx flag:
*  The 'nosgfx' flag is to allow other callers to manually request a log
*  without informing the SGFx about it.  While not likely to be anything other
*  then 'false', it would be a good idea to always send it down.  Also, always
*  send all 3 parameters in a single DBapi command, not doing so may result in
*  fetching the wrong log point.
*
*  Error cases and special output formats:
*  Requesting a log type of 'none', a log point larger then (log_size-1), or
*  erasing a log will result in size, time, buffer, and event being zero (there
*  is a EVENT_NONE which is zero, so you should still be able to parse the
*  result.  EVENT_NONE has no other purpose then to indicate a blank or
*  invalid event.  In addition, erasing a log will also reset the point to zero.
*
*  small problems:
*  Requesting the same log point sequentially may not respond at all, this is
*  because the DBapi didn't detect a DB change, and thus didn't trigger the
*  MCC EVENT task to read out a log point.
*
*  Unlike otherDBapi commands being sent to the SGFx, this one maybe delayed.
*  Nothing is returned until it has completed what it was suppose to do (ie,
*  read the EEPROM or erase the log)
*
*/
//
//  Copyright (c) 2009 Cybex International, Inc. All Rights Reserved
//  Copyright (c) IAR, Inc. All Rights Reserved
//
/************************************************************************/
#ifndef __LOG_GET_DB_H_
#define __LOG_GET_DB_H_

/*  Note that the +1 on the 'LOG_SIZE' defines below are to allow for a marker */
/*  in the EEPROM to indicate the end of the log.  1 sequential 'empty' event  */
/*  indicates the log is full.  2 (or more) sequential 'empty' events indicates*/
/*  the log is not full.                                                       */
#define PUBLIC_EVENT_LOG_SIZE                 (20+1) /**< how many public event entrees can be stored in the EEPROM */
#define PRIVATE_EVENT_LOG_SIZE                (100+1)/**< how many private (engineering) event entrees can be stored in the EEPROM */
#define KEYPRESS_EVENT_LOG_SIZE               (100+1)/**< how many keypress (engineering) event entrees can be stored in the EEPROM */
#define HR_EVENT_LOG_SIZE                     (100+1)/**< how many heart-rate (engineering) event entrees can be stored in the EEPROM */
#define EXTRA_EVENT_INFO_SIZE                 12     /**< how many bytes of 'debugging information' is stored along with the event */
#define EVENT_REPEATED_TIMEOUT                5      /**< in seconds, don't report the same event/error if it happenned recently */

typedef enum {
             EVENT_TYPE_NONE,
             EVENT_TYPE_PRIVATE,
             EVENT_TYPE_PUBLIC,
             EVENT_TYPE_KEYPRESS,
             EVENT_TYPE_ERASE_PRIVATE,
             EVENT_TYPE_ERASE_PUBLIC,
             EVENT_TYPE_ERASE_KEYPRESS,
             EVENT_TYPE_MAX,
             EVENT_TYPE_LAST = (EVENT_TYPE_MAX - 1),
             EVENT_TYPE_FIRST = EVENT_TYPE_NONE
             } event_type_t;

typedef enum {
             EVENT_NONE                      = 0x00000000,
             EVENT_END_OF_LOG,

             EVENT_MESG                      = 0x00000000, /**< informational message, generally used in non-public log */
             EVENT_SOFT                      = 0x00100000, /**< SOFT errors are just logged but no user interaction is required */
             EVENT_ESTOP                     = 0x00200000, /**< a SOFT error that toggles estop */
             EVENT_HARD                      = 0x00400000, /**< HARD errors set info->state = UI_STATE_ERROR_HARD */
             EVENT_OOO                       = 0x00800000, /**< OOO (Out Of Order) errors set info->state = UI_STATE_OUT_OF_ORDER */

             EVENT_LOG_LOCATION_MASK         = 0xF8000000,
             EVENT_UNUSED_BITS_MASK          = 0x07000000,
             EVENT_LOG_SEVERITY_MASK         = 0x00F00000,
             EVENT_LOG_CHECK_COUNT_MASK      = 0x000F0000,
             ERROR_NUMBER_MASK               = 0x0000FFFF, /**< lower 16bits reserved for an actual error # to be displayed */

             EVENT_KEYPRESS_LOG              = 0x08000000,

             EVENT_PUBLIC_LOG                = 0x80000000,
             EVENT_PUBLIC_0_REASON_UNKNOWN   = (EVENT_PUBLIC_LOG | EVENT_OOO  | 0),   /**< 0:      The only time this will happen is immediately after power up when new errors have pushed the reason for OOO out of the system */
             EVENT_PUBLIC_1_DRIVE_DIDNT_START= (EVENT_PUBLIC_LOG | EVENT_HARD | 1),   /**< 1:      Drive did not start (No Speed at Startup) */
             EVENT_PUBLIC_2_SGFX_COMM_ISSUE  = (EVENT_PUBLIC_LOG | EVENT_SOFT | 2),   /**< 2:      GFX communication issue */
             EVENT_PUBLIC_3_SPEED_MISMATCH   = (EVENT_PUBLIC_LOG | EVENT_HARD | 3),   /**< 3:      Speed miss-match */
             EVENT_PUBLIC_4_LED_COMM_ISSUE   = (EVENT_PUBLIC_LOG | EVENT_SOFT | 4),   /**< 4:      Upper Display communication issue */
#if (defined MCC_COMMUNICATION_WITH_LCB)
             EVENT_PUBLIC_5_DRIVE_COMM_ISSUE = (EVENT_PUBLIC_LOG | EVENT_SOFT | 5),   /**< 5:      Drive Communication issue, for arc/bike use */
#else
             EVENT_PUBLIC_5_DRIVE_COMM_ISSUE = (EVENT_PUBLIC_LOG | EVENT_HARD | 5),   /**< 5:      Drive Communication issue, for TREAD use */
#endif
             EVENT_PUBLIC_6_MEMBRANE_FAULT   = (EVENT_PUBLIC_LOG | EVENT_HARD | 6),   /**< 6:      Membrane fault */
             EVENT_PUBLIC_7_CONTR_FOLDBACK   = (EVENT_PUBLIC_LOG | EVENT_SOFT | 7),   /**< 7:      Controller Fold-back */
             EVENT_PUBLIC_8_NEAR_OVER_TEMP   = (EVENT_PUBLIC_LOG | EVENT_SOFT | 8),   /**< 8:      Approaching Over-Temperature */
             EVENT_PUBLIC_9_MCC_WDT          = (EVENT_PUBLIC_LOG | EVENT_SOFT | 9),   /**< 9:      MCC Watchdog triggered  */
             EVENT_PUBLIC_10_PIR_BLOCKED     = (EVENT_PUBLIC_LOG | EVENT_SOFT | 10),  /**< 10:     Motion Sensor Blocked */
             EVENT_PUBLIC_11_PIR_ERROR       = (EVENT_PUBLIC_LOG | EVENT_SOFT | 11),  /**< 11:     Motion Sensor reading out of range / defective */
             EVENT_PUBLIC_12_SGFX_WDT        = (EVENT_PUBLIC_LOG | EVENT_HARD | 12),  /**< 12:     SGFx Watchdog triggered  */
             EVENT_PUBLIC_13_LED_WDT         = (EVENT_PUBLIC_LOG | EVENT_HARD | 13),  /**< 13:     Upper Display (LED) Watchdog triggered  */
             EVENT_PUBLIC_14_MOTOR_UNKNOWN   = (EVENT_PUBLIC_LOG | EVENT_HARD | 14),  /**< 14:     an unknown motor error has been sent */
             EVENT_PUBLIC_15_AV_DEVICE_FAIL  = (EVENT_PUBLIC_LOG | EVENT_SOFT | 15),  /**< 15:     The AV (PEM or MYE) device is either not atached when av_mode!=none, or has failed */
             EVENT_PUBLIC_16_MEMBRANE_COM_ERR= (EVENT_PUBLIC_LOG | EVENT_HARD | 16),  /**< 16:     Membrane communications problem */

             EVENT_PUBLIC_18_MEMBRANE_FAULT  = (EVENT_PUBLIC_LOG | EVENT_HARD | 18),  /**< 18:     Membrane fault after system startup */

             // LCB-specific Events
             EVENT_PUBLIC_17_FORCE_LCB_OFF     = (EVENT_PUBLIC_LOG | EVENT_SOFT | 17), /**< 17:    LCB didn't shutdown properly, we needed to yank the power */
             EVENT_PUBLIC_22_POWER_NO_SPEED    = (EVENT_PUBLIC_LOG | EVENT_SOFT | 22), /**< 22:    Have Power(18V)  but no RPM (Speed) */
             EVENT_PUBLIC_23_SPEED_NO_POWER    = (EVENT_PUBLIC_LOG | EVENT_SOFT | 23), /**< 23:    Have RPM (Speed) but no Power(18V) */
             EVENT_PUBLIC_24_INCLINE_TOO_SLOW  = (EVENT_PUBLIC_LOG | EVENT_SOFT | 24), /**< 24:    The incline is moving too slowly */
             EVENT_PUBLIC_25_INCLINE_STALLED   = (EVENT_PUBLIC_LOG | EVENT_SOFT | 25), /**< 25:    The incline motor stalled  */
             EVENT_PUBLIC_26_INCLINE_DISABLED  = (EVENT_PUBLIC_LOG | EVENT_SOFT | 26), /**< 26:    The incline motor has been disabled */
             EVENT_PUBLIC_27_LOW_BATTERY       = (EVENT_PUBLIC_LOG | EVENT_SOFT | 27), /**< 27:    The Battery has been measured as Low */
             EVENT_PUBLIC_28_OVER_TEMPERATURE  = (EVENT_PUBLIC_LOG | EVENT_HARD | 28), /**< 28:    TBD, something is over Temperature */
             EVENT_PUBLIC_29_HARDWARE_WATCHDOG = (EVENT_PUBLIC_LOG | EVENT_HARD | 29), /**< 29:    The uC Watchdog has triggered */
             EVENT_PUBLIC_30_DEAD_BATTERY      = (EVENT_PUBLIC_LOG | EVENT_SOFT | 30), /**< 30:    The Battery has been measured as Dead */
             EVENT_PUBLIC_35_NO_POWER_OFF      = (EVENT_PUBLIC_LOG | EVENT_HARD | 35), /**< 35:    LCB Cannot power down from Battery */
             EVENT_PUBLIC_37_INCLINE_RANGE     = (EVENT_PUBLIC_LOG | EVENT_SOFT | 37), /**< 37:    The incline pot is out of valid range */
             EVENT_PUBLIC_38_INCLINE_TIMEOUT   = (EVENT_PUBLIC_LOG | EVENT_SOFT | 38), /**< 38:    The incline motor routine timed out */
             
             EVENT_PUBLIC_92_OVER_CURRENT    = (EVENT_PUBLIC_LOG | EVENT_HARD | 92),  /**< 92:     Over Current (Output) */
             EVENT_PUBLIC_93_OVER_VOLTAGE    = (EVENT_PUBLIC_LOG | EVENT_HARD | 93),  /**< 93:     Over Voltage (DC Link) */
             EVENT_PUBLIC_94_OVER_TEMP       = (EVENT_PUBLIC_LOG | EVENT_HARD | 94),  /**< 94:     Over Heat (Heatsink) */
             EVENT_PUBLIC_95_LOW_VOLTAGE     = (EVENT_PUBLIC_LOG | EVENT_HARD | 95),  /**< 95:     Low Voltage (DC Link) */
             EVENT_PUBLIC_96_INT_OUT_CURR    = (EVENT_PUBLIC_LOG | EVENT_HARD | 96),  /**< 96:     Thermal Integrator of output current */
             EVENT_PUBLIC_98_COMM_LOST_STOP  = (EVENT_PUBLIC_LOG | EVENT_ESTOP| 98),  /**< 98:     Display Communication Lost - Belt speed zero */
             EVENT_PUBLIC_99_COMM_LOST_ACTIVE= (EVENT_PUBLIC_LOG | EVENT_HARD | 99),  /**< 99:     Display Communication Lost - Belt moving */
             EVENT_PUBLIC_103_INPUT_OVER_CURR= (EVENT_PUBLIC_LOG | EVENT_HARD | 103), /**< 103:    Input Current OC trip (Drives with PFC only) */
             EVENT_PUBLIC_105_INT_IN_CURRENT = (EVENT_PUBLIC_LOG | EVENT_HARD | 105), /**< 105:    Thermal Integrator of Input Current (Drives with PFC only) */
             EVENT_PUBLIC_140_NO_HOME_AT_PUP = (EVENT_PUBLIC_LOG | EVENT_ESTOP | 140), /**< 140:    Can not find home position on power-up */
             EVENT_PUBLIC_141_NO_HOME        = (EVENT_PUBLIC_LOG | EVENT_SOFT | 141), /**< 141:    Can not find home position in normal use */
             EVENT_PUBLIC_142_INCLINE_RANGE  = (EVENT_PUBLIC_LOG | EVENT_HARD | 142), /**< 142:    Out of incline range (over 15% or lower than -3%) */
             EVENT_PUBLIC_150_SPEED_RANGE    = (EVENT_PUBLIC_LOG | EVENT_HARD | 150), /**< 150:    Out of Speed Range (over 150hz) */

             EVENT_PRIVATE_LOG_INFO          = 0x40000000,
             EVENT_SETUP_DEFAULTS_INSTALLED,
             EVENT_STATS_DEFAULTS_INSTALLED,
             EVENT_DIAG_DEFAULTS_INSTALLED,
             EVENT_PRIVATE_LOG_INIT,
             EVENT_PUBLIC_LOG_INIT,
             EVENT_FAN_STALLED,
             EVENT_DEFAULT_TIME,
             EVENT_WAKEUP_GRIP,
             EVENT_WAKEUP_KEY,
             EVENT_WAKEUP_PIR,
             G_EVENT_MOT_COM_RRB_ERROR,    // Motor Com, Raw Response Buffer error
             G_EVENT_MOT_COM_RX_TIMEOUT,   // Motor Com, Response Timeout
             G_EVENT_MOT_COM_PRB_ERR_CNT,  // Motor Com, Process Response Buffer, Data Count Mismatch
             G_EVENT_MOT_COM_PRB_ERR_CRC,  // Motor Com, Process Response Buffer, CRC Mismatch
             G_EVENT_MOT_COM_PRB_ERR_UNK,  // Motor Com, Process Response Buffer, Unknown
             G_EVENT_MOT_COM_CNE_ERR,      // Motor Com, Could Not Establish (at Start Up)
             G_EVENT_MOT_ESTOP_SET,        // E-Stop Set,   E-Stop is Active (Drive is Disabled)
             G_EVENT_MOT_ESTOP_CLEAR,      // E-Stop Clear, E-Stop is Inactive (Drive is Enabled)
             EVENT_KEYPRESS_LOG_INIT,
             G_EVENT_MOT_RESP_ID_NE,       // Motor Com, Response ID Not Equal to Command ID
             G_EVENT_MOT_RESP_ID_ERR,      // Motor Com, Response ID to Command (Not Yet) Supported
             G_EVENT_MOT_RESP_ID_BAD,      // Motor Com, Response ID to Command (Not At All) Supported
             G_EVENT_MOT_DIRECTION_BAD,    // Motor Com, Attempt to set Motor in Reverse failed
             EVENT_STLED316_INVALID_KEY,
             EVENT_STLED316_INVALID_CONFIG,
             EVENT_STLED316_INVALID_READ,
             EVENT_STLED316_KEY_MISSMATCH,
             EVENT_STLED316_INVALID_DIGIT_BRIGHT,
             EVENT_STLED316_INVALID_ANN_BRIGHT,
             EVENT_AUDIO_BYTE1_MISMATCH,
             EVENT_AUDIO_BYTE2_MISMATCH,
             G_EVENT_LED_SPI_QOS_MILESTONE,     // LED SPI, has succeeded in Tx of N Packets
             G_EVENT_LED_SPI_DMA_TX_ERROR,      // LED SPI, Packet DMA Transmit Error
             G_EVENT_LED_SPI_RETRY_IRQ_TIMEOUT, // LED SPI, Retry, due to IRQ Timeout (no LED IRQ Response)
             G_EVENT_LED_SPI_RETRY_BAD_CRC,     // LED SPI, Retry, due to bad CRC in Response
             G_EVENT_LED_SPI_RETRY_UNKNOWN,     // LED SPI, Retry, due to unknown
             G_EVENT_LED_SPI_FAIL_IRQ_TIMEOUT,  // LED SPI, Failed, last error was IRQ Timeout (no LED IRQ Response)
             G_EVENT_LED_SPI_FAIL_BAD_CRC,      // LED SPI, Failed, last error was bad CRC in Response
             G_EVENT_LED_SPI_FAIL_UNKNOWN,      // LED SPI, Failed, last error was unknown
             G_EVENT_MOT_TRANS_CRC_BYTE1_F3,    // Motor Com, Transmitting 1st CRC Byte as F3 - Motor does not like this.
             EVENT_LCB_EEPROM_WRITE,            // EEPROM write error 
             EVENT_LCB_UART_ERROR,              // UART1 Error 
             EVENT_LCB_PACKET_ERROR_33,         // Receive Packet Error, Packet Sequence Mismatch
             EVENT_LCB_COMM_WATCHDOG,           // Communication Watchdog Error 
             EVENT_LCB_LUMINARY_LIB,            // Luminary DriverLib Assertion Failure
             EVENT_LCB_UART_RX_BUF_OVER,        // UART (Command Rx)  Rx Buffer Overflow
             EVENT_LCB_UART_TX_BUF_OVER,	      // UART (Response Tx) Buffer Overflow
             EVENT_LCB_PACKET_ERROR_41,         // Receive Packet Error, Raw Command Buffer Overflow
             EVENT_LCB_PACKET_ERROR_42,         // Receive Packet Error, Packet CRC Mismatch
             EVENT_LCB_PACKET_ERROR_43,         // Receive Packet Error, Packet Size Mismatch
             EVENT_LCB_ADC_ERROR,               // ADC Sequence Buffer Error
             EVENT_EPEM_POWER_STATE_MISMATCH,   // EPEM is off, MCC expects it to be on
             EVENT_EPEM_DISCONNECTED,           // EPEM communication lost, TV disconnected
             EVENT_EPEM_RESET_DETECTED,         // EPEM reset detected
             EVENT_SYSTEM_RESET,                // System reset

             EVENT_PRIVATE_LOG_SW_FAILURE    = 0x20000000,
             EVENT_TASK_DIED,
             EVENT_NULL_CHECKIN,
             EVENT_INVALID_CHECKIN,
             EVENT_WRONG_CHECKIN,
             EVENT_PROGTASK_INVALID_NEW_STATE,
             EVENT_PROGTASK_INVALID_STATE_CHANGE,
             EVENT_LEDPCB_INVALID_API_CALL,
             EVENT_OUT_OF_RANGE_DBapi_READ,
             EVENT_SGFX_REBOOT,
             EVENT_SGFX_DIED,

             EVENT_PRIVATE_LOG_HW_FAILURE    = 0x10000000,
             EVENT_EEPROM_WRITE_FAILURE,
             EVENT_EEPROM_READ_FAILURE,
             EVENT_SYSTICK_FAILED,
             EVENT_RTC_WRITE_FAILED,
             EVENT_RTC_READ_FAILED,
             EVENT_RTC_OSCILLATOR_FAULT,
             EVENT_I2C_BUS_STUCK,
             EVENT_AUDIO_FAILURE,
             EVENT_USB_OVER_CURRENT,
             EVENT_MOTOR_NOT_ZERO,

             EVENT_PLACE_HOLDER_DONT_USE
             } events_t;

typedef struct database_event  {
                               uint32_t      count;
                               events_t      event;
                               uint32_t      time;
                               } database_event_t;

typedef struct event_fetch     {
                               event_type_t  type;   /**< which log to fetch from */
                               uint16_t      point;  /**< which log point to fetch */
                               bool          nosgfx; /**< when true, it will not automatically send a 'log all' to the SGFx */

                               uint16_t      size;   /**< number of points in the log */
                               uint32_t      time;   /**< in seconds from epoch */
                               uint8_t       buffer[EXTRA_EVENT_INFO_SIZE]; /**< possible debug info */
                               events_t      event;  /**< which event was logged (per the enum above */
                               } database_get_log_t;

#define MAX_EVENT_COUNT        15
#define EVENT_COUNT_SHIFT      16
#define EVENT_COUNT_MASK_CHECK ((events_t)(MAX_EVENT_COUNT << EVENT_COUNT_SHIFT)) // This should match EVENT_LOG_CHECK_COUNT_MASK

#define DEC_EVENT_COUNT(E)     if (((E) & EVENT_LOG_CHECK_COUNT_MASK) > 0)                           (E) -= (events_t)(1 << EVENT_COUNT_SHIFT)
#define INC_EVENT_COUNT(E)     if (((E) & EVENT_LOG_CHECK_COUNT_MASK) != EVENT_LOG_CHECK_COUNT_MASK) (E) = (events_t)((int)(E) + (events_t)(1 << EVENT_COUNT_SHIFT))
#define SET_EVENT_COUNT(E, V)  if ((V) <= MAX_EVENT_COUNT)                                           (E)  = (events_t)(((E) & ~EVENT_LOG_CHECK_COUNT_MASK) | (((V) << EVENT_COUNT_SHIFT) & EVENT_LOG_CHECK_COUNT_MASK))
#define GET_EVENT_COUNT(E)     (uint8_t)(((E) & EVENT_LOG_CHECK_COUNT_MASK) >> EVENT_COUNT_SHIFT)

#define GET_ERROR_NUMBER(E)    ((E) & ERROR_NUMBER_MASK)
#endif