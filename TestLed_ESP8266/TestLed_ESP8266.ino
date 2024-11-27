// Definir los pines de los LEDs
const int led1 = 5;  // GPIO 5 (D1)
const int led2 = 4;  // GPIO 4 (D2)
const int led3 = 0; // GPIO 14 (D5)

// Tiempo de parpadeo
const int delayTime = 500; // Milisegundos

void setup() {
  // Configurar los pines de los LEDs como salida
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
  pinMode(led3, OUTPUT);
}

void loop() {
  // Encender los LEDs
  digitalWrite(led1, HIGH);
  digitalWrite(led2, HIGH);
  digitalWrite(led3, HIGH);
  delay(delayTime);  // Esperar

  // Apagar los LEDs
  digitalWrite(led1, LOW);
  digitalWrite(led2, LOW);
  digitalWrite(led3, LOW);
  delay(delayTime);  // Esperar
}
