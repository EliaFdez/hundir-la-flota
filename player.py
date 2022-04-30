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

ANCHO = 3
ALTO = 3
BARCOS = 2


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

class Interface():
    def __init__(self):
        self.root = Tk() # Ventana Principal
        self.root.title("Silk the float") # Título
        self.root.resizable(0,0) # (0,0) = No se puede ampliar, (1,1) = sí

        # Título
        self.headboard = Label(self.root, text = "Bienvenid@ a Hundir la Flota")
        self.headboard.grid (row = 0, column = 11, columnspan = 2)
        self.headboard.config(fg = "blue",    # Foreground (Color delante)
                         bg = "grey",    # Background (Color detrás)
                         font = ("Verdana", 10)
                        )
    
    # Cambia el color del boton al clickar
    def clickBot (self, event):
        print("ssssssssssssssssssssssssssss", self.button.grid)
        if event.widget["bg"] == "grey": # cuidao, si es agua, azul, si es tocado, rojo

            # (No se queda el mismo color) messagebox.showerror("Hundir La Flota", "Ahí ya cayó un misil")
            event.widget["bg"] = "#00FFFF"
        else:
            pass    

    def graph_board_other (self, board, pos):
    # Tablero Player 1:     
        for i in range(pos[0], ALTO + 2):
            for j in range(pos[1], ANCHO + 1):
                self.button = Button(self.root,
                                    background = "grey",
                                    foreground = "black",
                                    bd = 3, # Borde
                                    padx = "17",
                                    pady = "5",
                                    font = ("Verdana", 8),
                                    width = "1",
                                    relief = RAISED   # Estilo de los botones
                                    )
                self.button.bind("<Button-1>", self.clickBot)
                self.button ["text"] = str(i - 1), ',' , str(j)     # En cada casilla hay escrita su coordenada
                self.button.grid(row = i, column = j)       # Para organizar todas las casillas
                labColumn1 = Label(self.root, text = "Col: " + str(j))      # Etiqueta de COLUMNAS
                labColumn1.grid(row = 12, column = (j))
            labRow1 = Label(self.root, text = "Fila: " + str(i - 1))        # Etiqueta de FILAS
            labRow1.grid(row = (i), column = (j + 1))
        self.root.mainloop()
    
    def graph_game (self, player, board):
        self.graph_board_other(board, (2,1))
        self.graph_board_self(player.board.barcos, (2,1 + ANCHO + 3))

def jugada(mqttc, name):
    # finished = False
    # while not finished:
    print('Donde quieres atacar:')
    fila = input('Fila: ')
    columna = input('Columna: ')
    print(f'clients/flota/jugador/{name}')
    # mqttc.publish(f'clients/flota/jugador/{name}', 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
    mqttc.publish(f'clients/flota/jugador/{name}', f'{name} {fila} {columna}')

def on_connect(mqttc, userdata, flags, rc):
    try:
        print("CONNECT:", userdata, flags, rc)
    except:
        traceback.print_exc()

def on_message(mqttc, userdata, msg, player):
    try:
        # print("MESSAGE:", userdata, msg.topic, msg.qos, msg.payload)
        boards = msg.payload.decode()[:-1]
        game_status = int(msg.payload.decode()[-1])
        if ('clients/flota/sala/' in msg.topic) and game_status == 1:
            print(boards)
            jugada(mqttc, player.name)

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
    # mqttc.on_publish = on_publish
    # mqttc.on_subscribe = on_subscribe
    # mqttc.on_unsubscribe = on_unsubscribe

    mqttc.connect("picluster02.mat.ucm.es")

    mqttc.subscribe('clients/flota/sala/' + name)
    mqttc.publish('clients/flota/jugador', player.name + player.board.barcos_to_string())
    
    mqttc.loop_forever()

if __name__ == "__main__":
    main()