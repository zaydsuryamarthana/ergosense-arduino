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
      trigger();
    } 
    else 
    {
      status = "WARNING";
    }
  }
  else if (currentDist >= (idealDistance - tolerance) && currentDist <= (idealDistance + tolerance + 20))
  {
    status = "AMAN";
    reset();
  }
  else
  {
    if (badPosture == 0) badPosture = millis();

    if (millis() - badPosture > threshold)
    {
      status = "STANDBY";
      standby();
    }
    else
    {
      status = "JAUH";
      trigger();
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

  for (int i = 10; i > 0; i--)
  {
    Serial.print("0,CALIB_"); 
    Serial.println(i);

    digitalWrite(ledRed, HIGH);
    delay(200);
    digitalWrite(ledRed, LOW);
    delay(800);
  }

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
    delay(100);
    digitalWrite(ledRed, LOW);
    delay(100); 
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

void trigger(){
  digitalWrite(ledGreen, LOW);
  digitalWrite(ledRed, HIGH);
}

void reset(){
  badPosture = 0;
  digitalWrite(ledRed, LOW);
  digitalWrite(ledGreen, HIGH);
}

void standby(){
  digitalWrite(ledRed, LOW);
  digitalWrite(ledGreen, LOW);
}
