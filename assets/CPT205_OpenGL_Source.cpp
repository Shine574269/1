// File ID: coursework1.cpp
// Title:
// Author:
#define FREEGLUT_STATIC
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <GL/freeglut.h>
#include <cmath>
#include <time.h>

typedef struct { GLfloat x, y; } point; // define a 2D point
point p0 = { 0,50 }; // set initial co-ordinate values of the point
GLfloat finishx = 300; // declare position of vertical axis

// Draw a rectangle (grass, cake layers, cream, and candles)
void drawRectangle(GLfloat x, GLfloat y, GLfloat width, GLfloat height, GLfloat r, GLfloat g, GLfloat b) {
	glColor3f(r, g, b);
	glBegin(GL_POLYGON);
	glVertex2f(x - width / 2, y); // bottom left
	glVertex2f(x + width / 2, y); // bottom right
	glVertex2f(x + width / 2, y + height); // top right
	glVertex2f(x - width / 2, y + height); // top left
	glEnd();
}

// Draw a circle
void drawCircle(float x, float y, float radius1, float radius2, int num_segments) {
	glBegin(GL_TRIANGLE_FAN);
	glVertex2f(x, y);
	for (int i = 0; i <= num_segments; i++) {
		float angle = 2.0 * 3.14159 * i / num_segments;
		glVertex2f(x + radius1 * cos(angle), y + radius2 * sin(angle));
	}
	glEnd();
}

GLfloat bgColor[4] = { 0.5, 0.8, 1.0, 1.0 }; // Initial background color
GLfloat grassColor[3] = { 0.6, 1.0, 0.6 }; // Initial grass color
bool isDarkMode = false; // State variable, indicating whether it's light mode or dark mode

// Grass
void drawGrass() {
	drawRectangle(300, 0, 600, 280, grassColor[0], grassColor[1], grassColor[2]);
}

bool drawSunFlag = true; // Flag to control whether the sun is drawn

// Draw the sun
void drawSun(float x, float y) {
	if (drawSunFlag) {
		// Set the color of sun rays (orange)
		glColor3f(1, 0.7, 0.5);

		// Draw multiple sun rays
		for (int i = 0; i < 10; ++i) {
			float angle = 2.0f * 3.14159265358979f * i / 10;
			float petalX = x + 60 * cos(angle);
			float petalY = y + 90 * sin(angle);

			glBegin(GL_TRIANGLE_FAN);
			glVertex2f(petalX, petalY); // center
			int segments = 50; // number of segments to approximate a circle
			for (int j = 0; j <= segments; ++j) {
				float segmentAngle = 2.0f * 3.14159f * j / segments;
				float dx = 6 * cos(segmentAngle);
				float dy = 10 * sin(segmentAngle);
				glVertex2f(petalX + dx, petalY + dy);
			}
			glEnd();
		}
		// Set the color of the sun center (red)
		glColor3f(1, 0.2, 0.2);
		// Draw the sun center
		glBegin(GL_TRIANGLE_FAN);
		drawCircle(x, y, 30, 50, 80);
	}
}

// Initial transformation parameters
float translateX = 0.0f;
float translateY = 0.0f;
float rotationAngle = 0.0f;
float scale = 1.0f;

// Butterfly
void drawButterfly(float x, float y) {
	glPushMatrix(); // Save the current transformation state

	// Apply transformations
	glTranslatef(translateX, translateY, 0.0f);
	glRotatef(rotationAngle, 0, 0, 1);
	glScalef(scale, scale, 1.0f);

	// Draw the butterfly
	// Draw butterfly wings
	glColor3f(1, 1, 0.5);
	glBegin(GL_TRIANGLE_FAN);
	drawCircle(x - 15, y + 20, 15, 40, 80);
	drawCircle(x - 10, y - 25, 10, 20, 80);
	drawCircle(x + 15, y + 20, 15, 40, 80);
	drawCircle(x + 10, y - 25, 10, 20, 80);

	// Draw the middle part of the butterfly wings
	glColor3f(1, 0.8, 0.5);
	drawCircle(x, y, 5, 55, 80);

	// Draw the butterfly antennae
	glColor3f(1, 0.5, 0.5);
	drawCircle(x + 5, y + 70, 3, 6, 80);
	drawCircle(x - 5, y + 70, 3, 6, 80);

	glPopMatrix(); // Restore to the previous transformation state
}


