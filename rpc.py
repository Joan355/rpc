# Needed imports
import json
import socket
import inspect
from threading import Thread
SIZE = 2048
# rpc.py
class RPCServer:
    def __init__(self, host:str='127.0.0.1', port:int=8080) -> None:
        self.host = host
        self.port = port
        self.address = (host, port)
        self._methods = {}
        


    # Within RPCServer
    def registerMethod(self, function) -> None:
        try:
            self._methods.update({function.__name__ : function})
        except:
            raise Exception('A non function object has been passed into RPCServer.registerMethod(self, function)')
        
    
    
    # Withing RPCServer
    def __handle__(self, client:socket.socket, address:tuple) -> None:
        print(f'Managing requests from {address}.')
        while True:
            try:
                functionName, args, kwargs = json.loads(client.recv(SIZE).decode())
            except: 
                print(f'! Client {address} disconnected.')
                break
            # Showing request Type
            print(f'> {address} : {functionName}({args})')

            try:
                response = self._methods[functionName](*args, **kwargs)
            except Exception as e:
                # Send back exeption if function called by client is not registred 
                client.sendall(json.dumps(str(e)).encode())
            else:
                client.sendall(json.dumps(response).encode())

        print(f'Completed requests from {address}.')
        client.close()

     # within RPCServer
    def run(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(self.address)
            sock.listen()

            print(f'+ Server {self.address} running')
            while True:
                try:
                    client, address = sock.accept()

                    Thread(target=self.__handle__, args=[client, address]).start()

                except KeyboardInterrupt:
                    print(f'- Server {self.address} interrupted')
                    break



class RPCClient:
    def __init__(self, host:str='localhost', port:int=8080) -> None:
        self.__sock = None
        self.__address = (host, port)

     # Within RPCClient
    def connect(self):
        try:
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__sock.connect(self.__address)
        except EOFError as e:
            print(e)
            raise Exception('Client was not able to connect.')
    
    def disconnect(self):
        try:
            self.__sock.close()
        except:
            pass

     # Within RPCClient
    def __getattr__(self, __name: str):
        def excecute(*args, **kwargs):
            self.__sock.sendall(json.dumps((__name, args, kwargs)).encode())

            response = json.loads(self.__sock.recv(SIZE).decode())
   
            return response
        
        return excecute