#define _GNU_SOURCE
/* For sockaddr_in */
#include <netinet/in.h>
/* For socket functions */
#include <sys/socket.h>
#include <linux/unistd.h>
#include <sys/file.h>

#include <event2/event.h>
#include <arpa/inet.h>
#include <sys/signal.h>
#include <assert.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <time.h>
#include <math.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <net/if.h>
#include <netinet/if_ether.h>
#include <net/ethernet.h>
#include <netinet/tcp.h>
#define __FAVOR_BSD
#include <netinet/udp.h>
#include <arpa/inet.h>
#include <pcap.h>
//#include <sys/file.h>
#include <sys/stat.h>

#include <sys/ioctl.h>

#include <sys/resource.h>

#include <fcntl.h>

#include <stdio.h>
#include <pthread.h>
#include <unistd.h>
#include <jansson.h>
#include <time.h>

#include "utils.h"

static pthread_t thread;

callback_quote_t global_mc_live_pcap_callback = NULL;
callback_quote_t global_mirror_live_pcap_callback = NULL;

typedef void (*quote_callback_t)(const unsigned char *data, unsigned int len, void *arg, const struct timeval *tv, int skip);

#define MAX_LINE 16384
struct fd_state {
    char buffer[MAX_LINE];
    struct in_addr mcast_ip;
    u_int16_t mcast_port;
    struct event *read_event;
    quote_callback_t callback;
    void *arg;

    char str_name[BUFSIZ];
    char str_mcast[BUFSIZ];
    char str_local[BUFSIZ];
    int int_mcast_port;
};

static void free_fd_state(struct fd_state *state)
{
    printf("state freed: %s %s:%d -> %s\n", state->str_name, state->str_mcast, state->int_mcast_port, state->str_local);
    event_free(state->read_event);
    free(state);
}

static void do_read(evutil_socket_t fd, short events, void *arg)
{
    struct fd_state *state = arg;
    unsigned char buf[BUFSIZ];
    struct sockaddr_in src_addr;
    socklen_t len;
    ssize_t result;
    struct timeval tv;

    result = recvfrom(fd, buf, sizeof(buf), 0, (struct sockaddr*)&src_addr, &len);
#if 0
    fprintf(stderr, "recv %zd from %s:%d", result, inet_ntoa(src_addr.sin_addr), ntohs(src_addr.sin_port));
    fprintf(stderr, " with mcast_channel %s:%d\n", inet_ntoa(state->mcast_ip), ntohs(state->mcast_port));
#endif

    if (result > 0) {
        gettimeofday(&tv, NULL);
        state->callback(buf, (int) result, state->arg, &tv, 0);
    }

    if (result == 0) {
        free_fd_state(state);
    } else if (result < 0) {
        if (errno == EAGAIN) // XXXX use evutil macro
        {
            return;
        }
        perror("recv");
        free_fd_state(state);
    }
}

static struct fd_state * alloc_fd_state(struct event_base *base, evutil_socket_t fd)
{
    struct fd_state *state = malloc(sizeof(struct fd_state));
    if (!state)
        return NULL;
    state->read_event = event_new(base, fd, EV_READ|EV_PERSIST, do_read, state);
    if (!state->read_event) {
        free(state);
        return NULL;
    }
    return state;
}