// Character count
const int CharacterCount = 13;
float CharacterX[CharacterCount] = { 170, 190,210, 230, 250,290,310,330,350,370,390,410,430 }; // Horizontal positions of characters
float CharacterY[CharacterCount] = { 780, 780, 780, 780, 780, 780 ,780, 780, 780, 780, 780, 780,780 }; // Initial vertical positions of characters
float CharacterChar[CharacterCount] = { 'H', 'A', 'P', 'P', 'Y', 'B' ,'I', 'R', 'T', 'H', 'D', 'A','Y' }; // Characters
// Colors for each character (R, G, B)
float CharacterColors[CharacterCount][3] = {
	{1.0, 0.8, 0.9}, // Soft pink
	{0.8, 1.0, 0.8}, // Light rose pink
	{1.0, 0.7, 0.7}, // Coral red
	{1.0, 1.0, 0.6}, // Light yellow
	{1.0, 0.8, 0.6}, // Light orange
	{0.9, 0.6, 1.0}, // Light purple
	{1.0, 0.8, 0.9}, // Soft pink
	{0.8, 1.0, 0.8}, // Light rose pink
	{1.0, 0.7, 0.7}, // Coral red
	{1.0, 1.0, 0.6}, // Light yellow
	{1.0, 0.8, 0.6}, // Light orange
	{0.9, 0.6, 1.0}, // Light purple
	{1.0, 0.8, 0.6}, // Light orange
};

// Jump offsets
float jumpOffsets[CharacterCount] = { 0 };
const float upperLimit = 16.0; // Highest point
const float lowerLimit = -16.0; // Lowest point
int directions[CharacterCount] = { 1,-1,1,-1,1,-1,1,-1,1,-1,1,-1,1 }; // Movement directions, 1 for up, -1 for down

// Update animation
void updateChar(int value) {
	for (int i = 0; i < CharacterCount; ++i) {
		jumpOffsets[i] += directions[i] * 4; // Update offsets based on direction
		// Check if reaching the upper or lower limit, change direction
		if (jumpOffsets[i] >= upperLimit) {
			directions[i] = -1; // Change to move down
		}
		else if (jumpOffsets[i] <= lowerLimit) {
			directions[i] = 1; // Change to move up
		}
	}

	glutPostRedisplay(); // Refresh the screen
	glutTimerFunc(50, updateChar, 0);

}

// Draw character function
void drawCharacter(float x, float y, char c, float color[3]) {
	glColor3f(color[0], color[1], color[2]); // Set character color
	glRasterPos2f(x, y); // Set character drawing position
	glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, c);
}


// Flowers
const int FlowerCount = 8; // Number of flowers
float FlowerX[FlowerCount] = { 50, 75, 120, 160, 450, 500, 530, 580 }; // Horizontal positions of flowers
float FlowerY[FlowerCount] = { 220, 100, 200, 150, 200, 100, 220, 150 }; // Initial vertical positions of flowers
float FlowerSize[FlowerCount] = { 6, 9, 5, 7, 10, 8, 5, 5 }; // Sizes of flowers

// Global variable for animation
float angleOffset = 0.0; // Angle offset for rotation


// Draw flowers
void drawFlower(float x, float y, float petalSize) {
	// Set petal color (pink)
	glColor3f(1, 0.5, 0.5);

	// Draw multiple petals
	for (int i = 0; i < 5; ++i) {
		float angle = 2.0f * 3.14159265358979f * i / 5 + angleOffset;
		float petalX = x + 1 * petalSize * cos(angle);
		float petalY = y + 1.6 * petalSize * sin(angle);

		// Draw a circle (petal)
		glBegin(GL_TRIANGLE_FAN);
		glVertex2f(petalX, petalY); // center
		int segments = 50; // number of segments to approximate a circle
		for (int j = 0; j <= segments; ++j) {
			float segmentAngle = 2.0f * 3.14159f * j / segments;
			float dx = 0.8 * petalSize * cos(segmentAngle);
			float dy = 1.3 * petalSize * sin(segmentAngle);
			glVertex2f(petalX + dx, petalY + dy);
		}
		glEnd();
	}

	// Set the color of the flower center (yellow)
	glColor3f(1, 1, 0.6);
	// Draw the flower center
	glBegin(GL_TRIANGLE_FAN);
	glVertex2f(x, y); // center
	int segments = 50; // number of segments to approximate a circle
	for (int j = 0; j <= segments; ++j) {
		float segmentAngle = 2.0f * 3.14159f * j / segments;
		float dx = 0.6 * petalSize * cos(segmentAngle);
		float dy = petalSize * sin(segmentAngle);
		glVertex2f(x + dx, y + dy);
	}
	glEnd();
}


