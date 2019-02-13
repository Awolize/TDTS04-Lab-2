import socket
import sys
import _thread
import time
import os

     # print out the code 
     # print out the limitations
     # Use the host part instead of "url host" 
     # fix the loop, do not save everything in one varibale 
     # save in a buffer with a set size, like 20MB 
     # read from the client until /r/n/r/n, not needed for the hand in

BUFFER_SIZE = 1024
LISTEN_PORT = 8080
REDIRECT_URL = "https://www.ida.liu.se/~TDTS04/labs/2011/ass2/error1.html"
IP_ADDRESS = "127.0.0.1"
BAD_WORDS = ["spongebob" "norrköping", "paris hilton", "paris+hilton", "britney spears", "britney+spears"]


def Redirect(conn):
    print("302 Found")
    customRedirectPackage = "HTTP/1.1 302 Found\r\nLocation: " + REDIRECT_URL + "\r\n\r\n"
    conn.sendall(customRedirectPackage.encode())
    conn.close()

def Filter(data):
    for x in BAD_WORDS:
        if x in data:
            return {"success" : False, "message" : "Bad data"}
    return {"success" : True, "message" : "Good data"}

def ProxyConnection(conn, data):
    try:
        rawData = data
        decodedData = data.decode()
        print("Conn:" + str(conn))
        print("Data:" + decodedData)
        FilterResult = Filter(decodedData) # returns dictkeys(success, message)
        if FilterResult["success"]:
            print(FilterResult["message"])
            Redirect(conn)
        else:
            print(FilterResult["message"])
            Redirect(conn)
    except Exception as e:
        print("[E] proxyConnection")
        print(e)

# Main loop
def MainLoop(s):
    while 1:
        try:
            conn, addr = s.accept()
            data = conn.recv(BUFFER_SIZE)
            _thread.start_new_thread(ProxyConnection,(conn, data)) 
        except Exception as e:
            s.close()
            print("[E] mainLoop exception")
            print(e)
            sys.exit(-2)

if __name__ == "__main__":
    try:   
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((IP_ADDRESS, LISTEN_PORT))
        s.listen(1)
        print("[S] Successfully Started the Server [ %s:%d ]\n" % (IP_ADDRESS, LISTEN_PORT))
        print("[>] = Connection to: \n")
        MainLoop(s)
    except socket.error as e:
        s.close()
        print("\n[E] Unable to initialize Socket \n")
        print(e)
        sys.exit(-1)