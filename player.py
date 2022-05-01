"""
Envía mensajes a un canal (clients/flota/jugador/...).
Recibe mensajes de un canal (clients/flota/sala/...).
"""

from operator import truediv
from paho.mqtt.client import Client
import paho.mqtt.publish as publish
from tkinter import *
import random
import traceback

ANCHO = 10
ALTO = 10
BARCOS = 10


class Player():
    def __init__(self, name):
        self.name = name
        self.board = Board()

    def __str__(self):
        return self.name

class Board():
    def __init__(self):
        self.ancho = ANCHO
        self.alto = ALTO
        self.barcos = self.first_board()  # 0 agua, 1 barco
        self.estado = [[0 for i in range(self.ancho)] for j in range(self.alto)]  # 0 nada, 1 disparado
    
    def first_board(self):
        posinit = sorted(random.sample(range(self.ancho*self.alto), BARCOS))
        tabinit = [[0 for i in range(self.ancho)] for j in range(self.alto)]
        for i in posinit:
            tabinit[i//self.ancho][i % self.ancho] = 1
        return tabinit

    def barcos_to_string(self):
        pos=' '
        for i in range(len(self.barcos)):
            for j in range(len(self.barcos[i])):
                if self.barcos[i][j] == 1:
                    pos += str(i) + ',' + str(j) + ' '
        return pos

    def __str__(self):
        mostrar = ''
        for i in range(len(self.barcos)):
            for j in self.barcos[i]:
                mostrar += '|' + str(j)
            mostrar += '|\n'

        return mostrar

def jugada(mqttc, name):
    # finished = False
    # while not finished:
    print('Donde quieres atacar:')
    fila = input('Fila: ')
    columna = input('Columna: ')
    # mqttc.publish(f'clients/flota/jugador/{name}', 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
    mqttc.publish(f'clients/flota/jugador/{name}', f'{name} {fila} {columna}')

def create_interface(mqttc, player):
    root = Tk() # Ventana Principal
    root.title("Silk the float") # Título
    root.resizable(0,0) # (0,0) = No se puede ampliar, (1,1) = sí

    # TítuloS
    headboard = Label(root, text = "Bienvenid@ a Hundir la Flota")
    headboard.grid (row = 0, column = 0, columnspan = 2*ANCHO + 4)
    headboard.config(fg = "blue",    # Foreground (Color delante)
                        bg = "grey",    # Background (Color detrás)
                        font = ("Verdana", 10)
                    )
    
    headboard = Label(root)
    headboard.grid (row = 1, column = 0, columnspan = 1)
    headboard.config(fg = "white",  
                     bg = "white" 
                    )

    headboard = Label(root, text = "Tablero del rival")
    headboard.grid (row = 2, column = 1, columnspan = 3)
    headboard.config(fg = "blue",    # Foreground (Color delante)
                        bg = "grey",    # Background (Color detrás)
                        font = ("Verdana", 10)
                    )

    headboard = Label(root, text = "Tu tablero")
    headboard.grid (row = 2, column = ANCHO + 3, columnspan = 3)
    headboard.config(fg = "blue",    # Foreground (Color delante)
                        bg = "grey",    # Background (Color detrás)
                        font = ("Verdana", 10)
                    )
    
    # Tablero rival
    for i in range(5, ALTO + 5):
        for j in range(1, ANCHO + 1):
            button = Button(root,
                                background = "grey",
                                foreground = "black",
                                bd = 3, # Borde
                                padx = "17",
                                pady = "5",
                                font = ("Verdana", 8),
                                width = "1",
                                relief = RAISED,
                                )
            button.bind("<Button-1>", lambda e, row=i-4, column=j: clickBot((row,column), e, mqttc, player))
            button ["text"] = str(i - 4), ',' , str(j)     # En cada casilla hay escrita su coordenada
            button.grid(row = i, column = j)       # Para organizar todas las casillas
            labColumn1 = Label(root, text = "Col: " + str(j))      # Etiqueta de COLUMNAS
            labColumn1.grid(row = ALTO + 5, column = (j))
        labRow1 = Label(root, text = "Fila: " + str(i - 1))        # Etiqueta de FILAS
        labRow1.grid(row = (i), column = (j + 1))

    # Tablero propio
    for i in range(5, ALTO + 5):
        for j in range(ANCHO + 4, 2*ANCHO + 4):
            button = Button(root,
                                background = "#00FFFF" if player.board.barcos[i-5][j-(ANCHO+4)] == 0 else "grey",
                                foreground = "black",
                                bd = 3, # Borde
                                padx = "17",
                                pady = "5",
                                font = ("Verdana", 8),
                                width = "1",
                                relief = RAISED,
                                state = DISABLED
                                )
            button ["text"] = str(i - 4), ',' , str(j-(ANCHO+3))     # En cada casilla hay escrita su coordenada
            button.grid(row = i, column = j)       # Para organizar todas las casillas
            labColumn1 = Label(root, text = "Col: " + str(j))      # Etiqueta de COLUMNAS
            labColumn1.grid(row = ALTO + 5, column = (j))

    mqttc.root = root
    mqttc.loop_start()
    mqttc.root.mainloop()

def clickBot (pos, event, mqttc, player):
    mqttc.publish(f'clients/flota/jugador/{player.name}', player.name + ' ' + str(pos[0]-1) + ' ' + str(pos[1]-1))

    if event.widget["bg"] == "grey": # cuidao, si es agua, azul, si es tocado, rojo

        # (No se queda el mismo color) messagebox.showerror("Hundir La Flota", "Ahí ya cayó un misil")
        event.widget["bg"] = "#00FFFF"
        #button.state = DISABLED
    else:
        pass    

def change_btn_color(mqttc, num, fila, columna):
    print('asdfasdfasdfa')
    button = Button(mqttc.root,
                        background = "#77DD77" if num == 0 else "#FF6961",
                        foreground = "black",
                        bd = 3, # Borde
                        padx = "17",
                        pady = "5",
                        font = ("Verdana", 8),
                        width = "1",
                        relief = RAISED,
                        state = DISABLED
                    )
    button ["text"] = str(fila), ',' , str(columna)    # En cada casilla hay escrita su coordenada
    button.grid(row = fila + 4, column = columna)

def put_x(mqttc, player, fila, columna):
    print('asdfasdfasdfa')
    button = Button(mqttc.root,
                        background = "#77DD77" if player.board.barcos[fila-1][columna-1] == 0 else "#FF6961",
                        foreground = "black",
                        bd = 3, # Borde
                        padx = "17",
                        pady = "5",
                        font = ("Verdana", 8),
                        width = "1",
                        relief = RAISED,
                        state = DISABLED
                    )
    button ["text"] = str(fila), ',' , str(columna)    # En cada casilla hay escrita su coordenada
    button.grid(row = fila + 4, column = columna + ANCHO + 3) 

def on_connect(mqttc, userdata, flags, rc):
    try:
        print("CONNECT:", userdata, flags, rc)
    except:
        traceback.print_exc()

def on_message(mqttc, userdata, msg, player):
    try:
        print("MESSAGE:", userdata, msg.topic, msg.qos, msg.payload)
        message = msg.payload.decode().split()
        if ('clients/flota/sala/' in msg.topic) and len(message) == 3:
            print('AAAAAAAAAAAAAAAAAAAAA', message)
            change_btn_color(mqttc, int(message[0]),int(message[1]), int(message[2]))
        elif ('clients/flota/sala/' in msg.topic) and len(message) == 2:
            print('BBBBBBBBBBBBBBBBBBBBB', message)
            put_x(mqttc, player, int(message[0]), int(message[1]))



    except:
        traceback.print_exc()

def on_publish(mqttc, userdata, mid):
    try:
        print("PUBLISH:", userdata, mid)
    except:
        traceback.print_exc()

def on_subscribe(mqttc, userdata, mid, granted_qos):
    try:
        print("SUBSCRIBED:", userdata, mid, granted_qos)
    except:
        traceback.print_exc()

def on_unsubscribe(mqttc, userdata, mid):
    try:
        print("UNSUBSCRIBED:", userdata, mid)
    except:
        traceback.print_exc()

def main():
    name = input('Como te llamas? ')
    if not name:
        name = ''.join((random.choice('abcdxyzpqr0123456789') for i in range(5)))

    print(f'Bienvenido {name}')
    
    player = Player(name)

    mqttc = Client(userdata=name)

    mqttc.on_message = lambda mqttc, userdata, msg: on_message(mqttc, userdata, msg, player)
    # mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    # mqttc.on_unsubscribe = on_unsubscribe

    mqttc.connect("picluster02.mat.ucm.es")

    mqttc.subscribe('clients/flota/sala/' + name)
    mqttc.publish('clients/flota/jugador', player.name + player.board.barcos_to_string())
    
    create_interface(mqttc, player)

if __name__ == "__main__":
    main()