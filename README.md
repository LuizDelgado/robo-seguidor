# RoboSeguidorDeMao

## Descrição
RoboSeguidorDeMao é um projeto que integra visão computacional e controle de robótica para seguir movimentos da mão humana em tempo real. Utilizando a biblioteca MediaPipe para rastreamento de mãos, este sistema captura coordenadas da mão e as envia, através de uma comunicação via socket, para um robô RV2F-BD da Mitsubishi Electric, que responde aos gestos realizados.

## Funcionalidades
- **Rastreamento de Mão**: Utiliza MediaPipe para detectar e rastrear a posição da mão em tempo real.
- **Comunicação em Tempo Real**: Envio de coordenadas via protocolo socket para controle do robô.
- **Controle de Robô**: Manipulação de um robô Mitsubishi RV2F-BD para seguir os movimentos da mão detectados pela câmera.

## Tecnologias Utilizadas
- Python 3.x
- OpenCV
- MediaPipe
- Socket Programming
- MQTT para comunicação entre dispositivos
- Dotenv para gerenciamento de variáveis de ambiente

## Pré-requisitos
Antes de iniciar, certifique-se de que você possui Python 3.x instalado em sua máquina. Você também precisará instalar as seguintes bibliotecas Python:
- `mediapipe`
- `cv2` (OpenCV)
- `paho-mqtt`
- `python-dotenv`

Você pode instalar todas as dependências necessárias com o seguinte comando:
```bash
pip install mediapipe opencv-python paho-mqtt python-dotenv
```

## Configuração
Passo 1: Copie o repositório para uso.
```bash
git clone https://github.com/LuizDelgado/robo-seguidor.git
```

Passo 2: Configure as variáveis de ambiente necessárias criando um arquivo .env na raiz do projeto e adicione as seguintes linhas como consta no arquivo env_example.

## Como executar

Depois de ter todas as variavéis de ambiente configuradas basta inicializar usando o comando 

```bash
python main.py
```

## Cuidado

O projeto final tem uma sinaleira integrada a um raspberry que mostra LED's vermelhos e verde sinalizando o estado de funcionamento do robô, se não for utilizar disso, retire TODAS as referências ao MQTT do código main para que ele possa inicializar corretamente.

## Contato

Luiz Felipe de Souza Delgado

@luzenhoww - Instagram
Luiz Felipe de Souza Delgado - LinkedIn
lfdelgadito@gmail.com



