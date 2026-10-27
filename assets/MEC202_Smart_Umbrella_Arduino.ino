#include <SoftwareSerial.h>
#include <TinyGPS++.h>
#include <Wire.h>
#include <MPU6050.h>

// 软串口定义
SoftwareSerial air780Serial(10, 11); // RX, TX (10接Air780EX的TX, 11接Air780EX的RX)
SoftwareSerial gpsSerial(7, 8);      // GPS模块 RX (7)，TX (8)

TinyGPSPlus gps;
MPU6050 mpu;

const int buzzerPin = 9;    // 蜂鸣器引脚
const int buttonPin = 6;    // 按键信号引脚（注意别用7, 7已连GPS）
bool detectionEnabled = false;  // 是否启用加速度检测
const float movementThreshold = 0.5;  // 加速度阈值

void setup() {
    Serial.begin(9600);
    air780Serial.begin(9600);
    gpsSerial.begin(9600);

    Wire.begin();
    mpu.initialize();

    pinMode(buzzerPin, OUTPUT);
    digitalWrite(buzzerPin, LOW);

    pinMode(buttonPin, INPUT);

    if (mpu.testConnection()) {
        Serial.println("MPU6050 连接成功");
    } else {
        Serial.println("MPU6050 连接失败，请检查接线");
        while (1);
    }

    Serial.println("按键控制加速度检测 (按下启用/关闭)");

    // 配置 GPS 模块只输出 RMC 数据
    gpsSerial.println("$PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*29");
    delay(1000);

    sendATCommand("AT+CGATT=1", 2000);
    sendATCommand("AT+CSTT", 2000);
    sendATCommand("AT+CIICR", 3000);
    sendATCommand("AT+CIFSR", 2000);

    Serial.println("Air780EX 已连接，开始获取 GPS...");
}

void loop() {
    handleButton();

    if (detectionEnabled) {
        detectMovement();
    }

    while (gpsSerial.available()) {
        char c = gpsSerial.read();
        gps.encode(c);
    }

    if (gps.location.isUpdated()) {
        float lat = gps.location.lat();
        float lon = gps.location.lng();
        Serial.print("lat: "); Serial.println(lat, 6);
        Serial.print("lon: "); Serial.println(lon, 6);

        gpsSerial.println("$PMTK314,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*28");
        delay(3000);
        while (gpsSerial.available()) { gpsSerial.read(); }
        Serial.println("GPS 清空缓冲区");

        air780Serial.listen();
        while (air780Serial.available()) { air780Serial.read(); }

        String gpsData = "{\"lat\": " + String(lat, 6) + ", \"lon\": " + String(lon, 6) + "}";
        int len = gpsData.length();
        Serial.print("gpsData 长度: "); Serial.println(len);

        delay(5000);

        sendATCommand("AT+CSQ", 100);
        sendATCommand("AT+CGATT?", 200);
        sendATCommand("AT+CIFSR", 500);

        sendATCommand("AT+HTTPSSL=1", 100);
        sendATCommand("AT+HTTPSSL?", 100);
        sendATCommand("AT+HTTPINIT", 5000);
        sendATCommand("AT+HTTPPARA=\"URL\",\"https://gps-signal.glitch.me/gps\"", 4000);
        sendATCommand("AT+HTTPPARA=\"CONTENT\",\"application/json\"", 2000);

        delay(2000);
        checkURL();

        sendATCommand("AT+HTTPDATA=" + String(gpsData.length()) + ",20000", 5000);
        delay(5000);
        air780Serial.println(gpsData);

        sendATCommand("AT+HTTPACTION=1", 5000);
        delay(1000);
        sendATCommand("AT+HTTPREAD", 3000);
        sendATCommand("AT+HTTPTERM", 1000);

        gpsSerial.listen();
        gpsSerial.println("$PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*29");
        delay(500);
        delay(5000);
    }
}

