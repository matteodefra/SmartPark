#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "contiki.h"
#include "coap-engine.h"
#include "coap-observe.h"
#include "os/dev/leds.h"
#include "os/dev/button-hal.h"
#include "os/dev/serial-line.h"
#include "sys/etimer.h"

#include "sys/log.h"
#define LOG_MODULE "lock sensor"
#define LOG_LEVEL LOG_LEVEL_DBG

#define MAX_PRESENCE 30
#define MIN_PRESENCE 10

extern bool occupied;
extern char datas[10];
// int presence;

static void res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);

static void res_event_handler(void);


EVENT_RESOURCE(res_client,
	"title=\"Client sensor\";methods=\"GET\";rt=\"int\";obs\n",
	res_get_handler,
	NULL,
  NULL,
	NULL,
	res_event_handler);


static void res_event_handler(void){
	// Change presence value and notify observers
	printf("Data values %s\n",datas);
	coap_notify_observers(&res_client);
}

static void res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset){


	int length;

	char msg[300];
	strcpy(msg,"{\"ClientInfo\":\"");
	strcat(msg,datas);
	strcat(msg,"\",\"BoxSituation\":\"");
	// F=free, B=busy
	char val2 = occupied == 0 ? 'F': 'B';
  strncat(msg,&val2,1);
	strcat(msg,"\"}");
	length = strlen(msg);
	memcpy(buffer, (uint8_t *)msg, length);

	printf("Message to send %s\n",msg);

	///
	memset(datas,0,10);

	coap_set_header_content_format(response, TEXT_PLAIN);
	coap_set_header_etag(response, (uint8_t *)&length, 1);
	coap_set_payload(response, (uint8_t *)buffer, length);

}
