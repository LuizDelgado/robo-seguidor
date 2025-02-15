import socket
import re
import time
import paho.mqtt.client as mqtt

class Robot():
    socketRobo = None
    def __init__(self, x_max, x_min, y_max, y_min, z_max, z_min,  a, b, c, camx_max, camx_min, camy_max, camy_min, camz_max, camz_min):
        self.x_max = x_max
        self.x_min = x_min
        self.y_max = y_max
        self.y_min = y_min
        self.z_max = z_max
        self.z_min = z_min 
        self.a = a
        self.b = b
        self.c = c
        self.camx_max = camx_max
        self.camx_min = camx_min
        self.camy_max = camy_max
        self.camy_min = camy_min
        self.camz_max = camz_max
        self.camz_min = camz_min

    @classmethod #Herança de classes
    def connect_to_robot(cls, host, port):
        socketRobo = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Instancia socket
        socketRobo.connect((host, port)) #Efetua conexão com o robô
        cls.socketRobo = socketRobo
        return cls

    def set_speed(self, speed=30):
        self.socketRobo.sendall("1;1;EXECSPD {}".format(speed).encode())  #Seta a velocidade do robô
        data = self.socketRobo.recv(1024)
        print(f"Received {data!r}")
        print("A velocidade do robô foi definida em {}".format(speed))

    def start_control(self):
        self.socketRobo.sendall(b"1;1;CNTLON")  #Inicia controle
        data = self.socketRobo.recv(1024) #Aguarda reasposta
        print(f"Received {data!r}") #Printa resposta

        self.socketRobo.sendall(b"1;1;EXECACCEL 30") #Seta aceleração do robô
        data = self.socketRobo.recv(1024)
        print(f"Received {data!r}")

        self.socketRobo.sendall(b"1;1;EXECMvTune 2") #Seta o robô no modo aprimorado para velocidade
        data = self.socketRobo.recv(1024)
        print(f"Received {data!r}")

        #A PARTIR DAQUI O ROBÔ ESTÁ HÁPTO A SER MOVIMENTADO
    def servo_on(self): #Liga o robô na programação desejada
        self.socketRobo.sendall(b"1;1;SRVON") #Habilita os servos
        data = self.socketRobo.recv(1024)
        print(f"Received {data!r}")

    def resetmap(self): #Essa função realiza o reset do robo no mapa dele 
        p1 = [196.360, -15.000, 370.000, 180.000, 0.000, 180.000]
        p2 = [104.000, -113.000, 451.000, 180.000, 0.000, 180.000]

        for qtd_posicoes in range(2):
            if qtd_posicoes == 0:
                    x = p1[0]
                    y = p1[1]
                    z = p1[2]
                    a = p1[3]
                    b = p1[4]
                    c = p1[5]
            elif qtd_posicoes == 1:
                    x = p2[0]
                    y = p2[1]
                    z = p2[2]
                    a = p2[3]
                    b = p2[4]
                    c = p2[5]

            self.socketRobo.sendall("1;1;EXECPPOS=({}, {}, {}, {}, {}, {})".format(x,y,z,a,b,c).encode()) #reinicia o robô
            data = self.socketRobo.recv(1024)
            print(f"Received {data!r}")
            self.socketRobo.sendall(b"1;1;EXECMOV PPOS") #reinicia o robô
            data = self.socketRobo.recv(1024)
            print(f"Received {data!r}")

    def reset(self): #Função que reinicia o controlador do robô
        str_commands = ["1;0;STOP","1;1;SLOTINIT",
                    "1;1;STATE","1;2;STATE",
                    "1;3;STATE","1;4;STATE",
                    "1;5;STATE","1;6;STATE",
                    "1;7;STATE","1;8;STATE"]
        for list_commands in str_commands:
            self.socketRobo.sendall('{}'.format(list_commands).encode()) #reinicia o robô
            data = self.socketRobo.recv(1024)
            print(f"Received {data!r}")

    def end_control(self):
        self.socketRobo.sendall(b"1;1;CNTLOFF") #desliga o controle
        data = self.socketRobo.recv(1024)
        print(f"Received {data!r}")
        self.socketRobo.close()

    def open_hand(self): #Abre a garra do robô
        str_commands = ["1;1EXECHCLOSE 1"]
        for list_commands in str_commands:
            self.socketRobo.sendall('{}'.format(list_commands).encode()) #reinicia o robô
            data = self.socketRobo.recv(1024)
            print(f"Received {data!r}")

    def close_hand(self): #Abre a garra do robô
        str_commands = ["1;1EXECHOPEN 1"]
        for list_commands in str_commands:
            self.socketRobo.sendall('{}'.format(list_commands).encode()) #reinicia o robô
            data = self.socketRobo.recv(1024)
            print(f"Received {data!r}")

    def moviment(self, x_cam, y_cam, z_cam): #função que determina o movimento do robô de acordo com a posição da mão
        float_pos_y_cam = float(y_cam)
        float_pos_z_cam = float(z_cam)
        #                           p4                        p3                        p2                         p1
        quadrado_maior = [(self.x_max, self.y_min), (self.x_max, self.y_max), (self.x_min, self.y_max), (self.x_min, self.y_min)]
        L1 = quadrado_maior[0][0] - quadrado_maior [3][0]
        L2 = quadrado_maior[1][1] - quadrado_maior[0][1]
        #x da camera é o y do robo
        resultado_proporcaoy = (L2 * float(x_cam))

        # y_robot = self.y_min + resultado_proporcaoy
        y_robot = self.y_max - resultado_proporcaoy
        x_robot = (self.x_max*float_pos_z_cam)/self.camz_max#ok
        z_robot = (self.z_max*self.camy_max)/float_pos_y_cam #ok
        a = self.a
        b = self.b
        c = self.c


        if self.x_min > x_robot:
            x_robot = self.x_min
        if x_robot > self.x_max:
            x_robot = self.x_max

        if self.y_min > y_robot:
            y_robot = self.y_min
        if y_robot > self.y_max:
            y_robot = self.y_max

        if self.z_min > z_robot:
            z_robot = self.z_min
        if z_robot > self.z_max:
            z_robot = self.z_max

        self.socketRobo.sendall("1;1;EXECPPOS=({}, {}, {:.3f}, {}, {}, {})".format(x_robot, y_robot, z_robot, a, b, c).encode()) # Envia os vetores
        data = self.socketRobo.recv(1024)

        print(f"Received {data!r}")
        self.socketRobo.sendall(b"1;1;EXECMOV PPOS") #Manda o robô para a posição
        data = self.socketRobo.recv(1024)
        print(f"Received {data!r}")

    def get_poss(self):
        self.socketRobo.sendall(b"1;1;VALP_CURR")  # Envia o comando desejado
        data = self.socketRobo.recv(1024)
        data_str = str(data, 'utf-8')  # Converte os bytes recebidos para uma string UTF-8
        match = re.search(r'\((.*?)\)', data_str)
        if match:
            content_inside_brackets = match.group(1)
            coordenates = content_inside_brackets.split(",")
            print(coordenates[0], coordenates[1],coordenates[2],coordenates[3],coordenates[4],coordenates[5])
            time.sleep(3)

    def verify_pos(self):
        self.socketRobo.sendall(b"1;1;VALP_CURR")  # Envia o comando desejado
        data = self.socketRobo.recv(1024)
        data_str = str(data, 'utf-8')  # Converte os bytes recebidos para uma string UTF-8
        match = re.search(r'\((.*?)\)', data_str)
        if match:
            content_inside_brackets = match.group(1)
            coordenates = content_inside_brackets.split(",")
            print(f"Received {data_str!r}")
            time.sleep(5)

