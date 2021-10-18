import tkinter as tk
import socket
import threading
from time import sleep


window = tk.Tk()
window.title("Server")

# Top frame consisting of two buttons widgets (i.e. startbutton, stopbutton)
topFrame = tk.Frame(window)
startbutton = tk.Button(topFrame, text="Start Game", command=lambda : start_server())
startbutton.pack(side=tk.LEFT)
stopbutton = tk.Button(topFrame, text="Stop Game", command=lambda : stop_server(), state=tk.DISABLED)
stopbutton.pack(side=tk.LEFT)
topFrame.pack(side=tk.TOP, pady=(5, 0))

# frame to dispay the ip address and port number.
middleFrame = tk.Frame(window)
lblHost = tk.Label(middleFrame, text = "Address: X.X.X.X")
lblHost.pack(side=tk.LEFT)
lblPort = tk.Label(middleFrame, text = "Port:XXXX")
lblPort.pack(side=tk.LEFT)
middleFrame.pack(side=tk.TOP, pady=(5, 0))


clientFrame = tk.Frame(window) #details about the client
lblLine = tk.Label(clientFrame, text="Players").pack()
scrollBar = tk.Scrollbar(clientFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(clientFrame, height=10, width=30)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="black", state="disabled")
clientFrame.pack(side=tk.BOTTOM, pady=(5, 10))


server = None
HOST_ADDR = "127.0.0.1"
HOST_PORT = 8432
client_name = " "
clients = []  #to store client connection objects
clientNames = []
data_of_players = []


# Start server function
def start_server():
    global server, HOST_ADDR, HOST_PORT 
    startbutton.config(state=tk.DISABLED)
    stopbutton.config(state=tk.NORMAL)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   
    server.bind((HOST_ADDR, HOST_PORT))
    server.listen(5)  # server is listening for client connection
    print("Server started")

    threading._start_new_thread(accept_requests, (server, " "))

    lblHost["text"] = "Address: " + HOST_ADDR
    lblPort["text"] = "Port: " + str(HOST_PORT)


# Stop server function
def stop_server():
    global server
    startbutton.config(state=tk.NORMAL)
    stopbutton.config(state=tk.DISABLED)


def accept_requests(the_server, y):
    while True:
        if len(clients) < 2:
            client, addr = the_server.accept()
            clients.append(client)

            # use a thread so as not to clog the gui thread
            threading._start_new_thread(send_receive_client_message, (client, addr))


# Function to receive message from current client AND
# Send that message to other clients
def send_receive_client_message(client_connection, client_ip_addr):
    global server, client_name, clients, data_of_players, player0, player1

    client_msg = " "

    # send welcome message to client
    client_name = client_connection.recv(4096).decode()

    if len(clients) < 2:
        client_connection.send("welcome1".encode())
    else:
        client_connection.send("welcome2".encode())

    clientNames.append(client_name)
    update_display(clientNames)  # update client names display

    if len(clients) > 1:
        sleep(1)
        symbols = ["O", "X"]

        # send opponent name and symbol
        clients[0].send(("opponent_name$" + clientNames[1] + "symbol" + symbols[0]).encode())
        clients[1].send(("opponent_name$" + clientNames[0] + "symbol" + symbols[1]).encode())


    while True:

        # get the player choice from received data
        data = client_connection.recv(4096).decode()
        if not data: break

        # player x,y coordinate data. forward to the other player
        if data.startswith("$xy$"):
            # is the message from client1 or client2?
            if client_connection == clients[0]:
                # send the data from this player (client) to the other player (client)
                clients[1].send(data.encode())
            else:
                # send the data from one client to the other. 
                clients[0].send(data.encode())

    idx = index_of_client(clients, client_connection)
    del clientNames[idx]
    del clients[idx]
    client_connection.close()

    update_display(clientNames)  # update client names display


# Return the index of the current client in the list of clients
def update_display(name_list):
    tkDisplay.config(state=tk.NORMAL)
    tkDisplay.delete('1.0', tk.END)

    for c in name_list:
        tkDisplay.insert(tk.END, c+"\n")
    tkDisplay.config(state=tk.DISABLED)

def index_of_client(client_list, curr_client):
    idx = 0
    for conn in client_list:
        if conn == curr_client:
            break
        idx = idx + 1

    return idx


window.mainloop()