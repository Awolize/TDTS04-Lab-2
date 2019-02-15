import socket
import sys
import _thread
import time
import os
import requests

     # print out the code 
     # print out the limitations
     # Use the host part instead of "url host" 
     # fix the loop, do not save everything in one varibale 
     # save in a buffer with a set size, like 20MB 
     # read from the client until /r/n/r/n, not needed for the hand in

BUFFER_SIZE = 1024
LISTEN_PORT = 8080
REDIRECT_URL_ERROR1 = "https://www.ida.liu.se/~TDTS04/labs/2011/ass2/error1.html"
REDIRECT_URL_ERROR2 = "https://www.ida.liu.se/~TDTS04/labs/2011/ass2/error2.html"
IP_ADDRESS = "127.0.0.1"
BAD_WORDS = ["spongebob" "norrköping", "paris hilton", "paris+hilton", "britney spears", "britney+spears"]

def SendReceive(conn, data):
    try: 
        url = data.split("\n")[0].split(" ")[1]
        hostStartPos = url.find("://")
        hostEndPos = url.find("/", hostStartPos + 3)
        host = url[hostStartPos+3:hostEndPos]

        print("[>] %s" % host)

        r = requests.get(url)
        '''
        webSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        webSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        webSocket.connect((host, 80))
        webSocket.sendall(data.encode())
        '''

        data = r.text

        '''
        while 1:
            ReceivedData = webSocket.recv(BUFFER_SIZE)
            if not ReceivedData:
                break
            rawData += ReceivedData
            strData = rawData.decode("utf-8")
            #strData = str(rawData)
            filterAnswer = Filter(strData.lower())
            if filterAnswer["success"] == False:
                print(filterAnswer["message"])
                Redirect(conn, 2)
                webSocket.close()
                return

        webSocket.close()
        '''

        print(r.headers['Content-Length'])
        if r.headers['Content-Type'] == "text/html" and r.headers['Content-Length'] < 20000000:
            filterAnswer = Filter(data.lower())
            if filterAnswer["success"] == False:
                print(filterAnswer["message"])
                Redirect(conn, 2)
                return

        conn.sendall(r.content)
    except Exception as e:
        print("[E] SendReceive")
        print(e)

def Redirect(conn, url=1):
    print("301 Moved Permanently")
    if url == 1:
        customRedirectPackage = "HTTP/1.1 301 Moved Permanently\r\nLocation: " + REDIRECT_URL_ERROR1 + "\r\n\r\n"
    else:
        customRedirectPackage = "HTTP/1.1 301 Moved Permanently\r\nLocation: " + REDIRECT_URL_ERROR2 + "\r\n\r\n"

    conn.sendall(customRedirectPackage.encode())
    conn.close()

def Filter(data):
    for word in BAD_WORDS:
        if word in data:
            return {"success" : False, "message" : "Bad data"}
    return {"success" : True, "message" : "Good data"}

def ProxyConnection(conn, data):
    try:
        decodedData = data.decode()
        FilterResult = Filter(decodedData.lower()) # returns dictkeys(success, message)
        if FilterResult["success"]:
            SendReceive(conn, decodedData)
        else:
            Redirect(conn, 1)
    except Exception as e:
        print("[E] proxyConnection")
        print(e)

# Main loop
def MainLoop(s):
    while 1:
        try:
            conn, addr = s.accept()
            data = conn.recv(BUFFER_SIZE)
            #ProxyConnection(conn, data)
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
    except Exception as e:
        s.close()
        print("\n[E] Unable to initialize Socket \n")
        print(e)
        sys.exit(-1)