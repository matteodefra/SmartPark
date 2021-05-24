from server import CoAPServer, registeredUsersDict

# Unspecified IPv6 address
ip = "::"
port = 5683

def main():
    registeredUsersDict["mat"] = "mat"
    registeredUsersDict["nick"] = "nick"
    registeredUsersDict["marc"] = "marc"
    print("Initializing server")
    server = CoAPServer(ip, port)
    try:
        server.listen(100)
    except KeyboardInterrupt:
        print("Server Shutdown")
        server.close()
        print("Exiting...")

if __name__ == '__main__':
    main()
