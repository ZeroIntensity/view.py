#ifdef _WIN32
#include <winsock2.h>
#include <Ws2tcpip.h>
#else
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <unistd.h>
#endif

int init_sock(void) {
    #ifdef _WIN32
    WSADATA wsa_data;
    return WSAStartup(
        MAKEWORD(
            1,
            1
        ),
        &wsa_data
    );
    #else
    return 0;
    #endif
}

int quit_sock(void) {
    #ifdef _WIN32
    return WSACleanup();
    #else
    return 0;
    #endif
}
