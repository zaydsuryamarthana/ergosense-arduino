#include <Arduino.h>

#include <NewPing.h>

#define trigPin 9
#define echoPin 10
#define ledRed 2
#define ledGreen 3
#define caliBtn 5

#define maxDistance 200

NewPing sonar(trigPin, echoPin, maxDistance);

int idealDistance = 0;
unsigned long badPosture = 0;
bool warningActive = false;
const int tolerance = 10;
const int threshold = 5000;

void setup()
{
  pinMode(caliBtn, INPUT_PULLUP);
  pinMode(ledRed, OUTPUT);
  pinMode(ledGreen, OUTPUT);
  Serial.begin(9600);
}

void loop()
{
  if (digitalRead(caliBtn) == LOW)
  {
    calibrate();
  }

  if (idealDistance == 0)
  {
    digitalWrite(ledRed, HIGH);
    delay(100);
    digitalWrite(ledRed, LOW);
    delay(100);
  }

  int currentDist = sonar.ping_cm();
  if (currentDist == 0)
    return;

  if (currentDist < (idealDistance - tolerance))
  {
    if (badPosture == 0)
    {
      badPosture = millis();
    }
    if (millis() - badPosture > threshold)
    {
      trigger();
    }
  }
  else if (currentDist > (idealDistance - tolerance) && currentDist < (idealDistance + tolerance + 20))
  {
    reset();
  }
  else
  {
    reset();
  }
  delay(100);
}

void calibrate()
{
  Serial.println("Tombol Ditekan! Memulai Kalibrasi...");
  long total = 0;
  for (int i = 0; i < 10; i++)
  {
    total += sonar.ping_cm();
    delay(50);
  }
  idealDistance = total / 10;
  Serial.print("Hasil Kalibrasi: ");
  Serial.println(idealDistance);
  digitalWrite(ledGreen, HIGH);
}

void trigger()
{
  digitalWrite(ledGreen, LOW);
  digitalWrite(ledRed, HIGH);
}

void reset()
{
  badPosture = 0;
  digitalWrite(ledRed, LOW);
  digitalWrite(ledGreen, HIGH);
}