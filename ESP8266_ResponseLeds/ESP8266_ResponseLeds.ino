#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

const char* ssid = "Janco";         // Cambia por tu SSID
const char* password = "ZG3011#cdz"; // Cambia por tu contraseña

ESP8266WebServer server(80);

// Pines para los LEDs
const int ledIzquierda = 5;  // LED para "izquierda"
const int ledCentro = 4;     // LED para "centro"
const int ledDerecha = 0;    // LED para "derecha"

void setup() {
  Serial.begin(115200);

  // Configurar pines de los LEDs como salida
  pinMode(ledIzquierda, OUTPUT);
  pinMode(ledCentro, OUTPUT);
  pinMode(ledDerecha, OUTPUT);

  // Apagar todos los LEDs al inicio
  digitalWrite(ledIzquierda, LOW);
  digitalWrite(ledCentro, LOW);
  digitalWrite(ledDerecha, LOW);

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
  server.handleClient();
}

// Función para manejar las peticiones entrantes
void handleMensaje() {
  String text = server.arg("text");
  
  // Imprimir el mensaje recibido en el Serial Monitor
  Serial.println("Mensaje recibido: " + text);

  // Apagar todos los LEDs antes de encender el correspondiente
  digitalWrite(ledIzquierda, LOW);
  digitalWrite(ledCentro, LOW);
  digitalWrite(ledDerecha, LOW);

  // Control de LEDs basado en el texto recibido
  if (text.indexOf("izquierda") >= 0) {
    // Encender LED 1 para "izquierda"
    Serial.println("Encender LED1 (Izquierda)");
    digitalWrite(ledIzquierda, HIGH);
  } else if (text.indexOf("centro") >= 0) {
    // Encender LED 2 para "centro"
    Serial.println("Encender LED2 (Centro)");
    digitalWrite(ledCentro, HIGH);
  } else if (text.indexOf("derecha") >= 0) {
    // Encender LED 3 para "derecha"
    Serial.println("Encender LED3 (Derecha)");
    digitalWrite(ledDerecha, HIGH);
  }

  // Responder al cliente que envió el mensaje
  server.send(200, "text/plain", "Mensaje recibido");
}