static int mcast_channel_fd_new(const char *str_name,
                                struct event_base *base,
                                struct in_addr mcast,
                                const char *str_mcast,
                                struct in_addr local,
                                const char *str_local,
                                u_int16_t mcast_port,
                                int int_mcast_port )
{
    evutil_socket_t nsock;
    struct sockaddr_in sin;
    int loop = 1;
    struct ip_mreq mreq;
    struct fd_state *state = NULL;

    mreq.imr_multiaddr = mcast;
    mreq.imr_interface = local;

    sin.sin_family = AF_INET;
    //sin.sin_addr.s_addr = inet_addr("192.168.56.126");
    sin.sin_addr.s_addr = 0;
    sin.sin_port = mcast_port;
    nsock = socket(AF_INET, SOCK_DGRAM, 0);
    evutil_make_socket_nonblocking(nsock);

    {
        int one = 1;
        setsockopt(nsock, SOL_SOCKET, SO_REUSEADDR, &one, sizeof(one));
    }

    if (bind(nsock, (struct sockaddr*)&sin, sizeof(sin)) < 0) {
        perror("bind");
        return -1;
    }
    if(setsockopt(nsock, IPPROTO_IP, IP_MULTICAST_LOOP, &loop, sizeof(loop)) < 0)
    {
        perror("setsocket():IP MULTICAST_LOOP");
        return -1;
    }

    if(setsockopt(nsock, IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq, sizeof(mreq)) < 0) {
        printf("%s setsockopt():IP ADD MEMBURSHIP\n",strerror(errno));
        return -1;
    }
    state = alloc_fd_state(base, nsock);
    if (state == NULL) {
        return 0;
    }
    state->mcast_ip = mreq.imr_multiaddr;
    state->mcast_port = mcast_port;
    // User defined data
    if (!strncmp(str_name, "TSE", 3)) {
        state->callback = stock_quote_unpacker;
    } else if (!strncmp(str_name, "OTC", 3)) {
        state->callback = stock_quote_unpacker;
    } else if (!strncmp(str_name, "FUT", 3)) {
        state->callback = future_quote_unpacker;
    } 
    state->arg = NULL;

    strcpy(state->str_name, str_name);
    strcpy(state->str_mcast, str_mcast);
    strcpy(state->str_local, str_local);
    state->int_mcast_port = int_mcast_port;
    event_add(state->read_event, NULL);
    return 0;
}


#include <linux/if_packet.h> // Add this include
#include <sys/socket.h>
#include <netinet/in.h>
#include <net/if.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <event2/event.h>
#include <event2/util.h>

// Handler for mirror mode packets
static void mirror_packet_handler(const unsigned char *data, unsigned int len, void *arg, const struct timeval *tv, int skip)
{
    if (len < sizeof(struct ether_header) + sizeof(struct ip)) {
        return; // Packet too small to contain headers
    }
    
    // Extract Ethernet header
    const struct ether_header *etherHeader = (struct ether_header *)data;
    
    // Check if this is an IP packet
    if (ntohs(etherHeader->ether_type) != ETHERTYPE_IP) {
        return; // Not an IP packet
    }
    
    // Extract IP header
    const struct ip *ipHeader = (struct ip *)(data + sizeof(struct ether_header));
    
    // Check if this is a UDP packet
    if (ipHeader->ip_p != IPPROTO_UDP) {
        return; // Not a UDP packet
    }
    
    // Extract UDP header
    const struct udphdr *udpHeader = (struct udphdr *)(data + sizeof(struct ether_header) + sizeof(struct ip));
    
    // Extract packet data after headers
    const unsigned char *payload = data + sizeof(struct ether_header) + sizeof(struct ip) + sizeof(struct udphdr);
    int payload_len = len - sizeof(struct ether_header) - sizeof(struct ip) - sizeof(struct udphdr);
    
    if (payload_len <= 0) {
        return; // No payload
    }
    
    // Get destination IP and port
    char dest_IP[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &(ipHeader->ip_dst), dest_IP, INET_ADDRSTRLEN);
    int dest_port = ntohs(udpHeader->uh_dport);

    if (0) {
        char source_IP[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &(ipHeader->ip_src), source_IP, INET_ADDRSTRLEN);
        int source_port = ntohs(udpHeader->uh_sport);
        printf("Mirror: %s:%d -> %s:%d len: %d\n", 
               source_IP, source_port, dest_IP, dest_port, payload_len);
        DumpHex(payload, payload_len);
    }

    stock_quote_unpacker(payload, payload_len, NULL, tv, 0);
    
}





