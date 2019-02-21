import os
import sys
import threading
import socket

BACKLOG = 5
MAX_DATA_RECV = 4096
BAD_WORDS = ["spongebob", "britney spears", "paris hilton", "norrköping"] 
REDIRECT_URL_BAD_URL = "http://www.ida.liu.se/~TDTS04/labs/2011/ass2/error1.html"
REDIRECT_URL_BAD_CONTENT = "http://www.ida.liu.se/~TDTS04/labs/2011/ass2/error2.html"

# Search for censured words in a given string
def contains_bad_words(str):
    for word in BAD_WORDS:
        if(str.find(word) != -1):
            return True
    return False

# Initialize the proxy : create a socket and listen for connection.
#       Handle each connection in a new thread.
def proxy_init():

    ##### FEATURE 7 #####
    # check if port number was given in command line
    if (len(sys.argv) < 2):
        print ("No port given, using :8080 (http-alt)") 
        port = 8080
    else:
        port = int(sys.argv[1]) # port from argument
    
    host = '127.0.0.1' # get local machine name
    
    try:
        #create a socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        print("server on ", host, ": ", port)

        # associate socket to host and port
        s.bind((host, port))

        # wait for client connection
        s.listen(BACKLOG)

    except OSError as message:
        if s:
            s.close()
        print("Proxy socket problem", message)
        sys.exit(1)

    while True:
        # establish connection with client
        connection_socket, client_addr = s.accept()

        # create a thread to handle the request
        threading.Thread(target=proxy_server_side, args=(connection_socket, client_addr)).start()
    
    s.close()

# Server part of the proxy : forward the request to the client side of proxy and 
#       send the response back to the browser.
#       Or send 301 response to browser if censured words contained in url.  
def proxy_server_side(connection_socket, client_addr):

    ##### FEATURE 6 #####
    # get the request from browser
    request = connection_socket.recv(MAX_DATA_RECV)
    headers, sep, body = request.partition(b"\r\n\r\n")
    headers = headers.decode('utf-8')
    if (headers.find("GET") == -1):
        connection_socket.close()
        return
    #print(request)
    request = request.decode('utf-8')
    
    # get first line
    first_line = request.split("\n")[0]

    # get the absolute url
    if(len(first_line) == 0):
        print("first line empty")
        print("request: ", request)
        connection_socket.close()
        return
    url = first_line.split(" ")[1]
    
    print(client_addr, "\tRequest\t", first_line) 
    
    ##### FEATURE 3 #####
    # check url for censured words
    if(contains_bad_words(url.lower())):
        print("Censured words found in url : web redirection")
        response = "HTTP/1.1 301 Moved Permanently\r\nLocation: " + REDIRECT_URL_BAD_URL + "\r\n"
        connection_socket.sendall(response.encode())     
    
    else:
        # forward the request to the client side
        response = proxy_client_side(request)
        # send the response to the browser
        connection_socket.sendall(response)
        print("*** data delivered to browser ***\n")
    
    connection_socket.close()

# Client part of the proxy : Modify the request if needed.
#       Create a socket and connect to web server.
#       If needed, filter the data received from server.
#       Send the response back the server side.
def proxy_client_side(request):

    # get first line
    first_line = request.split("\n")[0]
    
    # get the absolute url
    url = first_line.split(" ")[1]

    # find webserver name
    webserver_begin_pos = url.find("://")
    webserver_end_pos = url.find("/",webserver_begin_pos+3)
    web_server_name = url[webserver_begin_pos+3:webserver_end_pos]
    
    port_server = 80

    # remove host information from the GET line
    if(url.find("://") != -1):
        first_line_end_pos = request.find("\n")
        temp = request[first_line_end_pos+1:]
        abs_path = url[webserver_end_pos:]
        first_line = first_line.split(" ")[0] + " " + abs_path + " " + first_line.split(" ")[2] + "\n"
        request = first_line + temp
        print("Request modification: ", first_line)

    try:
        # create a socket to connect to the web server
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2.connect((web_server_name, port_server))        
        s2.sendall(request.encode())
        
        # retrieve data
        all_data_encoded = data_received = s2.recv(MAX_DATA_RECV)
        
        ##### FEATURE 8 #####
        # check if content is text and not compressed
        isText = False
        headers, sep, body = all_data_encoded.partition(b"\r\n\r\n")
        headers = headers.decode('utf-8')
        if (headers.find("Content-Type: text") != -1):
            if(headers.find("Content-Encoding") == -1):
                isText = True

        # receive data from web server
        while(len(data_received) > 0):
            
            ##### FEATURE 4 #####
            # if the content needs to be filtered
            if(isText):
                # check for censured words in the newly received data 
                if(contains_bad_words(data_received.decode('utf-8').lower())):
                    print("Censured words found in content : web redirection")
                    response = "HTTP/1.1 301 Moved Permanently\r\nLocation: " + REDIRECT_URL_BAD_CONTENT + "\r\n"
                    s2.close()
                    return response.encode() 
            
            data_received = s2.recv(MAX_DATA_RECV)
            # add newly received data to the whole response
            all_data_encoded += data_received   

        s2.close()
        return all_data_encoded

    except OSError as error:
        if s2:
            s2.close()
        print("client side proxy problem", error)

if __name__ == "__main__":
    proxy_init()