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
BARCOS = 5


class Player():
    def __init__(self, name, pos):
        self.name = name
        self.board = Board(pos)
        self.hits = 0
    
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
        self.status[pos[0]][pos[1]] = 1

class Game():
    def __init__(self):
        self.num_jug = 0
        self.jugadores = [Player, Player]
        self.status = 0  # 0 sin empezar, 1 en progreso, 2 finalizado
    
    def show_boats(self, jug):
        mostrar = ''
        for i in range(len(jug.board.barcos)):
            for j in jug.board.barcos[i]:
                mostrar += '|' + str(j)
            mostrar += '|\n'

        return mostrar
    
    def show_status(self, jug):
        mostrar = ''
        for i in range(len(jug.board.status)):
            for j in range(len(jug.board.status[i])):
                if jug.board.status[i][j] == 1:
                    mostrar += '|' + str(jug.board.barcos[i][j])
                else:
                    mostrar += '|' + ' '
            mostrar += '|\n'

        return mostrar

    def show_boards(self, jug):
        jugboard = 'Tu tablero:\n' + self.show_boats(jug)
        if jug == self.jugadores[0]:
            otherboard = f'Tablero de {self.jugadores[1].name}:\n' + self.show_boats(self.jugadores[1])
        else:
            otherboard = f'Tablero de {self.jugadores[0].name}:\n' + self.show_status(self.jugadores[0])
            
        return jugboard + '\n' + otherboard

    def change_board(self, jug, pos):
        jug.board.status[pos[1]][pos[0]] = 1

def on_connect(mqttc, userdata, flags, rc):
    try:
        print("CONNECT:", userdata, flags, rc)
    except:
        traceback.print_exc()

def on_message(mqttc, userdata, msg, game):
    try:
        #print("MESSAGE:", userdata, msg.topic, msg.qos, msg.payload,)
        if msg.topic == 'clients/flota/jugador' and game.num_jug == 2:
            data = msg.payload.split()
            name = str(data[0])[2:-1]
            mqttc.publish(f'clients/flota/sala/{name}', 'Partida llena. Vuelva a intentarlo en unos minutos.')
        elif msg.topic == 'clients/flota/jugador':
            data = msg.payload.split()
            name = str(data[0])[2:-1]
            pos = []
            for i in data[1:]:
                pos.append((int(str(i)[2]), int(str(i)[4])))
            game.jugadores[game.num_jug] = Player(name, pos)
            game.num_jug += 1
            mqttc.subscribe(msg.topic + '/' + name)
            if game.num_jug == 2:
                mqttc.publish(f'clients/flota/sala/{game.jugadores[0].name}', game.jugadores[1].name)
                mqttc.publish(f'clients/flota/sala/{game.jugadores[1].name}', game.jugadores[0].name)
                game.status = 1
        else:
            name = msg.payload.decode().split()[0]
            fila = int(msg.payload.decode().split()[1])
            columna = int(msg.payload.decode().split()[2])

            if name == game.jugadores[0].name:
                game.jugadores[0].hits += game.jugadores[1].board.barcos[fila][columna]
                mqttc.publish(f'clients/flota/sala/{game.jugadores[0].name}', str(game.jugadores[1].board.barcos[fila][columna]) + ' ' + str(fila+1) + ' ' + str(columna+1))
                mqttc.publish(f'clients/flota/sala/{game.jugadores[1].name}', str(fila+1) + ' ' + str(columna+1))
                if game.jugadores[0].hits >= BARCOS:
                    mqttc.publish(f'clients/flota/sala/{game.jugadores[0].name}', 'Felicidades, ha ganado la partida.')
                    mqttc.publish(f'clients/flota/sala/{game.jugadores[1].name}', 'Lo siento, ha perdido la partida.')

            elif name == game.jugadores[1].name:
                game.jugadores[1].hits += game.jugadores[0].board.barcos[fila][columna]
                mqttc.publish(f'clients/flota/sala/{game.jugadores[1].name}', str(game.jugadores[0].board.barcos[fila][columna]) + ' ' + str(fila+1) + ' ' + str(columna+1))
                mqttc.publish(f'clients/flota/sala/{game.jugadores[0].name}', str(fila+1) + ' ' + str(columna+1))
                if game.jugadores[1].hits >= BARCOS:
                    mqttc.publish(f'clients/flota/sala/{game.jugadores[1].name}', 'Felicidades, ha ganado la partida.')
                    mqttc.publish(f'clients/flota/sala/{game.jugadores[0].name}', 'Lo siento, ha perdido la partida.')
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
    game = Game()

    mqttc = Client(userdata='sala')
    
    mqttc.on_message = lambda mqttc, userdata, msg: on_message(mqttc, userdata, msg, game)
    # mqttc.on_connect = on_connect
    # mqttc.on_publish = on_publish
    #mqttc.on_subscribe = on_subscribe
    # mqttc.on_unsubscribe = on_unsubscribe

    mqttc.connect("picluster02.mat.ucm.es")
    mqttc.subscribe('clients/flota/jugador')

    mqttc.loop_forever()

if __name__ == "__main__":
    main()