void *thread_mirror_live_pcap_reader(void *interface_name)
{
    struct event_base *base = event_base_new();

    // Create raw socket to capture all packets
    evutil_socket_t nsock = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL));
    if (nsock < 0) {
        perror("socket(AF_PACKET)");
        return (void *)-1;
    }

    // Bind to the specified interface using sockaddr_ll
    struct sockaddr_ll sll;
    memset(&sll, 0, sizeof(sll));
    sll.sll_family = AF_PACKET;
    sll.sll_protocol = htons(ETH_P_ALL);
    sll.sll_ifindex = if_nametoindex(interface_name);
    if (sll.sll_ifindex == 0) {
        perror("if_nametoindex");
        close(nsock);
        return (void *)-1;
    }
    if (bind(nsock, (struct sockaddr*)&sll, sizeof(sll)) < 0) {
        perror("bind");
        close(nsock);
        return (void *)-1;
    }

    // Set socket options for performance
    int val = 1;
    if (setsockopt(nsock, SOL_SOCKET, SO_REUSEADDR, &val, sizeof(val)) < 0) {
        perror("setsockopt(SO_REUSEADDR)");
    }

    // Set receive buffer size
    int rcvbuf = 1024 * 1024 * 1024; // 16MB receive buffer
    if (setsockopt(nsock, SOL_SOCKET, SO_RCVBUF, &rcvbuf, sizeof(rcvbuf)) < 0) {
        perror("setsockopt(SO_RCVBUF)");
    }

    // Make the socket non-blocking
    evutil_make_socket_nonblocking(nsock);

    // Create a new fd_state for this socket
    struct fd_state *state = alloc_fd_state(base, nsock);
    if (state == NULL) {
        close(nsock);
        return (void *)-1;
    }

    // Set up the state
    strcpy(state->str_name, "mirror");
    strcpy(state->str_mcast, "raw_packet");
    strcpy(state->str_local, interface_name);
    state->int_mcast_port = 0;
    state->callback = mirror_packet_handler;
    state->arg = NULL;

    printf("Mirror mode enabled on interface: %s\n", (char *)interface_name);

    // Register the read event
    event_add(state->read_event, NULL);
    event_base_dispatch(base);
    return NULL;
}

void set_mirror_live_pcap_callback(callback_quote_t callback) {
    global_mirror_live_pcap_callback = callback;
}


void start_mirror_live_pcap_read(const char *str_mapping) {
    str_mapping = strdup(str_mapping);
    pthread_create(&thread, NULL, thread_mirror_live_pcap_reader, (void *)str_mapping);
}

void stop_mirror_live_pcap_read() {
    pthread_cancel(thread);
    pthread_join(thread, NULL);
}



void *thread_mc_live_pcap_reader(void *str_mapping)
{
    json_t *root;
    json_error_t error;
    struct event_base *base;
    struct in_addr mcast;
    struct in_addr local;

    base = event_base_new();
    if (!base) {
        printf("event_base_new error. Exit..\n");
        return NULL;
    }

    root = json_loads(str_mapping, 0, &error);
    if (!root) {
        fprintf(stderr, "Error parsing JSON: %s\n", error.text);
        return NULL;
    }

    if (!json_is_array(root)) {
        fprintf(stderr, "Error: root is not an array\n");
        json_decref(root);
        return NULL;
    }

    size_t index;
    json_t *value;
    json_array_foreach(root, index, value) {
        const char *description = json_string_value(json_object_get(value, "description"));
        const char *multicast_address = json_string_value(json_object_get(value, "multicast_address"));
        int port = json_integer_value(json_object_get(value, "port"));
        const char *interface = json_string_value(json_object_get(value, "interface"));

        mcast.s_addr = inet_addr(multicast_address);
        local.s_addr = inet_addr(interface);

        printf("Description: %s\n", description);
        printf("Multicast Address: %s\n", multicast_address);
        printf("Port: %d\n", port);
        printf("Interface: %s\n", interface);
        printf("\n");

        mcast_channel_fd_new(description, 
                             base, 
                             mcast, 
                             multicast_address, 
                             local, 
                             interface, 
                             htons(port), 
                             port);
    }
    json_decref(root);
    event_base_dispatch(base);
    return NULL;
}

void set_mc_live_pcap_callback(callback_quote_t callback) {
    global_mc_live_pcap_callback = callback;
}


void start_mc_live_pcap_read(const char *str_mapping) {
    printf("%s:%d %s\n", __FUNCTION__, __LINE__, str_mapping);
    str_mapping = strdup(str_mapping);
    pthread_create(&thread, NULL, thread_mc_live_pcap_reader, (void *)str_mapping);
}

void stop_mc_live_pcap_read() {
    pthread_cancel(thread);
    pthread_join(thread, NULL);
}

