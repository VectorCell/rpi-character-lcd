/*
 * read_dht11.c
 * 
 * adapted from code from
 * http://www.circuitbasics.com/how-to-set-up-the-dht11-humidity-sensor-on-the-raspberry-pi/
 * 
 */

#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <wiringPi.h>

#define P_DATA      0
#define MAXTIMINGS 85

bool read_dht11_dat (int data[5])
{
	uint8_t laststate	= HIGH;
	uint8_t counter		= 0;
	uint8_t j		= 0, i;

	data[0] = data[1] = data[2] = data[3] = data[4] = 0;

	pinMode( P_DATA, OUTPUT );
	digitalWrite( P_DATA, LOW );
	delay( 18 );
	digitalWrite( P_DATA, HIGH );
	delayMicroseconds( 40 );
	pinMode( P_DATA, INPUT );

	for ( i = 0; i < MAXTIMINGS; i++ ) {
		counter = 0;
		while ( digitalRead( P_DATA ) == laststate ) {
			counter++;
			delayMicroseconds( 1 );
			if ( counter == 255 )
			{
				break;
			}
		}
		laststate = digitalRead( P_DATA );

		if ( counter == 255 )
			break;

		if ( (i >= 4) && (i % 2 == 0) ) {
			data[j / 8] <<= 1;
			if ( counter > 16 )
			data[j / 8] |= 1;
			j++;
		}
	}

	if ( (j >= 40) && (data[4] == ( (data[0] + data[1] + data[2] + data[3]) & 0xFF) ) ) {
		return true;
	} else  {
		return false;
	}
}

int main (int argc, char *argv[])
{
	if (wiringPiSetup() == -1) {
		fprintf(stderr, "ERROR: unable to read gpio");
		return 1;
	}

	int data[5] = {0, 0, 0, 0, 0};
	while (!read_dht11_dat(data)) {
		// unsuccessful read, trying again
		delay(10);
	}

	float f = data[2] * 9. / 5. + 32;
	printf("%d.%d °C (%.1f °F)\n", data[2], data[3], f);
	printf("%d.%d %% relative humidity\n", data[0], data[1]);

	return 0;
}