// Update animation
void updateFlower(int value) {
	angleOffset += 5;
	if (angleOffset > 2 * 3.14159265358979) {
		angleOffset -= 2 * 3.14159265358979; // Prevent angle overflow
	}
	glutPostRedisplay(); // Request redrawing
	glutTimerFunc(16, updateFlower, 0);
}

// Balloons
const int balloonCount = 6; // Number of balloons
float balloonX[balloonCount] = { 50, 400, 200, 450, 500, 550 }; // Horizontal positions of balloons
float balloonY[balloonCount] = { 550, 450, 680, 650, 400, 600 }; // Initial vertical positions of balloons
float balloonSize[balloonCount] = { 2, 1, 1.5, 1, 1.2, 1.8 }; // Sizes of balloons
bool balloonMoving[balloonCount] = { false, false, false, false, false, false }; // Whether balloons are moving upwards

// Colors for each balloon (R, G, B)
float balloonColors[balloonCount][3] = {
	{1.0, 0.8, 0.9}, // Soft pink
	{0.8, 1.0, 0.8}, // Light rose pink
	{1.0, 0.7, 0.7}, // Coral red
	{1.0, 1.0, 0.6}, // Light yellow
	{1.0, 0.8, 0.6}, // Light orange
	{0.9, 0.6, 1.0}, // Light purple
};

// Function to draw a circular balloon
void drawBalloonCircle(float x, float y, float size) {
	int numSegments = 60; // Number of segments to approximate a circle
	glBegin(GL_TRIANGLE_FAN);
	glVertex2f(x, y); // Center of the circle
	for (int i = 0; i <= numSegments; i++) {
		float angle = 2.0 * 3.14159 * i / numSegments;
		float dx = size * 7.0 * cos(angle); // Scale using size parameter
		float dy = size * 15.0 * sin(angle);
		glVertex2f(x + dx, y + dy);
	}
	glEnd();
}

// Function to draw a single balloon
void drawBalloon(float x, float y, float color[3], float size) {
	// Draw balloon (heart shape)
	glColor3f(color[0], color[1], color[2]); // Set balloon color
	// Draw upper part of the heart (circular part)
	drawBalloonCircle(x, y, size);
	drawBalloonCircle(x + size * 9, y, size);

	// Draw the tip of the heart (triangular part)
	glBegin(GL_TRIANGLES);
	glVertex2f(x - size * 5.5, y - size * 10); // Left point
	glVertex2f(x + size * 14.5, y - size * 10); // Right point
	glVertex2f(x + size * 4, y - size * 35); // Top point
	glEnd();

	// Draw the curved string of the balloon
	glColor3f(1, 1, 1); // White string
	glLineWidth(1.48); // Line width of the string

	// Bezier curve control points
	float x0 = x + size * 4, y0 = y - size * 35;
	float controlPoints[4][2] = {
		{x - size * 10.0, y - size * 60.0},
		{x + size * 25.0, y - size * 70.0},
		{x - size * 15.0, y - size * 80.0},
		{x + size * 10.0, y - size * 100.0}
	};

	glBegin(GL_LINE_STRIP);
	for (float t = 0; t <= 1.0; t += 0.05) {
		float xt = pow(1 - t, 4) * x0 +
			4 * pow(1 - t, 3) * t * controlPoints[0][0] +
			6 * pow(1 - t, 2) * t * t * controlPoints[1][0] +
			4 * (1 - t) * t * t * t * controlPoints[2][0] +
			t * t * t * t * controlPoints[3][0];
		float yt = pow(1 - t, 4) * y0 +
			4 * pow(1 - t, 3) * t * controlPoints[0][1] +
			6 * pow(1 - t, 2) * t * t * controlPoints[1][1] +
			4 * (1 - t) * t * t * t * controlPoints[2][1] +
			t * t * t * t * controlPoints[3][1];

		glVertex2f(xt, yt);
	}
	glEnd();

	glLineWidth(1.0); // Restore line width
}