void handleButton() {
    static bool lastButtonState = HIGH;
    bool buttonState = digitalRead(buttonPin);

    if (buttonState == LOW && lastButtonState == HIGH) {
        detectionEnabled = !detectionEnabled;
        Serial.println(detectionEnabled ? "加速度检测已启用" : "加速度检测已关闭");
        delay(200);
    }
    lastButtonState = buttonState;
}

void detectMovement() {
    int16_t ax, ay, az;
    mpu.getAcceleration(&ax, &ay, &az);

    float ax_g = ax / 16384.0;
    float ay_g = ay / 16384.0;
    float az_g = az / 16384.0;
    float totalAcc = sqrt(ax_g * ax_g + ay_g * ay_g + az_g * az_g);

    Serial.print("加速度: ");
    Serial.println(totalAcc);

    if (totalAcc > 1.0 + movementThreshold || totalAcc < 1.0 - movementThreshold) {
        Serial.println("警报！雨伞被移动！");
        digitalWrite(buzzerPin, HIGH);
        delay(2000);
        digitalWrite(buzzerPin, LOW);
    }
}

void sendATCommand(String cmd, int waitTime) {
    air780Serial.println(cmd);
    Serial.print("发送命令: "); Serial.println(cmd);

    unsigned long startTime = millis();
    while (millis() - startTime < waitTime) {
        while (air780Serial.available()) {
            char c = air780Serial.read();
            Serial.write(c);
        }
    }
}

void checkURL() {
    sendATCommand("AT+HTTPPARA?", 4000);
}












// gps 信号测试代码

// #include <SoftwareSerial.h>

// // 设置串口
// SoftwareSerial gpsSerial(7, 8);  // 连接到 GPS 模块的串口

// void setup() {
//   // 初始化串口
//   Serial.begin(9600);  // 与电脑的串口通信
//   gpsSerial.begin(9600);  // 与 GPS 模块的通信

//   Serial.println("GPS 模块已初始化，正在读取原始数据...");

//   gpsSerial.println("$PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*29");

  
//   delay(10000);  // 给 GPS 模块一点时间
// }

// void loop() {
//   // 读取 GPS 数据并直接打印
//   while (gpsSerial.available()) {
//     char c = gpsSerial.read();  // 读取一个字符
//     Serial.write(c);  // 打印该字符到串口
    
//   }
// }



// //  air780ex测试

// SoftwareSerial airSerial(10, 11); // RX, TX

// void setup() {
//   Serial.begin(9600);        // 电脑串口监视器
//   airSerial.begin(9600);     // 软串口，连接 Air780EX

//   delay(1000);
  
//   Serial.println("Starting Air780EX Test with SoftwareSerial...\n");

//   // // 检查 AT 是否正常
//   sendATCommand("AT");
//   sendATCommand("AT+HTTPINIT");
//   sendATCommand("AT+HTTPACTION=0");

//   // 查看信号强度
//   sendATCommand("AT+CSQ");

//   // 检查是否附着到网络
//   sendATCommand("AT+CGATT?");

//   // 设置 APN（你可以修改这里的 cmnet）
//   sendATCommand("AT+CSTT");

//   // 激活网络
//   sendATCommand("AT+CIICR");

//   // 获取 IP 地址
//   sendATCommand("AT+CIFSR");

//   // Serial.println("Initialization done.\n");
// }

// void loop() {
//   // 可选：把模块返回的数据实时打印到监视器
//   if (airSerial.available()) {
//     char c = airSerial.read();
//     Serial.write(c);
//   }
// }

// void sendATCommand(String command) {
//   Serial.print("Sending: ");
//   Serial.println(command);
  
//   airSerial.println(command);  // 发命令给模块
  
//   unsigned long startTime = millis();
//   while (millis() - startTime < 5000) {  // 最多等5秒响应
//     while (airSerial.available()) {
//       char c = airSerial.read();
//       Serial.write(c);  // 打印模块返回内容
//     }
//   }

//   Serial.println("\n-----------------------------\n");
// }
