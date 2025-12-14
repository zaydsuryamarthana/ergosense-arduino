#include <Arduino.h>
#include <NewPing.h>

#define trigPin 12
#define echoPin 11
#define ledRed 2
#define ledGreen 3
#define caliBtn 5
#define maxDistance 200

NewPing sonar(trigPin, echoPin, maxDistance);

int idealDistance = 0;
unsigned long badPosture = 0;
const int tolerance = 10;
const int threshold = 5000;

void setup()
{
  Serial.begin(9600);
  
  pinMode(caliBtn, INPUT_PULLUP);
  pinMode(ledRed, OUTPUT);
  pinMode(ledGreen, OUTPUT);

  delay(3000);
  calibrate();
}

void loop()
{
  if (digitalRead(caliBtn) == LOW)
  {
    delay(200);
    calibrate();
  }

  if (idealDistance == 0)
  {
    digitalWrite(ledRed, HIGH);
    Serial.print(0);
    Serial.print(",");
    Serial.println("ERROR");
    delay(500);
    digitalWrite(ledRed, LOW);
    delay(500);
    return;
  }

  int currentDist = sonar.ping_cm();
  
  if (currentDist == 0) 
  {
    currentDist = 250;
  }

  String status = "";

  if (currentDist < (idealDistance - tolerance))
  {
    if (badPosture == 0) badPosture = millis();
    
    if (millis() - badPosture > threshold) 
    {
      status = "BAHAYA";
      digitalWrite(ledGreen, LOW);
      digitalWrite(ledRed, HIGH);
    } 
    else 
    {
      status = "WARNING";
      digitalWrite(ledGreen, LOW);
      digitalWrite(ledRed, HIGH);
    }
  }
  else if (currentDist >= (idealDistance - tolerance) && currentDist <= (idealDistance + tolerance + 20))
  {
    badPosture = 0;
    status = "AMAN";
    digitalWrite(ledRed, LOW);
    digitalWrite(ledGreen, HIGH);
  }
  else
  {
    if (badPosture == 0) badPosture = millis();

    if (millis() - badPosture > threshold)
    {
      status = "STANDBY";
      digitalWrite(ledRed, LOW);
      digitalWrite(ledGreen, LOW);
    }
    else
    {
      status = "JAUH";
      digitalWrite(ledRed, LOW);
      digitalWrite(ledGreen, HIGH);
    }
  }

  Serial.print(currentDist);
  Serial.print(",");
  Serial.println(status);

  delay(100);
}

void calibrate()
{
  digitalWrite(ledGreen, LOW);
  digitalWrite(ledRed, LOW);

  long total = 0;
  int validReadings = 0;

  for (int i = 0; i < 10; i++)
  {
    int reading = sonar.ping_cm();
    if (reading > 0)
    {
      total += reading;
      validReadings++;
    }
    
    Serial.print(reading);
    Serial.print(",");
    Serial.println("CALIBRATING");
    
    digitalWrite(ledRed, HIGH);
    delay(50);
    digitalWrite(ledRed, LOW);
    delay(50);
  }

  if (validReadings > 0)
  {
    idealDistance = total / validReadings;
  }
  else
  {
    idealDistance = 0;
  }

  digitalWrite(ledGreen, HIGH);
  Serial.print(idealDistance);
  Serial.print(",");
  Serial.println("CALIBRATED");
  delay(1000);
}