// Timer function for continuous upward movement of balloons
void updateBalloon(int value) {
	for (int i = 0; i < balloonCount; i++) {
		if (balloonMoving[i]) {
			balloonY[i] += 5.0f; // Make the balloon move upwards

			// Check if the balloon has gone off-screen
			if (balloonY[i] > 1200) {
				balloonMoving[i] = false; // Stop the upward movement of the balloon
			}
		}
	}

	glutPostRedisplay(); // Refresh the screen

	// Set the next timer
	glutTimerFunc(16, updateBalloon, 0); // Call updateBalloon every 16 milliseconds
}

// Cloud
void drawCloud(float x, float y) {
	glColor3f(1, 1, 1); // White

	// Draw multiple circles for the cloud
	drawCircle(x, y, 55, 55, 80);
	drawCircle(x - 20, y + 40, 25, 30, 80);
	drawCircle(x - 20, y - 40, 20, 30, 80);
	drawCircle(x + 20, y - 40, 20, 25, 80);
	drawCircle(x + 20, y + 40, 20, 25, 80);

	// Draw eyes
	glColor3f(0, 0, 0); // Black
	drawCircle(x - 15, y + 10, 4, 8, 50);
	drawCircle(x + 15, y + 10, 4, 8, 50);

	// Draw a smile
	glBegin(GL_LINE_STRIP);
	for (int i = -10; i <= 10; i++) {
		float x_offset = i * 1.0;
		float y_offset = -2.0 * sqrt(10 - (i * i));
		glVertex2f(x_offset + x, y_offset + y + 7);
	}
	glEnd();

	// Draw blush
	glColor3f(1, 0.7, 0.7); // Light pink
	drawCircle(x - 25, y - 5, 8, 14, 80);
	drawCircle(x + 25, y - 5, 8, 14, 80);
}


// Stars
bool drawStarFlag = false;
bool isStarVisible = true; // Whether the star is visible

// General function to draw a star
void drawStar(float centerX, float centerY, float size, int points) {
	if (drawStarFlag) {
		if (!isStarVisible) return; // Return directly if the star is not visible

		glColor3f(1.0, 1.0, 0.0); // Star color: yellow
		glBegin(GL_TRIANGLE_FAN);
		glVertex2f(centerX, centerY); // Star center

		for (int i = 0; i < points + 1; i++) {
			// Calculate outer points
			float angleOuter = 2 * 3.14159 * i / points;
			float dxOuter = size * cos(angleOuter);
			float dyOuter = (9.0 / points) * size * sin(angleOuter);

			// Calculate inner points
			float angleInner = 2 * 3.14159 * (i + 0.5) / points;
			float dxInner = size * 0.1 * points * cos(angleInner);
			float dyInner = size * 0.16 * points * sin(angleInner);

			// Draw outer and inner points
			glVertex2f(centerX + dxOuter, centerY + dyOuter);
			glVertex2f(centerX + dxInner, centerY + dyInner);
		}
		glEnd();
	}
}

// Five-pointed star
void drawStar1(float centerX, float centerY, float size) {
	drawStar(centerX, centerY, size, 5); // 5-pointed star
}

// Four-pointed star
void drawStar2(float centerX, float centerY, float size) {
	drawStar(centerX, centerY, size, 4); // 4-pointed star
}

// Timer function to update the star's visibility
void updateStar(int value) {
	isStarVisible = !isStarVisible; // Toggle the star's visibility
	glutPostRedisplay(); // Request redrawing
	glutTimerFunc(500, updateStar, 0); // Call every 500 milliseconds
}

