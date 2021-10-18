import tkinter as tk
import socket
from time import sleep
import threading

window_main = tk.Tk()
window_main.title("Player")#this is the game window.
top_welcome_frame= tk.Frame(window_main)
lbl_name = tk.Label(top_welcome_frame, text = "Name:") #a box to take name input.
lbl_name.pack(side=tk.LEFT)
ent_name = tk.Entry(top_welcome_frame)
ent_name.pack(side=tk.LEFT)
btn_connect = tk.Button(top_welcome_frame, text="Connect", command=lambda : connect()) #this is to connect to the server.
btn_connect.pack(side=tk.LEFT)
top_welcome_frame.pack(side=tk.TOP)

top_frame = tk.Frame(window_main)


# network client
client = None
HOST_ADDR = "127.0.0.1"
HOST_PORT = 8432

tablelabels = []
num_cols = 3
your_turn = False
you_started = False

your_details = {
    "name": "Charles",
    "symbol": "X",
    "color" : "",
    "score" : 0
}

opponent_details = {
    "name": " ",
    "symbol": "O",
    "color": "",
    "score": 0
}

for x in range(3):
    for y in range(3):
        lbl = tk.Label(top_frame, text=" ", font="Helvetica 45 bold", height=2, width=5, highlightbackground="black",
                       highlightcolor="black", highlightthickness=1)
        lbl.bind("<Button-1>", lambda e, xy=[x, y]: Coordinates(xy))
        lbl.grid(row=x, column=y)

        dict_labels = {"xy": [x, y], "symbol": "", "label": lbl, "ticked": False}
        tablelabels.append(dict_labels)

lbl_status = tk.Label(top_frame, text="Not connected to server", font="Helvetica 14 bold")
lbl_status.grid(row=3, columnspan=3)

top_frame.pack_forget()


def init(arg0, arg1):
    global tablelabels, your_turn, your_details, opponent_details, you_started

    sleep(3)

    for i in range(len(tablelabels)):
        tablelabels[i]["symbol"] = ""
        tablelabels[i]["ticked"] = False
        tablelabels[i]["label"]["text"] = ""
        tablelabels[i]["label"].config(foreground="black", highlightbackground="grey",
                                       highlightcolor="grey", highlightthickness=1)

    lbl_status.config(foreground="black")
    lbl_status["text"] = "Game's starting."
    sleep(1)
    lbl_status["text"] = "Game's starting.."
    sleep(1)
    lbl_status["text"] = "Game's starting..."
    sleep(1)

    if you_started:
        you_started = False
        your_turn = False
        lbl_status["text"] = "STATUS: " + opponent_details["name"] + "'s turn!"
    else:
        you_started = True
        your_turn = True
        lbl_status["text"] = "STATUS: Your turn!"


def Coordinates(xy):
    global client, your_turn
    # convert 2D to 1D cordinate i.e. index = x * num_cols + y
    label_index = xy[0] * num_cols + xy[1]
    label = tablelabels[label_index]

    if your_turn:
        if label["ticked"] is False:
            label["label"].config(foreground=your_details["color"])
            label["label"]["text"] = your_details["symbol"]
            label["ticked"] = True
            label["symbol"] = your_details["symbol"]
            # send xy cordinate to server to give the turn to the other player.
            client.send(("$xy$" + str(xy[0]) + "$" + str(xy[1])).encode())
            your_turn = False

            # Does this play leads to a win or a draw
            result = game_logic()
            if result[0] is True and result[1] != "":  # a win
                your_details["score"] = your_details["score"] + 1
                lbl_status["text"] = "Game over, You won! You(" + str(your_details["score"]) + ") - " \
                    "" + opponent_details["name"] + "(" + str(opponent_details["score"])+")"
                lbl_status.config(foreground="green")
                threading._start_new_thread(init, ("", ""))

            elif result[0] is True and result[1] == "":  # a draw
                lbl_status["text"] = "Game over, Draw! You(" + str(your_details["score"]) + ") - " \
                    "" + opponent_details["name"] + "(" + str(opponent_details["score"]) + ")"
                lbl_status.config(foreground="blue")
                threading._start_new_thread(init, ("", ""))

            else:
                lbl_status["text"] = "STATUS: " + opponent_details["name"] + "'s turn!"
    else:
        lbl_status["text"] = "STATUS: Wait for your turn!"
        lbl_status.config(foreground="red")

        # send xy coordinate to server to server


