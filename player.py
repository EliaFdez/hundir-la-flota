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

ANCHO = 5
ALTO = 5
BARCOS = 3


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
            tabinit[i//self.ancho][i%self.ancho] = 1
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

def start_game():
    finished = False
    print('JUEGO EMPEZADO')
    while not finished:
        pos = input('Donde quieres atacar: ')

def on_connect(mqttc, userdata, flags, rc):
    try:
        print("CONNECT:", userdata, flags, rc)
    except:
        traceback.print_exc()

def on_message(mqttc, userdata, msg):
    try:
        print("MESSAGE:", userdata, msg.topic, msg.qos, msg.payload)
        waiting = True
        if ('clients/flota/sala/' in msg.topic) and waiting:
            waiting = False
            start_game()

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

    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    mqttc.on_unsubscribe = on_unsubscribe

    mqttc.connect("picluster02.mat.ucm.es")

    mqttc.subscribe('clients/flota/sala/' + name)
    print('clients/flota/sala/' + name)
    mqttc.publish('clients/flota/jugador', player.name + player.board.barcos_to_string())
    
    mqttc.loop_forever()

if __name__ == "__main__":
    main()