class MQTTClient:
    # Construtor da classe, inicializa uma instância da classe com as configurações necessárias.
    def __init__(self, broker, port, username, password, client_id):
        self.broker = broker  # Endereço do broker MQTT.
        self.port = port  # Porta para a conexão com o broker.
        self.username = username  # Nome de usuário para autenticação no broker.
        self.password = password  # Senha para autenticação no broker.
        self.client_id = client_id  # ID do cliente para identificação no broker.
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=self.client_id)  # Cria o objeto cliente MQTT com a versão de callback especificada.
        self.configure_client()  # Chama o método para configurar o cliente MQTT.

    # Método para configurar o cliente MQTT, definindo credenciais e handlers (funções de callback).
    def configure_client(self):
        self.client.username_pw_set(self.username, self.password)  # Configura o nome de usuário e senha no cliente MQTT.
        self.client.on_connect = self.on_connect  # Define o handler para o evento de conexão.
        self.client.on_disconnect = self.on_disconnect  # Define o handler para o evento de desconexão.

    # Função chamada quando o cliente se conecta ao broker.
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Conectado ao broker MQTT.")  # Sucesso na conexão.
        else:
            print(f"Falha na conexão com o servidor, código de retorno: {rc}")  # Falha na conexão.

    # Função chamada quando o cliente se desconecta do broker.
    def on_disconnect(self, client, userdata, rc):
        print("Desconectado do broker MQTT.")  # Informa sobre a desconexão.

    # Método para publicar uma mensagem em um tópico específico.
    def publish(self, topic, message):
        try:
            self.client.connect(self.broker, self.port)  # Conecta ao broker MQTT.
            self.client.loop_start()  # Inicia o loop em segundo plano para processar callbacks de rede.
            self.client.publish(topic, message)  # Publica a mensagem no tópico especificado.
            print("Mensagem enviada")
        finally:
            self.client.loop_stop()  # Para o loop de rede.
            self.client.disconnect()  # Desconecta do broker MQTT.