# [(0,0) -> (0,1) -> (0,2)], [(1,0) -> (1,1) -> (1,2)], [(2,0), (2,1), (2,2)]
def check_row():
    list_symbols = []
    tablelabels_temp = []
    winner = False
    win_symbol = ""
    for i in range(len(tablelabels)):
        list_symbols.append(tablelabels[i]["symbol"])
        tablelabels_temp.append(tablelabels[i])
        if (i + 1) % 3 == 0:
            if (list_symbols[0] == list_symbols[1] == list_symbols[2]):
                if list_symbols[0] != "":
                    winner = True
                    win_symbol = list_symbols[0]

                    tablelabels_temp[0]["label"].config(foreground="green", highlightbackground="green",
                                                        highlightcolor="green", highlightthickness=2)
                    tablelabels_temp[1]["label"].config(foreground="green", highlightbackground="green",
                                                        highlightcolor="green", highlightthickness=2)
                    tablelabels_temp[2]["label"].config(foreground="green", highlightbackground="green",
                                                        highlightcolor="green", highlightthickness=2)

            list_symbols = []
            tablelabels_temp = []

    return [winner, win_symbol]


#check for diagonal , column wise, row wise
def columncheck():
    winner = False
    win_symbol = ""
    for i in range(num_cols):
        if tablelabels[i]["symbol"] == tablelabels[i + num_cols]["symbol"] == tablelabels[i + num_cols + num_cols][
            "symbol"]:
            if tablelabels[i]["symbol"] != "":
                winner = True
                win_symbol = tablelabels[i]["symbol"]

                tablelabels[i]["label"].config(foreground="green", highlightbackground="green",
                                               highlightcolor="green", highlightthickness=2)
                tablelabels[i + num_cols]["label"].config(foreground="green", highlightbackground="green",
                                                          highlightcolor="green", highlightthickness=2)
                tablelabels[i + num_cols + num_cols]["label"].config(foreground="green", highlightbackground="green",
                                                                     highlightcolor="green", highlightthickness=2)

    return [winner, win_symbol]


def diagonalcheck():
    winner = False
    win_symbol = ""
    i = 0
    j = 2

    # top-left to bottom-right diagonal check
    a = tablelabels[i]["symbol"]
    b = tablelabels[i + (num_cols + 1)]["symbol"]
    c = tablelabels[(num_cols + num_cols) + (i + 1)]["symbol"]
    if tablelabels[i]["symbol"] == tablelabels[i + (num_cols + 1)]["symbol"] == \
            tablelabels[(num_cols + num_cols) + (i + 2)]["symbol"]:
        if tablelabels[i]["symbol"] != "":
            winner = True
            win_symbol = tablelabels[i]["symbol"]

            tablelabels[i]["label"].config(foreground="green", highlightbackground="green",
                                           highlightcolor="green", highlightthickness=2)

            tablelabels[i + (num_cols + 1)]["label"].config(foreground="green", highlightbackground="green",
                                                            highlightcolor="green", highlightthickness=2)
            tablelabels[(num_cols + num_cols) + (i + 2)]["label"].config(foreground="green",
                                                                         highlightbackground="green",
                                                                         highlightcolor="green", highlightthickness=2)

    # top-right to bottom-left diagonal
    elif tablelabels[j]["symbol"] == tablelabels[j + (num_cols - 1)]["symbol"] == tablelabels[j + (num_cols + 1)][
        "symbol"]:
        if tablelabels[j]["symbol"] != "":
            winner = True
            win_symbol = tablelabels[j]["symbol"]

            tablelabels[j]["label"].config(foreground="green", highlightbackground="green",
                                           highlightcolor="green", highlightthickness=2)
            tablelabels[j + (num_cols - 1)]["label"].config(foreground="green", highlightbackground="green",
                                                            highlightcolor="green", highlightthickness=2)
            tablelabels[j + (num_cols + 1)]["label"].config(foreground="green", highlightbackground="green",
                                                            highlightcolor="green", highlightthickness=2)
    else:
        winner = False

    return [winner, win_symbol]


# it's a draw if grid is filled
def checkForDraw():
    for i in range(len(tablelabels)):
        if tablelabels[i]["ticked"] is False:
            return [False, ""]
    return [True, ""]


