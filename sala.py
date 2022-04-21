"""
Envía mensajes a un canal por jugador (clients/flota/sala/...).
Recibe mensajes de cada jugador por un canal (clients/flota/jugador/...).

Cada vez que recibe información de un jugador, la procesa y manda los tableros actualizados a todos los jugadores.
"""

from paho.mqtt.client import Client
from multiprocessing import Lock
from tkinter import *

ANCHO = 20
ALTO = 20


class Tablero():
    def __init__(self):
        self.ancho = ANCHO
        self.alto = ALTO

    def __str__(self):
        return (self.ancho, self.alto)