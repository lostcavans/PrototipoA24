
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

const char* ssid = "Janco";         // Cambia por tu SSID
const char* password = "ZG3011#cdz"; // Cambia por tu contraseña

ESP8266WebServer server(80);

// Pines para los LEDs
const int led1 = 5;  // motor 1
const int led2 = 4;  // motor 2
const int led3 = 0;  // motor 3
const int led4 = 2;  // motor 4

// Pines para los sensores ultrasonidos
const int trigPin1 = 12; // Sensor 1 (Trig)
const int echoPin1 = 13; // Sensor 1 (Echo)
const int trigPin2 = 14; // Sensor 2 (Trig)
const int echoPin2 = 15; // Sensor 2 (Echo)

// Variables para las distancias medidas
long duration1, duration2;
float distance1, distance2;

// Variable para controlar el tiempo desde la última solicitud
unsigned long lastMessageTime = 0;
const unsigned long timeout = 500; // Tiempo límite en milisegundos (3 segundos)

// Variable para bloquear mensajes cuando sensores detectan algo cercano
bool sensorPriority = false;

void setup() {
  Serial.begin(115200);

  // Configurar pines de los LEDs como salida
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
  pinMode(led3, OUTPUT);
  pinMode(led4, OUTPUT);

  // Configurar pines de los sensores ultrasonidos
  pinMode(trigPin1, OUTPUT);
  pinMode(echoPin1, INPUT);
  pinMode(trigPin2, OUTPUT);
  pinMode(echoPin2, INPUT);

  // Apagar todos los LEDs al inicio
  digitalWrite(led1, LOW);
  digitalWrite(led2, LOW);
  digitalWrite(led3, LOW);
  digitalWrite(led4, LOW);

  // Configurar Wi-Fi
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.print("IP del ESP8266: ");
  Serial.println(WiFi.localIP());  // Muestra la IP asignada al ESP8266

  // Manejar peticiones en "/mensaje"
  server.on("/mensaje", handleMensaje);
  server.begin();
}

void loop() {
  // Leer datos de los sensores ultrasonidos
  distance1 = measureDistance(trigPin1, echoPin1);
  distance2 = measureDistance(trigPin2, echoPin2);

  // Lógica para bloquear mensajes si hay obstáculos cercanos
  if (distance1 < 10 || distance2 < 10) {
    sensorPriority = true; // Bloquea mensajes
    handleObstacle(distance1, distance2); // Manejar acciones
  } else {
    sensorPriority = false; // Permite mensajes
  }

  // Manejar solicitudes del cliente solo si no hay prioridad de sensores
  if (!sensorPriority) {
    server.handleClient();

    // Verificar si ha pasado el tiempo límite desde el último mensaje recibido
    if (millis() - lastMessageTime > timeout) {
      // Apagar todos los LEDs si no se ha recibido mensaje en el tiempo especificado
      digitalWrite(led1, LOW);
      digitalWrite(led2, LOW);
      digitalWrite(led3, LOW);
      digitalWrite(led4, LOW);
    }
  }

  delay(100); // Ajustar para evitar lecturas constantes
}

// Función para manejar obstáculos detectados por sensores
void handleObstacle(float dist1, float dist2) {
  if (dist1 < 20) { // Objeto cerca del lado izquierdo
    Serial.println("Obstáculo cercano en el lado izquierdo.");
    // Secuencia de movimiento derecha -> recto -> izquierda
    digitalWrite(led1, LOW);
    digitalWrite(led2, HIGH);
    digitalWrite(led3, LOW);
    digitalWrite(led4, HIGH);
    delay(1000);

    digitalWrite(led1, LOW);
    digitalWrite(led2, HIGH);
    digitalWrite(led3, HIGH);
    digitalWrite(led4, LOW);
    delay(1000);

    digitalWrite(led1, HIGH);
    digitalWrite(led2, LOW);
    digitalWrite(led3, HIGH);
    digitalWrite(led4, LOW);
    delay(500);
  }

  if (dist2 < 20) { // Objeto cerca del lado derecho
    Serial.println("Obstáculo cercano en el lado derecho.");
    // Secuencia de movimiento izquierda -> recto -> derecha
    digitalWrite(led1, HIGH);
    digitalWrite(led2, LOW);
    digitalWrite(led3, HIGH);
    digitalWrite(led4, LOW);
    delay(1000);

    digitalWrite(led1, LOW);
    digitalWrite(led2, HIGH);
    digitalWrite(led3, HIGH);
    digitalWrite(led4, LOW);
    delay(1000);

    digitalWrite(led1, LOW);
    digitalWrite(led2, HIGH);
    digitalWrite(led3, LOW);
    digitalWrite(led4, HIGH);
    delay(400);
  }
}

// Función para medir distancia con un sensor ultrasonido
float measureDistance(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH);
  float distance = (duration * 0.034) / 2; // Convertir a distancia en cm
  return distance;
}

// Función para manejar las peticiones entrantes
void handleMensaje() {
  if (sensorPriority) {
    server.send(503, "text/plain", "Prioridad en sensores. Mensaje ignorado.");
    return;
  }

  String text = server.arg("text");

  // Actualizar el tiempo de la última solicitud recibida
  lastMessageTime = millis();
  
  // Imprimir el mensaje recibido en el Serial Monitor
  Serial.println("Mensaje recibido: " + text);

  // Apagar todos los LEDs antes de encender el correspondiente
  digitalWrite(led1, LOW);
  digitalWrite(led2, LOW);
  digitalWrite(led3, LOW);
  digitalWrite(led4, LOW);

  // Control de LEDs basado en el texto recibido
  if (text.indexOf("izquierda") >= 0) {
    Serial.println("Encender LED (Izquierda)");
    digitalWrite(led1, HIGH);
    digitalWrite(led2, LOW);
    digitalWrite(led3, HIGH);
    digitalWrite(led4, LOW);
  } else if (text.indexOf("centro") >= 0) {
    Serial.println("Encender LED (Centro)");
    digitalWrite(led1, LOW);
    digitalWrite(led2, HIGH);
    digitalWrite(led3, HIGH);
    digitalWrite(led4, LOW);
  } else if (text.indexOf("derecha") >= 0) {
    digitalWrite(led1, LOW);
    digitalWrite(led2, HIGH);
    digitalWrite(led3, LOW);
    digitalWrite(led4, HIGH);
  } else if (text.indexOf("muy cerca") >= 0) {
    Serial.println("Encender LED (Muy Cerca)");
    digitalWrite(led1, LOW);
    digitalWrite(led2, LOW);
    digitalWrite(led3, LOW);
    digitalWrite(led4, LOW);
  }

  // Responder al cliente que envió el mensaje
  server.send(200, "text/plain", "Mensaje recibido");
}
