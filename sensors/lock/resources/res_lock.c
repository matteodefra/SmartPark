#include "contiki.h"
#include "coap-engine.h"
#include <string.h>
#include "time.h"
#include "os/dev/leds.h"

/* Log configuration */
#include "sys/log.h"
#define LOG_MODULE "lock sensor"
#define LOG_LEVEL LOG_LEVEL_DBG

extern bool pressed;
extern bool occupied;

static void res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);

static void res_post_put_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);

RESOURCE(res_lock,
         "title=\"Lock actuator: ?POST/PUT\";obs;rt=\"lock\"",
         res_get_handler,
         res_post_put_handler,
         res_post_put_handler,
         NULL);

static void res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset)
{

	// Create a JSON message with the detected presence value and led value
	// In both the resources the get_handler return the current sensor values
	int length;

	char msg[300];
  // F = free box
  // B = busy box
	char val2 = occupied == 0 ? 'F': 'B';
  strcpy(msg,"{\"Box situation\":\"");
  strncat(msg,&val2,1);
	strcat(msg,"\"}");
	length = strlen(msg);
	memcpy(buffer, (uint8_t *)msg, length);

	coap_set_header_content_format(response, TEXT_PLAIN);
	coap_set_header_etag(response, (uint8_t *)&length, 1);
	coap_set_payload(response, (uint8_t *)buffer, length);

}

static void res_post_put_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset)
{
	if(request != NULL) {
		LOG_DBG("POST/PUT Request Sent\n");
	}

  printf("Post handler called\n");


	size_t len = 0;
	const char *state = NULL;
	int check = 1;

	if((len = coap_get_post_variable(request, "state", &state))) {
		if (atoi(state) == 1){
			leds_set(LEDS_NUM_TO_MASK(LEDS_RED));
		}

		else if(atoi(state) == 0){
			leds_set(LEDS_NUM_TO_MASK(LEDS_GREEN));

		}

		else{
			check = 0;
		}

		occupied = atoi(state);

	}
	else{
		check = 0;
	}

	if (check){
		coap_set_status_code(response, CHANGED_2_04);
	}
	else{
		coap_set_status_code(response, BAD_REQUEST_4_00);
	}

}
