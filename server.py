#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    ENCODE = 'utf-8'
    STATUS_200 = "HTTP/1.1 200 OK\r\nContent-Type: text/%s; charset=utf-8\r\n\r\n"
    STATUS_301 = "HTTP/1.1 301 Moved Permanently\n"
    STATUS_404 = "HTTP/1.1 404 Not Found\r\n"
    STATUS_405 = "HTTP/1.1 405 Method Not Allowed\r\n\r\n"

    def handle(self):

        # decode the request 
        self.data = self.request.recv(1024).decode(self.ENCODE)

        try:

            # extracts the requested method and path by the user
            method_requested = self.data.splitlines()[0].split()[0]
            path_requested = self.data.splitlines()[0].split()[1]


            # only GET is allowed
            if not self.valid_method(method_requested):
                self.request.sendall(self.STATUS_405.encode())
                return

            # checks for valid path
            elif not self.valid_path(path_requested):
                self.request.sendall(bytearray(self.STATUS_404, self.ENCODE))
                return

            try:
                if os.path.isdir("www" + path_requested):

                    self.check_path_request(path_requested)

                # the path entered is not found and is invalid
                elif not os.path.isfile("www" + path_requested):
                    # File not found error message or NOT FOUND error
                    self.request.sendall(bytearray(self.STATUS_404, self.ENCODE))
                    return
                
                else:
                    # the correct path entered
                    path_requested = "www" + path_requested
                    with open(path_requested, "r") as file:
                            self.request.sendall(bytearray(self.STATUS_200%(path_requested.split(".")[1])+file.read(), self.ENCODE))

            except: 
                self.request.sendall(bytearray(self.STATUS_404, self.ENCODE)) # File not found error message or NOT FOUND error  
                return
            
        # File not found error message or NOT FOUND error
        except:
            self.request.sendall(bytearray(self.STATUS_404, self.ENCODE)) 
            return


    def valid_method(self, method):

        # checks if the correct method is requested or not
        # takes the method as an argument 
        # Returns True is the correct method is requested else returns False

        if (method == "GET"):
            return True
        
        return False

    def valid_path (self, path_req):
        # checks if the correct path is requested or not
        # takes the requested path  as an argument 
        # Returns True is the correct path is requested else returns False

        if "/../" not in path_req:
            return True

        return False

    def check_path_request(self, path_req):
        #checks the requested path by the user 

        # the default path syntax
        if path_req.endswith("/"):
            path_req += "index.html"
            path_req = "www" + path_req #serves files from "./www."
                    
            # opens the file and reads it's content
            with open(path_req, "r") as file:
                self.request.sendall(bytearray(self.STATUS_200%(path_req.split(".")[1])+file.read(), self.ENCODE))

        else:
            self.request.sendall(bytearray(self.STATUS_301, self.ENCODE)) # accepts the file path entered but shows 301 error


        
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
