#include "contiki.h"
#include "net/routing/routing.h"
#include "random.h"
#include "net/netstack.h"
#include "net/ipv6/simple-udp.h"
#include "sys/node-id.h"
#include "os/dev/button-hal.h"
#include "os/dev/serial-line.h"
#include "os/dev/leds.h"

#include "coap-engine.h"
#include "coap-blocking-api.h"

#include "sys/log.h"
#include "sys/etimer.h"

#define LOG_MODULE "NODE"
#define LOG_LEVEL LOG_LEVEL_INFO

#define UDP_CLIENT_PORT	8765
#define UDP_SERVER_PORT	5678

#define SERVER_EP "coap://[fd00::1]:5683"
#define SERVER_REGISTRATION "registration"

#define TOGGLE_INTERVAL 10

static struct etimer register_timer;

bool registered = false;
bool pressed = false;
bool occupied = false;

char datas[10];

extern coap_resource_t res_client;
extern coap_resource_t res_lock;

/*---------------------------------------------------------------------------*/
PROCESS(coap_client, "CoAP Client");
PROCESS(sensor_node, "Sensor node");
AUTOSTART_PROCESSES(&coap_client, &sensor_node);

/*---------------------------------------------------------------------------*/
void response_handler(coap_message_t *response){
	const uint8_t *chunk;
	if(response == NULL) {
		puts("Request timed out");
		return;
	}
	int len = coap_get_payload(response, &chunk);
	printf("|%.*s\n", len, (char *)chunk);
}

/*---------------------------------------------------------------------------*/
/**
 * Node behave as coap_client in order to register to the rpl_border_router.
 */
PROCESS_THREAD(coap_client, ev, data){

	static coap_endpoint_t server_ep;
	static coap_message_t request[1];
	uip_ipaddr_t dest_ipaddr;

	PROCESS_BEGIN();
	leds_set(LEDS_NUM_TO_MASK(LEDS_GREEN));
	coap_endpoint_parse(SERVER_EP, strlen(SERVER_EP), &server_ep);

	etimer_set(&register_timer, TOGGLE_INTERVAL * CLOCK_SECOND);

	while(1) {

		printf("Waiting connection..\n");
		PROCESS_YIELD();

		if((ev == PROCESS_EVENT_TIMER && data == &register_timer) || ev == PROCESS_EVENT_POLL) {

			if(NETSTACK_ROUTING.node_is_reachable() && NETSTACK_ROUTING.get_root_ipaddr(&dest_ipaddr)){
				printf("--Registration--\n");

				coap_init_message(request, COAP_TYPE_CON, COAP_GET, 0);
				coap_set_header_uri_path(request, (const char *)&SERVER_REGISTRATION);
				char msg[300];
				strcpy(msg,"{\"NodeType\":\"Both\",\"MoteResource\":\"client\",\"NodeID\":");
				char node[2];
				sprintf(node,"%d",node_id);
				strcat(msg,node);
				strcat(msg,"}");
				printf("%s\n", msg);
				coap_set_payload(request, (uint8_t *)msg, strlen(msg));

				registered = true;
				COAP_BLOCKING_REQUEST(&server_ep, request, response_handler);
				// registered = true;
				break;
			}

			else{
				printf("Not rpl address yet\n");
			}
			etimer_reset(&register_timer);
		}
	}

	PROCESS_END();
}


/*---------------------------------------------------------------------------*/
/**
 * Node behave as coap_server in order to publish messages
 */
PROCESS_THREAD(sensor_node, ev, data){

	button_hal_button_t *btn;

	PROCESS_BEGIN();

	btn = button_hal_get_by_index(0);

	coap_activate_resource(&res_lock, "lock");
	coap_activate_resource(&res_client, "client");

	while (1) {

		PROCESS_YIELD();
		if ((ev == button_hal_press_event) && !pressed && !occupied) {
			if (registered) {
				printf("Button pressed\n");
				btn = (button_hal_button_t *)data;
				printf("Release event (%s)\n", BUTTON_HAL_GET_DESCRIPTION(btn));
				pressed = !pressed;
			}
		}

		if ((ev == button_hal_press_event) && !pressed && occupied) {
			if (registered) {
				printf("Button pressed: leave place\n");
				btn = (button_hal_button_t *)data;
				printf("Release event (%s)\n", BUTTON_HAL_GET_DESCRIPTION(btn));
				pressed = !pressed;
			}
		}

		if ((ev == serial_line_event_message) && pressed && !occupied) {
			if (registered) {
				printf("Received: %s\n",(char*)data);
				strcpy(datas,(char*)data);
				printf("Datas written %s\n",datas);
				res_client.trigger();
				// Elaborate message
				pressed = false;
				occupied = true;
			}
		}

		if ((ev == serial_line_event_message) && pressed && occupied) {
			if (registered) {
				printf("Received (leaving mode): %s\n",(char*)data);
				// Elaborate message
				strcpy(datas,(char*)data);
				printf("Datas written %s\n",datas);
				res_client.trigger();
				pressed = false;
				occupied = false;
			}
		}


		// PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&notify_timer));
		//
		// if (ev == PROCESS_EVENT_TIMER && data == &notify_timer) {
		// 	if (registered) {
		//
		// 		printf("Trigger presence\n");
		//
		// 		res_presence.trigger();
		//
		// 	}
		//
		// 	etimer_set(&notify_timer,NOTIFY_PRESENCE_INTERVAL*CLOCK_SECOND);
		// }



	}


	PROCESS_END();
}
