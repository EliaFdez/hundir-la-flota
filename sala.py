"""
Envía mensajes a un canal por jugador (clients/flota/sala/...).
Recibe mensajes de cada jugador por un canal (clients/flota/jugador/...).

Cada vez que recibe información de un jugador, la procesa y manda los tableros actualizados a todos los jugadores.
"""

from paho.mqtt.client import Client
from multiprocessing import Lock
from tkinter import *
import random
import traceback

ANCHO = 5
ALTO = 5
BARCOS = 3


class Player():
    def __init__(self, name, pos):
        self.name = name
        self.board = Board(pos)
    
    def __str__(self):
        return self.name

class Board():
    def __init__(self, pos):
        self.ancho = ANCHO
        self.alto = ALTO
        self.barcos = self.build_board(pos) # 0 agua, 1 barco
        self.status = [[0 for i in range(self.ancho)] for j in range(self.alto)]  # 0 nada, 1 disparado
    
    def build_board(self, pos):
        tab = [[0 for i in range(self.ancho)] for j in range(self.alto)]
        for i in pos:
            tab[i[0]][i[1]] = 1
        return tab

    def actualizar(self, pos):
        self.status[pos[1]][pos[0]] = 1

class Game():
    def __init__(self, jug1, jug2):
        self.jugador1 = jug1
        self.jugador2 = jug2
    
    def show_boats(self, jug):
        mostrar = ''
        for i in range(len(jug.board.barcos)):
            for j in jug.board.barcos[i]:
                mostrar += '|' + str(j)
            mostrar += '|\n'

        return mostrar
    
    def show_status(self, jug):
        mostrar = ''
        for i in range(len(jug.status)):
            for j in jug.status[i]:
                if j == 1:
                    mostrar += '|' + str(jug.board.barcos[i][j])
                else:
                    mostrar += '|' + ' '
            mostrar += '|\n'

        return mostrar

    def show_boards(self, jug):
        jugboard = self.show_boats(jug)
        if jug == self.jugador1:
            otherboard = self.show_status(self.jugador2)
        else:
            otherboard = self.show_status(self.jugador1)
            
        return jugboard + '\n' + otherboard

    def change_board(self, jug, pos):
        jug.board.status[pos[1]][pos[0]] = 1

def on_connect(mqttc, userdata, flags, rc):
    try:
        print("CONNECT:", userdata, flags, rc)
    except:
        traceback.print_exc()

def on_message(mqttc, userdata, msg):
    try:
        print("MESSAGE:", userdata, msg.topic, msg.qos, msg.payload)
        if msg.topic == 'clients/flota/jugador':
            data = msg.payload.split()
            name = str(data[0])[2:-1]
            pos = []
            for i in data[1:]:
                pos.append((int(str(i)[2]),int(str(i)[4])))
            player1 = Player(name, pos)

            mqttc.subscribe(msg.topic + name)
            
            mqttc.publish('clients/flota/sala/' + name, 'HA JUGAR')
            print('clients/flota/sala/' + name)

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

def main():
    mqttc = Client(userdata='sala')
    
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe

    mqttc.connect("picluster02.mat.ucm.es")
    mqttc.subscribe('clients/flota/jugador')

    mqttc.loop_forever()

if __name__ == "__main__":
    main()