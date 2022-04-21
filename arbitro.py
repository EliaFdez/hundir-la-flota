import paho.mqtt.client as mqtt



# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    
    client.subscribe(f"tablero1/p_estado")
    client.subscribe(f"tablero2/p_estado")
    client.subscribe(f"tablero1/p_accion")
    client.subscribe(f"tablero2/p_accion")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg, estado_partida, barcos):
    topic = msg.topic
    tablero, tipo = topic.split("/")
    
    if estado_partida[0] == 0 and tipo == "p_estado": # ha recibido que un jugador posiciona un barco
        msg_barcos = str(msg.payload.decode()).split("|")
        jugador = int(tablero[-1])
        barcos[jugador] = []
        for barco in msg_barcos:
            x, y = barco.split(",")
            x, y = int(x), int(y)
            barcos[jugador].append((x, y))
            print(f"Recibido barco {x} {y} de jugador {jugador}")
        
        if len(barcos[1]) == len(barcos[2]) == 10:
            estado_partida[0] = 1
            client.publish(f"tablero1/r_estado", "empieza")
            client.publish(f"tablero2/r_estado", "empieza")
    elif estado_partida[0] == 1 and tipo == "p_accion": # ha recibido que un jugador posiciona un barco
        barco = str(msg.payload.decode())
        jugador = int(tablero[-1])
        x, y = barco.split(",")
        x, y = int(x), int(y)
        
        if jugador == 1: contrincante = 2
        else: contrincante = 1
        
        if (x, y) in barcos[contrincante]:
            barcos[contrincante].remove((x, y))
            client.publish(f"tablero{jugador}/r_accion", f"{x},{y}|ok")
            client.publish(f"tablero{contrincante}/r_estado", f"{x},{y}")
            if len(barcos[contrincante]) == 0:
                client.publish(f"tablero{jugador}/r_estado", "ganado")
                client.publish(f"tablero{contrincante}/r_estado", "perdido")
                barcos[jugador] = []
                estado_partida[0] = 0
        else:
            client.publish(f"tablero{jugador}/r_accion", f"{x},{y}|agua")
        
def mqttmain():
    barcos = {
        1 : [],
        2 : []
    }
    
    estado_partida = [0] # 0 = no ha empezado,  1 = ha empezado, 2 finalizado
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = lambda client, userdata, msg: on_message(client, userdata, msg, estado_partida, barcos)
    
    client.connect("mqtt.eclipseprojects.io", 1883, 60)

    # manual interface.
    client.loop_forever()

mqttmain()