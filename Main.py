#Importando as bibliotecas
from commands import Robot, MQTTClient
from dotenv import load_dotenv
import os
import mediapipe as mp
import cv2
import time

#Carregando as varivaveis de ambiente
load_dotenv()

x_rec, y_rec, w_rec, h_rec = 60, 112, 520, 255

#flags de controle de ação
control_servo_on_flag = True
control_servo_state_flag = False

#Adicionando os parametros para o reconhecimento de imagem
cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)
hand = mp.solutions.hands
Hand = hand.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils

#iniciando comunicação com o robô
host_init = os.getenv("HOST")
port_init = os.getenv("PORT")
BROKER = str(os.getenv("BROKER"))
PORT = int(os.getenv("PORT"))
USERNAME = str(os.getenv("HOST_NAME"))
PASSWORD = str(os.getenv("PASSWORD"))
CLIENT_ID = str(os.getenv("CLIENT_ID"))
TOPIC = str(os.getenv("TOPIC"))

host_robot = str(host_init) #Ip do robô tem que ser str 
port_robot = int(port_init) #Port de comunicação tem que ser um número inteiro
robo = Robot(365, 225,165,-76.5,445,225,-180,0,180,0.80,0.20,0.25,0.75,-0.12,-0.5)
robo.connect_to_robot(host_robot, port_robot)
leds = MQTTClient(BROKER, PORT, USERNAME,PASSWORD, CLIENT_ID)
robo.start_control()
robo.set_speed(100)
leds.publish(TOPIC, "led_verde")
led_verde_ligado = False
led_vermelho_ligado = False

while True:
    check, img = cam.read()
    imgrgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = Hand.process(imgrgb)
    handpoints = results.multi_hand_landmarks
    h,w,_ = img.shape
    pontos = []

    if handpoints:
        for points in handpoints:
            mpDraw.draw_landmarks(img, points, hand.HAND_CONNECTIONS)
            for id, cord in enumerate(points.landmark):
                cx,cy = int(cord.x*w), int(cord.y*h)
                cv2.putText(img, str(id), (cx,cy + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (90,41,70),2)
                cv2.rectangle(img, (x_rec,y_rec), (x_rec + w_rec, y_rec + h_rec), (0, 255, 0), thickness=2 )
                pontos.append((cx, cy))

        dedos = [8,12,16,20]
        contador = 0
        if points:
            if pontos [4][0] < pontos[2][0]:
                contador +=1
            for x in dedos:
                if pontos[x][1] < pontos[x-2][1]:
                    contador += 1 

            if contador >=4:
                if not led_verde_ligado:
                    leds.publish(TOPIC, "led_vermelho")
                    led_verde_ligado = True
                    led_vermelho_ligado = False
                if control_servo_on_flag:
                    robo.servo_on()
                    time.sleep(3)
                    control_servo_state_flag = True
                    control_servo_on_flag = False

                if control_servo_state_flag: 
                    reference_point = handpoints[0].landmark[8]
                    x, y, z, z_manipulated = (
                        format(reference_point.x, '.2f'),
                        format(reference_point.y, '.2f'),
                        format(reference_point.z, '.3f'),
                        format(reference_point.z, '.2f')
                    )
                    z_decimal = int(z[-1])
                    if 0 <= z_decimal <= 6:
                        z_final = f"{z_manipulated}4"
                    else:
                        z_final = f"{z_manipulated}9"

                    robo.moviment(x,y,z_final)
                    time.sleep(0.05)

            elif contador < 4:
                if not led_vermelho_ligado:
                    leds.publish(TOPIC, "led_verde")
                    led_vermelho_ligado = True
                    led_verde_ligado = False

        cv2.rectangle(img,(20,10),(100,50),(90,41,70), -1)
        cv2.putText(img, str(contador),(48,48),cv2.FONT_HERSHEY_COMPLEX,1.5,(255,255,255),3)
    img = cv2.flip(img,1)
    cv2.imshow("Camera", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
robo.end_control()
