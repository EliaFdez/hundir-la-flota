import paho.mqtt.client as mqtt
from itertools import product
from random import choices
import argparse

parser = argparse.ArgumentParser(description='Jugador.')
parser.add_argument('i', metavar='N', type=int, nargs=1, help='n')
args = parser.parse_args()
N = args.i[0]
print(N)
def generar_tablero(m, n, n_barcos):
    return choices(list(product(range(m), range(n))), k = n_barcos)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc, barcos):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    m, n = 20, 20
    barcos_aux = generar_tablero(m, n, 10)
    barcos.extend(barcos_aux)
    # suscribirse al estado de mi tablero y enviar los barcos
    client.subscribe(f"tablero{N}/r_estado")
    client.subscribe(f"tablero{N}/r_accion")
    
    # se envia el estado de esta forma: 3,4|5,6|9,1
    client.publish(f"tablero{N}/p_estado", "|".join([f"{x},{y}" for x, y in barcos]))
        
    # enviar barcos al "servidor"
    # client.subscribe(f"tablero{n}/accion")
    

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg, barcos):
    topic = msg.topic
    print(f"[{topic}] {msg.payload}")
    if topic.endswith("estado"): # le han matado un barco
        # recibe un mensaje del tipo "4,5" o "perdido" o "ganado"
        barco_asesinado = str(msg.payload.decode())
        
        if barco_asesinado == "empieza":
            pass # se comunica que ya se puede atacar
        elif barco_asesinado == "perdido":
            pass # avisar de que has perdido
        elif barco_asesinado == "ganado":
            pass # avisar de que has ganado
        else:
            x, y = barco_asesinado.split(",")
            x, y = int(x), int(y)
            barcos.remove((x, y))
            print(barcos)
            pass # avisar a tkinter del barco perdido y eliminarlo
    elif topic.endswith("accion"): # resultado de una acción
        # recibe un mensaje del tipo "4,5|agua" o "4,5|ok"
        barco_asesinado, resultado = str(msg.payload.decode()).split("|")
        x, y = barco_asesinado.split(",")
        x, y = int(x), int(y)
        # actualizar tkinter
        
    

def atacar(client, x, y):
    client.publish(f"tablero{N}/p_accion", f"{x},{y}")
   

def mqtt_main():
    barcos = []

    client = mqtt.Client()
    client.on_connect = lambda client, userdata, flags, rc: on_connect(client, userdata, flags, rc, barcos)
    client.on_message = lambda client, userdata, msg: on_message(client, userdata, msg, barcos)
    client.connect("mqtt.eclipseprojects.io", 1883, 60)

    # INICIAR TKINTER
    client.loop_forever()
mqtt_main()