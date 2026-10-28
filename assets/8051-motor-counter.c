#include <reg51.h>

/* 7-segment display control pins */
sbit P3_3 = P3^3;
sbit P3_4 = P3^4;
sbit P0_7 = P0^7;

/* Motor control pins */
sbit MOTOR_A = P3^0;
sbit MOTOR_B = P3^1;

/* 7-segment codes for digits 0-9 */
unsigned char code digitCode[10] = {
    0xC0, // 0
    0xF9, // 1
    0xA4, // 2
    0xB0, // 3
    0x99, // 4
    0x92, // 5
    0x82, // 6
    0xF8, // 7
    0x80, // 8
    0x90  // 9
};

/* Four digits shown on 7-segment display */
unsigned char displayDigits[4] = {0, 0, 0, 0};

/* Motor revolution count and calculated frequency */
unsigned int R = 0;
unsigned int frequency = 0;

/* Simple display delay */
void delay(void)
{
    unsigned int i;
    for(i = 0; i < 800; i++);
}

/* Select one of the four 7-segment digit positions */
void selectDigit(unsigned char pos)
{
    if(pos == 0)        // first digit: leftmost
    {
        P3_4 = 1;
        P3_3 = 1;
    }
    else if(pos == 1)   // second digit
    {
        P3_4 = 1;
        P3_3 = 0;
    }
    else if(pos == 2)   // third digit
    {
        P3_4 = 0;
        P3_3 = 1;
    }
    else                // fourth digit: rightmost
    {
        P3_4 = 0;
        P3_3 = 0;
    }
}

/* Convert a number 0-9999 into four display digits */
void setDisplayNumber(unsigned int num)
{
    if(num > 9999)
    {
        num = 9999;
    }

    displayDigits[0] = num / 1000;
    displayDigits[1] = (num / 100) % 10;
    displayDigits[2] = (num / 10) % 10;
    displayDigits[3] = num % 10;
}

/* Refresh the four 7-segment displays */
void displayNumber(void)
{
    unsigned char i;

    for(i = 0; i < 4; i++)
    {
        P0_7 = 0;                          // turn off display
        P1 = 0xFF;                         // clear segments

        selectDigit(i);                    // select digit position
        P1 = digitCode[displayDigits[i]];  // set digit pattern
        P0_7 = 1;                          // enable display

        delay();

        P0_7 = 0;                          // turn off before next digit
        P1 = 0xFF;                         // clear segments
    }
}

/* Timer 0 interrupt: measurement window */
void timer0_ISR(void) interrupt 1
{
    unsigned long tempFreq;

    TR0 = 0;        // stop Timer 0
    TR1 = 0;        // stop Counter 1

    /* Read 16-bit motor revolution count from Counter 1 */
    R = TH1 * 256 + TL1;

    /*
       Timer 0 initial value = 0x2176
       Measurement window:
       65536 - 0x2176 = 56970 us, about 57 ms

       frequency = R / 0.057
                 = R * 1000 / 57
    */
    tempFreq = (unsigned long)R * 1000;
    frequency = tempFreq / 57;

    /*
       Display scaled frequency to avoid overflow.
       Actual frequency is approximately 100 times the displayed value.
       Example: display 0123 means actual frequency is about 12300 Hz.
    */
    setDisplayNumber(frequency / 100);

    /* Reset Counter 1 */
    TH1 = 0x00;
    TL1 = 0x00;

    /* Reload Timer 0 using student ID last four digits: 2176 */
    TH0 = 0x21;
    TL0 = 0x76;

    TR1 = 1;        // restart Counter 1
    TR0 = 1;        // restart Timer 0
}

void main(void)
{
    /* Initial display value */
    setDisplayNumber(0);

    /*
       TMOD = 0x51

       Timer 1:
       GATE = 0
       C/T  = 1, counter mode
       M1 M0 = 01, Mode 1, 16-bit counter

       Timer 0:
       GATE = 0
       C/T  = 0, timer mode
       M1 M0 = 01, Mode 1, 16-bit timer
    */
    TMOD = 0x51;

    /* Timer 0 initial value based on ID digits 2176 */
    TH0 = 0x21;
    TL0 = 0x76;

    /* Reset Counter 1 */
    TH1 = 0x00;
    TL1 = 0x00;

    /* Enable Timer 0 interrupt and global interrupt */
    IE = 0x82;

    /* Start motor */
    MOTOR_A = 1;
    MOTOR_B = 0;

    /* Start Counter 1 and Timer 0 */
    TR1 = 1;
    TR0 = 1;

    while(1)
    {
        displayNumber();
    }
}