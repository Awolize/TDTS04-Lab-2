import socket
import sys
import _thread
import time
import os

     # print out the code
     # print out the limitations
     # Use the host part instead of "url host" 
     # fix the loop, do not save everything in one varibale // fixed
     # save in a buffer with a set size, like 20MB // fixed
     # read from the client until /r/n/r/n, not needed for the hand in

bufferSize = 1024
listenPort = 8080
ipAddress = "127.0.0.1"

class ConnectionData:
    rawData = b""
    strData = ""
    host = ""
    ifRelocate = False

    def __init__(self, conn, data):
        try:
            self.conn = conn
            self.rawData = data
            self.strData = data.decode("utf-8")
            
            #Search for the Host address
            pos = self.strData.find("Host:")
            self.host = self.strData[(pos + 6):]
            pos = self.host.find('\r')
            self.host = self.host[:(pos)]

            pos = self.strData.find("Connection: ")
            bconn = self.strData[:(pos)]
            aconn = self.strData[(pos):]
            pos = aconn.find("\r")
            aconn = aconn[(pos):]
            self.strData = bconn + "Connection: close" + aconn
            self.rawData = self.strData.encode()

            # Search for words in the URL:
            if ((self.strData.lower().find("spongebob") != -1) or (self.strData.lower().find("norrköping") != -1) or (self.strData.lower().find("paris hilton") != -1) or (self.strData.lower().find("paris+hilton") != -1) or (self.strData.lower().find("britney spears") != -1) or (self.strData.lower().find("britney+spears") != -1) or (self.strData.lower().find("norrk%c3%b6ping") != -1)):
                self.ifRelocate = True

        except Exception as e:
            print(e)
            self.conn.close()
            s.close()
            print("Proxy was interrupted by user.")
            sys.exit()

    def Redirect(self):
        print("302 Found")
        relocate = "HTTP/1.1 302 Found\r\nLocation: http://www.ida.liu.se/~TDTS04/labs/2011/ass2/error1.html\r\n\r\n"
        self.conn.sendall(relocate.encode())
        self.conn.close()

    def SendnRecieve(self):
        try:
            print("[>] %s" % self.host)
            webSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            webSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            webSocket.connect((self.host, 80))
            webSocket.sendall(self.rawData)

            ifText = False
            ifLarge = False
            strData = ""
            rawData = webSocket.recv(bufferSize)

            while (str(rawData).find("\\r\\n\\r\\n") == -1):
                rawData += webSocket.recv(bufferSize)
                if (len(rawData) > 20000000): # 20 mb
                    print("Header file len: " + str(len(rawData)) + "\nClosing the connection!\n")
                    s.close()
                    self.conn.close()
                    webSocket.close()
                    break

            header = str(rawData).split("\\r\\n\\r\\n")[0]
            if (header.find("Content-Type: text") != -1):
                ifText = True
            
            #rawData
            while 1:
                data = webSocket.recv(bufferSize)
                if not data:
                    break
                rawData += data
                strData = str(rawData)
                if (len(rawData) > 20000000): # 20 mb
                    self.conn.sendall(rawData)
                    ifLarge = True
                    break
                elif (((strData.lower().find("spongebob") != -1) or (strData.lower().find("norrköping") != -1) or (strData.lower().find("paris hilton") != -1) or (strData.lower().find("paris+hilton") != -1) or (strData.lower().find("britney spears") != -1) or (strData.lower().find("britney+spears") != -1))):
                    print("302 Found")
                    relocate = "HTTP/1.1 302 Found\r\nLocation: http://www.ida.liu.se/~TDTS04/labs/2011/ass2/error2.html\r\n\r\n"
                    webSocket.close()
                    self.conn.sendall(relocate.encode())
                    break
                    
            if (ifLarge):
                while rawData:
                    rawData = webSocket.recv(bufferSize)
                    self.conn.sendall(rawData)
            else:
                self.conn.sendall(rawData)

                
            webSocket.close()
            self.conn.close() 
          
        except socket.error as e:
            print(e)
            webSocket.close()
            self.conn.close()
        except Exception as e:
            print(e)
            webSocket.close()
            self.conn.close()
            s.close()
            sys.exit()

def proxyServer(conn, data):  
    try:
        connectionInfo = ConnectionData(conn, data)
        if (connectionInfo.ifRelocate):
            connectionInfo.Redirect();
        else:
            connectionInfo.SendnRecieve()
    except:
        pass

def mainLoop():
    while 1:
        try: 
            conn, addr = s.accept()
            data = conn.recv(bufferSize)
            _thread.start_new_thread(proxyServer,(conn, data)) 
        except:
            conn.close()
            s.close()
            print("Proxy was interrupted. (Error mainLoop)")
            sys.exit()

try:   
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((ipAddress, listenPort))
    s.listen(1)
    print("[S] Successfully Started the Server [ %s:%d ]\n" % (ipAddress, listenPort))
    print("[>] = Connection to: \n")
    mainLoop()
    sys.exit()
except:
    s.close()
    print("\n[x] Unable to initialize Socket \n")
    sys.exit()
