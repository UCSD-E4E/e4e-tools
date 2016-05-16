////////////////////////////////PIN ASSIGNMENT///////////////////////////////////
#define THCLK   A1
#define THCS    A2
#define THSO    A3
#define SSR     5

// Defines
#define TARGET_TEMP 40
#define SOAK_TIME 300
#define RAMP_SPEED 0.1

// Includes
#include <MAX31855.h>
#include <avr/interrupts.h>

double setPoint, input, kp = 40, ki = 1, kd = -100;
double error = 0;
double integral = 0;
double derivative = 0;
double previous = 0;
int16_t output = 0;
uint32_t time = 0;
uint8_t state = 0;

MAX31855 thermocouple (THSO, THCS, THCLK);

void setup(){
    pinMode(SSR, OUTPUT);
    Serial.begin(57600);

    setPoint = thermocouple.readThermocouple(CELSIUS);

}

void loop(){
    input = thermocouple.readThermocouple(CELSIUS);
    if((input == FAULT_OPEN) || (input == FAULT_SHORT_GND) || (input == FAULT_SHORT_VCC)){
        Serial.println("THERMOCOUPLE ERROR");
        return;
    }
    error = setPoint - input;
    derivative = input - previous;
    if(state == 1 && input > 0.9 * TARGET_TEMP){
        integral += error;
        if(integral > 300){
            Serial.println("Integral Windup!");
            integral = 300;
        }
        if(integral < -300){
            integral = 300;
        }
    }
    output = kp * error + ki * integral + kd * derivative;
    if(output > 1000){
        output = 1000;
    }
    if(output < 0){
        output = 0;
    }
    if(error < 0){
        output = 0;
    }
    if(input > TARGET_TEMP * 1.1){
        output = 0;
        Serial.println("WARNING!!! OVERHEAT WARNING!!!");
        pinMode(6, OUTPUT);
        digitalWrite(6, HIGH);
    }
    if(input < TARGET_TEMP * 1.1){
        digitalWrite(6, LOW);
    }
    if(error > 5 || error < -5){
    Serial.print(millis());
    Serial.print('\t');
    Serial.print(input);
    Serial.print('\t');
    Serial.print(error);
    Serial.print('\t');
    Serial.print(derivative);
    Serial.print('\t');
    Serial.print(output);
    Serial.print('\t');
    Serial.print(setPoint);
    Serial.print('\t');
    Serial.print(integral);
    Serial.print('\t');
    Serial.print(state);

    Serial.print('\n');
    }
    previous = input;
    digitalWrite(SSR, HIGH);
    delay(output);
    digitalWrite(SSR, LOW);
    delay(1000 - output);
    if(state == 0){
        setPoint += RAMP_SPEED;
    }
    if(setPoint >= TARGET_TEMP && state == 0){
        state = 1;
        setPoint = TARGET_TEMP;
    }
    if(state == 1){
        time ++;
    }
    if(time > SOAK_TIME && state == 1){
        state++;
    }
    if(state == 2){
        if(setPoint > 65){
            setPoint -= RAMP_SPEED;
        }
    }
    if(state == 2 && input < 65){
        state ++;
    }
    if(state == 3){
        pinMode(6, OUTPUT);
        digitalWrite(6, HIGH);
        delay(1000);
        digitalWrite(6, LOW);
    }

}