// Draw a cake
void drawCake(GLfloat x, GLfloat y) {
	// Draw the bottom layer of the cake
	drawRectangle(x, y, 200.0f, 230.0f, 0.9f, 0.7f, 0.5f); // Bottom layer of the cake
	drawRectangle(x, y + 175, 200.0f, 55.0f, 1.0f, 1.0f, 1.0f); // Cream bottom layer

	// Draw the middle layer of the cake
	drawRectangle(x, y + 230, 150.0f, 170.0f, 1.0f, 0.75f, 0.6f); // Middle layer of the cake
	drawRectangle(x, y + 350, 150.0f, 50.0f, 1.0f, 1.0f, 1.0f); // Cream middle layer

	// Draw the top layer of the cake
	drawRectangle(x, y + 400, 90.0f, 140.0f, 1.0f, 0.8f, 0.6f); // Top layer of the cake
	drawRectangle(x, y + 500, 90.0f, 40.0f, 1.0f, 1.0f, 1.0f); // Cream top layer

	// Draw candles
	GLfloat candleWidth = 8.0f, candleHeight[] = { 80.0f, 105.0f, 80.0f };
	GLfloat candleXOffsets[] = { -24.0f, 0.0f, 24.0f }; // Candle's X coordinate offset
	for (int i = 0; i < 3; ++i) {
		drawRectangle(x + candleXOffsets[i], y + 540, candleWidth, candleHeight[i], 1.0f, 0.87f, 0.6f);
	}
}

// Draw flame
float flameOpacity = 1.0f; // Initial opacity

void drawFlame(float x, float y) {
	glColor4f(1.0f, 0.8f, 1.0f, flameOpacity);

	// Draw the lower part of the flame
	glBegin(GL_TRIANGLE_FAN);
	glVertex2f(x - 24, y + 645); // Center of the flame
	int numSegments = 60; // Number of segments to approximate a circle
	for (int i = 0; i <= numSegments; i++) {
		float angle = 2.0 * 3.14159 * i / numSegments;
		float dx = 5.0 * cos(angle);
		float dy = 15.0 * sin(angle);
		glVertex2f(x - 24 + dx, y + 645 + dy);
	}
	glEnd();

	// Draw the tip of the flame
	glBegin(GL_TRIANGLES);
	glVertex2f(x - 28, y + 653); // Left point
	glVertex2f(x - 20, y + 653); // Right point
	glVertex2f(x - 24, y + 668); // Top point
	glEnd();
}

GLfloat messageY = 1200; // Initial y-coordinate of the message (above the window)
// Draw a message
void drawMessage(GLfloat x, GLfloat y, GLfloat width, GLfloat height) {
	glColor3f(0.0, 0.6, 0.0); // Green
	glRasterPos2f(x - 30, y + 40); // Set text position
	const char* message = "Forever 18";
	for (const char* c = message; *c != '\0'; c++) {
		glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, *c); // Draw each character
	}
}

// Mouse click event handling
void mouseClick(int button, int state, int x, int y) {
	if (button == GLUT_LEFT_BUTTON && state == GLUT_DOWN) {
		// Decrease opacity each time the left button is clicked
		flameOpacity -= 0.1f;
		if (flameOpacity < 0.0f) {
			flameOpacity = 0.0f; // Ensure opacity does not go below 0
		}
		glutPostRedisplay(); // Request redrawing
	}
	else if (button == GLUT_RIGHT_BUTTON && state == GLUT_DOWN) {
		drawSunFlag = !drawSunFlag;
		drawStarFlag = !drawStarFlag;
		// Toggle colors
		if (!isDarkMode) {
			// Switch to dark mode
			bgColor[0] = 0.0;
			bgColor[1] = 0.0;
			bgColor[2] = 0.0;

			grassColor[0] = 0.0; // Dark green
			grassColor[1] = 0.5;
			grassColor[2] = 0.0;
		}
		else {
			// Switch back to light mode
			bgColor[0] = 0.5; // Light blue
			bgColor[1] = 0.8;
			bgColor[2] = 1.0;

			grassColor[0] = 0.0; // Light green
			grassColor[1] = 1.0;
			grassColor[2] = 0.6;
		}

		isDarkMode = !isDarkMode; // Toggle the state
		glutPostRedisplay(); // Request redrawing
	}
}

