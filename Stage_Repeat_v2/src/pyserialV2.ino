int valve1 = 12;
int valve2 = 13;

String rx1; // received valve 1 status
String rx2; // received valve 2 status

void setup() {
  Serial.begin(9600); // set the baud rate
  Serial.println("1"); // write random string to tell python it is ready
  pinMode(valve1,OUTPUT);
  pinMode(valve2, OUTPUT);
}

void loop()
{
  while (!Serial.available()) {} // wait for data to arrive
  
  rx1 = Serial.readStringUntil('\n'); // serial read section: valve 1 status
  rx2 = Serial.readStringUntil('\n'); // serial read section: valve 2 status
  
  valveOperation (rx1); // operate valve 1
  valveOperation (rx2); // operate valve 2
  
  rx1 = ""; // reset valve 1 received status
  rx2 = ""; // reset valve 2 received status

  delay(500); // give python time to read
  Serial.flush(); // clear serial port
}

void valveOperation (String rx) {
  // operate valve with status
  if (rx == "12HIGH") {
    digitalWrite(valve1,HIGH);
    Serial.println("valve 1 energized");
  }
  else if (rx == "13HIGH") {
    digitalWrite(valve2,HIGH);
    Serial.println("valve 2 energized");
  }
  else if (rx == "12LOW") {
    digitalWrite(valve1,LOW);
    Serial.println("valve 1 denergized");
  }
  else if (rx == "13LOW") {
    digitalWrite(valve2,LOW);
    Serial.println("valve 2 denergized");
  }
  else if (rx == "EXIT") {
    digitalWrite(valve1,LOW);
    digitalWrite(valve2,LOW);
  }
  else {
    Serial.println("Error");
  }
}