def game_logic():
    result = check_row()
    if result[0]:
        return result

    result = columncheck()
    if result[0]:
        return result

    result = diagonalcheck()
    if result[0]:
        return result

    result = checkForDraw()
    return result


def connect():
    global your_details
    if len(ent_name.get()) < 1:  #if name is empty
        tk.messagebox.showerror(title="ERROR!!!", message="You MUST enter your first name <e.g. John>")
    else:
        your_details["name"] = ent_name.get()
        Connect_to_the_server(ent_name.get())


def Connect_to_the_server(name):
    global client, HOST_PORT, HOST_ADDR
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST_ADDR, HOST_PORT))
        client.send(name.encode())  # Send name to server after connecting
        # start a thread to keep receiving message from server
        # do not block the main thread :)
        threading._start_new_thread(receive_message_from_server, (client, "m"))
        top_welcome_frame.pack_forget()
        top_frame.pack(side=tk.TOP)
        window_main.title("Player - " + name)
    except Exception as e:
        tk.messagebox.showerror(title="ERROR!!", message="Cannot connect to host: " + HOST_ADDR + " on port: " + str(
            HOST_PORT) + " Server may be Unavailable. Try again later")


def receive_message_from_server(sock, m):
    global your_details, opponent_details, your_turn, you_started
    while True:
        from_server = sock.recv(4096).decode()

        if not from_server: break

        if from_server.startswith("welcome"):
            if from_server == "welcome1":
                your_details["color"] = "blue"
                opponent_details["color"] = "red"
                lbl_status["text"] = "Server: Welcome " + your_details["name"] + "! Waiting for player 2"
            elif from_server == "welcome2":
                lbl_status["text"] = "Server: Welcome " + your_details["name"] + "! Game will start soon"
                your_details["color"] = "red"
                opponent_details["color"] = "blue"

        elif from_server.startswith("opponent_name$"):
            temp = from_server.replace("opponent_name$", "")
            temp = temp.replace("symbol", "")
            name_index = temp.find("$")
            symbol_index = temp.rfind("$")
            opponent_details["name"] = temp[0:name_index]
            your_details["symbol"] = temp[symbol_index:len(temp)]

            # set opponent symbol
            if your_details["symbol"] == "O":
                opponent_details["symbol"] = "X"
            else:
                opponent_details["symbol"] = "O"

            lbl_status["text"] = "STATUS: " + opponent_details["name"] + " is connected!"
            sleep(3)
            # is it your turn to play? hey! 'O' comes before 'X'
            if your_details["symbol"] == "O":
                lbl_status["text"] = "STATUS: Your turn!"
                your_turn = True
                you_started = True
            else:
                lbl_status["text"] = "STATUS: " + opponent_details["name"] + "'s turn!"
                you_started = False
                your_turn = False
        elif from_server.startswith("$xy$"):
            temp = from_server.replace("$xy$", "")
            _x = temp[0:temp.find("$")]
            _y = temp[temp.find("$") + 1:len(temp)]

            # update board
            label_index = int(_x) * num_cols + int(_y)
            label = tablelabels[label_index]
            label["symbol"] = opponent_details["symbol"]
            label["label"]["text"] = opponent_details["symbol"]
            label["label"].config(foreground=opponent_details["color"])
            label["ticked"] = True

            # Does this cordinate leads to a win or a draw
            result = game_logic()
            if result[0] is True and result[1] != "":  # opponent win
                opponent_details["score"] = opponent_details["score"] + 1
                if result[1] == opponent_details["symbol"]:  #
                    lbl_status["text"] = "Sorry, You Lost! You(" + str(your_details["score"]) + ") - " \
                        "" + opponent_details["name"] + "(" + str(opponent_details["score"]) + ")"
                    lbl_status.config(foreground="red")
                    threading._start_new_thread(init, ("", ""))
            elif result[0] is True and result[1] == "":  # a draw
                lbl_status["text"] = "Its a Draw! You(" + str(your_details["score"]) + ") - " \
                    "" + opponent_details["name"] + "(" + str(opponent_details["score"]) + ")"
                lbl_status.config(foreground="blue")
                threading._start_new_thread(init, ("", ""))
            else:
                your_turn = True
                lbl_status["text"] = "STATUS: Your turn!"
                lbl_status.config(foreground="black")

    sock.close()


window_main.mainloop()