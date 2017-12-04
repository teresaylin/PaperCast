
//////////
/////////  All Serial Handling Code,
/////////  It's Changeable with the 'outputType' variable
/////////  It's declared at start of code.
/////////

void serialOutput(){   // Decide How To Output Serial.
  switch(outputType){
    case PROCESSING_VISUALIZER:
      //sendDataToSerial('S', Signal);     // goes to sendDataToSerial function
      Serial.println(BPM);
      break;
    case SERIAL_PLOTTER:  // open the Arduino Serial Plotter to visualize these data
//      Serial.write(BPM);
      Serial.print(BPM);
      Serial.print(",");
      Serial.print(IBI);
      Serial.print(",");
      Serial.println(Signal);
      break;
    default:
      break;
  }

}

//  Decides How To OutPut BPM and IBI Data
void serialOutputWhenBeatHappens(){
  switch(outputType){
    case PROCESSING_VISUALIZER:    // find it here https://github.com/WorldFamousElectronics/PulseSensor_Amped_Processing_Visualizer
//      sendDataToSerial('B',BPM);   // send heart rate with a 'B' prefix
//      sendDataToSerial('Q',IBI);   // send time between beats with a 'Q' prefix
        Serial.println(BPM);
      break;

    default:
      break;
  }
}

//  Sends Data to Pulse Sensor Processing App, Native Mac App, or Third-party Serial Readers.
void sendDataToSerial(char symbol, int data ){
    Serial.print(symbol);
    Serial.println(data);
  }