// Keyboard key callback function
void keyboard(unsigned char key, int x, int y) {
	switch (key) {
	case ' ':
		for (int i = 0; i < balloonCount; i++) {
			balloonMoving[i] = true; // Make the balloons start moving upwards
		}
		break;
	case 'w': // Move up
		translateY += 5.0f;
		break;
	case 's': // Move down
		translateY -= 5.0f;
		break;
	case 'a': // Move left
		translateX -= 5.0f;
		break;
	case 'd': // Move right
		translateX += 5.0f;
		break;
	case 'r': // Rotate
		rotationAngle += 10.0f;
		break;
	case 'R': // Rotate in the opposite direction
		rotationAngle -= 10.0f;
		break;
	case 'q': // Zoom in
		scale += 0.1f;
		break;
	case 'e': // Zoom out
		scale -= 0.1f;
		if (scale < 0.1f) scale = 0.1f; // Prevent excessive zoom out
		break;
	case 13:
		messageY = 400; // Reset the position of the message
		break;
	case 27: // ESC key to exit
		exit(0);
	}
	glutPostRedisplay(); // Request redrawing
}

// TASK 7
void display(void)
{
	// Set up the projection matrix and clear the color buffer
	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
	gluOrtho2D(0, 600, 0, 1100);
	glClearColor(bgColor[0], bgColor[1], bgColor[2], bgColor[3]);
	glClear(GL_COLOR_BUFFER_BIT);
	glColor3f(1, 1, 1);
	glBegin(GL_LINES);
	glVertex2f(finishx, 50);
	glVertex2f(finishx, 350);
	glEnd();

	// Grass
	drawGrass();

	// Sun
	drawSun(150, 950);

	// Flowers
	for (int i = 0; i < FlowerCount; i++) {
		drawFlower(FlowerX[i], FlowerY[i], FlowerSize[i]);
	}

	// Balloons
	for (int i = 0; i < balloonCount; i++) {
		if (balloonY[i] <= 1200) { // Only draw balloons that have not left the screen
			drawBalloon(balloonX[i], balloonY[i], balloonColors[i], balloonSize[i]);
		}
	}

	// Draw a cloud at a specific position
	drawCloud(400, 930);

	// Draw stars
	drawStar1(250, 930, 10);
	drawStar1(300, 970, 20);
	drawStar1(20, 950, 5);
	drawStar1(100, 920, 8);
	drawStar1(560, 1000, 7);
	drawStar1(80, 1050, 5);
	drawStar1(220, 1050, 5);
	drawStar1(50, 1010, 10);
	drawStar2(500, 980, 15);
	drawStar2(510, 1000, 5);
	drawStar2(150, 1020, 15);
	drawStar2(163, 1008, 6);
	drawStar2(173, 1005, 4);

	// Draw a cake
	drawCake(300.0, 0.0);  // Cake position

	// Draw flame
	drawFlame(300.0, 0.0);
	drawFlame(324.0, 20.0);
	drawFlame(348.0, 0.0);
	glFlush();

	// Characters
	for (int i = 0; i < CharacterCount; i++) {
		drawCharacter(CharacterX[i], CharacterY[i] + jumpOffsets[i], CharacterChar[i], CharacterColors[i]);
	}
	glFlush();

	drawButterfly(140, 420);

	// Draw a message
	drawMessage(300, messageY, 100, 100); // Draw a rectangular message at position (300, messageY)

	glutSwapBuffers();
}

int main(int argc, char** argv)
{
	srand(time(0));
	glutInit(&argc, argv);
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB);
	glutInitWindowPosition(100, 50);
	glutInitWindowSize(900, 700);
	glutCreateWindow("My Interactive Window");
	glutDisplayFunc(display);
	glutKeyboardFunc(keyboard);
	glutMouseFunc(mouseClick);
	glEnable(GL_BLEND);// Enable blending
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA); // Set blending function

	// Start the timers
	glutTimerFunc(500, updateStar, 0); // Call every 500 milliseconds
	glutTimerFunc(50, updateFlower, 0); // Call every 50 milliseconds
	glutTimerFunc(50, updateChar, 0); // Call every 50 milliseconds
	glutTimerFunc(50, updateBalloon, 0); // Call every 50 milliseconds

	glutMainLoop();
}
