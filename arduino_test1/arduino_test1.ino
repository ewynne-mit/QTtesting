const int pumpPin = 6;
const int airPin = 7;
const int valvePin = 8;

int incomingByte;

void setup() {
  Serial.begin(9600);
  pinMode(pumpPin,OUTPUT);
  pinMode(airPin,OUTPUT);
  pinMode(valvePin,OUTPUT);

  digitalWrite(pumpPin,LOW)
  digitalWrite(airPin,LOW)
  digitalWrite(valvePin,LOW)

}

void loop() {
  if (Serial.available() > 0){
    incomingByte = Serial.read();
  }

  if(incomingByte == 'R'){
    digitalWrite(pumpPin,HIGH)
    delay(500)
    digitalWrite(pumpPin,LOW)
  }

  if(incomingByte =='E'{
    digitalWrite(pumpPin,HIGH)
    delay(100)
    digitalWrite(valvePin,HIGH)
    digitalWrite(airPin,HIGH)
  }

  if(incomingByte =='S'{
    digitalWrite(airPin,LOW)
    digitalWrite(valvePin,LOW)
  }

}
