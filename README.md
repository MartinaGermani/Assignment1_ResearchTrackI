# Assignment1 - Python Robotics Simulator
This is a simple, portable robot simulator developed by [Student Robotics](https://studentrobotics.org).
Some of the arenas and the exercises have been modified for the Research Track I course

## Installing and running

The simulator requires a Python 2.7 installation, the [pygame](http://pygame.org/) library, [PyPyBox2D](https://pypi.python.org/pypi/pypybox2d/2.1-r331), and [PyYAML](https://pypi.python.org/pypi/PyYAML/).


## Troubleshooting

When running `python run.py <file>`, you may be presented with an error: `ImportError: No module named 'robot'`. This may be due to a conflict between sr.tools and sr.robot. To resolve, symlink simulator/sr/robot to the location of sr.tools.

On Ubuntu, this can be accomplished by:
* Find the location of srtools: `pip show sr.tools`
* Get the location. In my case this was `/usr/local/lib/python2.7/dist-packages`
* Create symlink: `ln -s path/to/simulator/sr/robot /usr/local/lib/python2.7/dist-packages/sr/`

## How to run: 

To run one or more scripts in the simulator, use `run.py`, passing it the file names: 


```bash
$ python run.py assignment1.py
```

## Assignment1's aim: ##

The aim of this first assignment is to drive the robot around the circuit in the counter-clockwise direction avoiding to touch the golden boxes, and to grab silver box when the robot is close to it and move it behind itself.


## Robot API

The API for controlling a simulated robot is designed to be as similar as possible to the [SR API][sr-api].

### Motors ###
-----------------------------
The simulated robot has two motors configured for skid steering, connected to a two-output [Motor Board](https://studentrobotics.org/docs/kit/motor_board). The left motor is connected to output `0` and the right motor to output `1`.

The Motor Board API is identical to [that of the SR API](https://studentrobotics.org/docs/programming/sr/motors/), except that motor boards cannot be addressed by serial number. So, to turn on the spot at one quarter of full power, one might write the following:

```python
R.motors[0].m0.power = 25
R.motors[0].m1.power = -25
```

### The Grabber ###
-----------------------------
The robot is equipped with a grabber, capable of picking up a token which is in front of the robot and within 0.4 metres of the robot's centre. To pick up a token, call the `R.grab` method:

```python
success = R.grab()
```

The `R.grab` function returns `True` if a token was successfully picked up, or `False` otherwise. If the robot is already holding a token, it will throw an `AlreadyHoldingSomethingException`.

To drop the token, call the `R.release` method.

Cable-tie flails are not implemented.

### Vision ###
-----------------------------
To help the robot find tokens and navigate, each token has markers stuck to it, as does each wall. The `R.see` method returns a list of all the markers the robot can see, as `Marker` objects. The robot can only see markers which it is facing towards.

Each `Marker` object has the following attributes:

* `info`: a `MarkerInfo` object describing the marker itself. Has the following attributes:
  * `code`: the numeric code of the marker.
  * `marker_type`: the type of object the marker is attached to (either `MARKER_TOKEN_GOLD`, `MARKER_TOKEN_SILVER` or `MARKER_ARENA`).
  * `offset`: offset of the numeric code of the marker from the lowest numbered marker of its type. For example, token number 3 has the code 43, but offset 3.
  * `size`: the size that the marker would be in the real game, for compatibility with the SR API.
* `centre`: the location of the marker in polar coordinates, as a `PolarCoord` object. Has the following attributes:
  * `length`: the distance from the centre of the robot to the object (in metres).
  * `rot_y`: rotation about the Y axis in degrees.
* `dist`: an alias for `centre.length`
* `res`: the value of the `res` parameter of `R.see`, for compatibility with the SR API.
* `rot_y`: an alias for `centre.rot_y`
* `timestamp`: the time at which the marker was seen (when `R.see` was called).

For example, the following code lists all of the markers the robot can see:

```python
markers = R.see()
print "I can see", len(markers), "markers:"

for m in markers:
    if m.info.marker_type in (MARKER_TOKEN_GOLD, MARKER_TOKEN_SILVER):
        print " - Token {0} is {1} metres away".format( m.info.offset, m.dist )
    elif m.info.marker_type == MARKER_ARENA:
        print " - Arena marker {0} is {1} metres away".format( m.info.offset, m.dist )
```

[sr-api]: https://studentrobotics.org/docs/programming/sr/

### How to detect silver token? ###
-----------------------------
The first problem to solve was the fact that the robot, having a complete view (-180 degrees to 180 degrees), used to go back to grab the silver box already taken (if closer).
So to get around this problem, I have reduced the robot's search view for silver boxes to 120 degrees (-60 degrees to 60 degrees). 
In this way the robot can only detect the silver box in front of it. 

Therefore in the function `find_silver_token` you can find this code:

```python
for token in R.see():
     if token.dist < dist and token.info.marker_type is MARKER_TOKEN_SILVER and -60<token.rot_y<60:
            dist=token.dist
	    rot_y=token.rot_y
```

### Explanetion of `function_control_boundaries(rot_y)` ###
-----------------------------
This function was created for avoiding that the robot could turn itself in the worst direction. 
In fact this function takes into consideration two situations in which the robot might find itself, relative to the angles of the path.
To explain how it works, I report below an image:

![alt text](https://github.com/MartinaGermani/Assignment1_ResearchTrackI/blob/main/imm.jpg?raw=true)

As you can see, if the angle between the robot and the golden token is included between 60 degrees to 180 degrees, it means that the robot is in the first situation, and so it must turn left.
On the other hand, if the angle between the robot and the golden token is included between -180 degrees to -60 degrees, it means that the robot is in the second situation, and so it must turn right.

Below the code written:
```python
	if 60<rot_y<180:
		print("angolo, giro a sinistra!")
		turn(-2,3)
		
	elif -180<rot_y<-60:
		print("angolo, giro a destra!") 
		turn(2,3)

```
So, in this way, the robot always turns in the correct direction and avoids going back.

### PSEUDO-CODE: ###
-----------------------------
In the code `assignment1.py` you can find an infinite while loops, within which there are different sections, which are explained below:

### 1. if dist_silver==-1: ###
-----------------------------
CALLING THE `find_silver_token` function
IF NO SILVER TOKEN IS DETECTED, THEN the robot has to move around the arena in search of one of them, SO:

	CALLING THE `function_control_boundaries(rot_y_gold)`, WHERE:
	IF the angle between the robot and the golden token is included between 60 degrees to 180 degrees, THEN:
		 THE ROBOT MUST TURN LEFT
	ELIF the angle between the robot and the golden token is included between -180 degrees to -60 degrees, THEN: 
		 THE ROBOT MUST TURN RIGHT
		 
	CALLING THE `looking_for_silver_token(rot_y_amoung, dist_gold_amoung)` function, WHERE:
		 IF the angle between the robot and the golden token in front of it is less than -2 (on the left) AND the distance between the robot and this golden token is less than 0.7, THEN:
		 	THE ROBOT TURNS RIGHT
	 	 ELIF the angle between the robot and the golden token in front of it is bigger than 2 (on the right) AND the distance between the robot and the golden token is less than 0.7. THEN:
	         	THE ROBOT TURNS LEFT
		 ELIF the robot is well aligned with the golden token in front of it AND the distance between the robot and the golden token is less than 0.7, THEN:
		 	THE ROBOT COMES BACK FOR 2 SECONDS
		 	CONTROL THE NEAREST GOLDEN TOKEN AROUNG AND IN FRONT OF IT
 		 	IF the nearest golden token in front of it is on the left, then:
       			THE ROBOT TURNS RIGHT
       		ELIF the nearest golden token in front of it is on the right, then:
       			THE ROBOT TURNS LEFT
   		ELSE:
   			THE ROBOT GOES ON FOR 1 SECOND
   	
	CONTROL SILVER BOX AND THE NEAREST GOLDEN BOXES AROUND AND IN FRONT OF IT
	
### 2. if dist_silver <d_th and -a_th<= rot_y_silver <= a_th: ###
-----------------------------
IF A SILVER BOX IS CLOSER AND THE ROBOT IS WELL ALIGNED WITH IT, THEN:

	THE ROBOT GRABS THE SILVER TOKEN
	THE ROBOT MOVES FORWARD AND ON THE RIGHT
	THE ROBOT RELEASES THE SILVER TOKEN
	THE ROBOT GOES BACK TO THE INITIAL POSITION
	CONTROL THE NEAREST GOLDEN BOXES AROUND AND IN FRONT OF IT
	
	WHILE the distance between the robot and the golden token is bigger that 0.4 (threshold), THEN:
		 CALLING THE `after_grab(rot_y_gold, dist_gold)` function, WHERE:
		 	IF the robot is well aligned with the golden token AND it's closer, THEN:
		 		THE ROBOT COMES BACK FOR 2 SECONDS
		 	ELSE:
		 		THE ROBOT GOES ON FOR 0.5 SECONDS
		 		DETECTS THE NEW NEAREST GOLDEN TOKEN
		 	
		 		IF the angle between the robot and the golden token is less than -2 AND the distance between the robot and the golden token is bigger than 0.6, THEN:
		 			THE ROBOT TURNS RIGHT
		 			THE ROBOT GOES ON FOR 0.5 SECONDS
			 	ELIF the angle between the robot and the golden token is bigger than 2 AND the distance between the robot and the golden token is bigger than 0.6, THEN:
			 		THE ROBOT TURNS LEFT
			 		THE ROBOT GOES ON FOR 0.5 SECONDS
			        ELIF the robot is well aligned with the golden token AND the distance between the robot and the golden token is bigger than 0.6, THEN:
			 		THE ROBOT COMES BACK FOR 2 SECONDS
		 CONTROL THE NEAREST GOLDEN BOXES AROUND AND IN FRONT OF IT
		 SUBTRACTS 0.35 (a little less than the threshold) FROM THE DETECTED DISTANCE BETWEEN THE ROBOT AND THE NEAREST GOLDEN TOKEN
	SILVER==FALSE
 	
 	WHILE SILVER==FALSE:
 		CALLING `function_control_boundaries(rot_y)`, WHERE:
 			IF the angle between the robot and the golden token is included between 60 degrees to 180 degrees, THEN:
		 		THE ROBOT MUST TURN LEFT
	        	ELIF the angle between the robot and the golden token is included between -180 degrees to -60 degrees, THEN: 
		 		THE ROBOT MUST TURN RIGHT
 		
 		CALLING `control_golden_token(rot_y_gold, 2)` function, WHERE:
 			IF the nearest golden token is at left, THEN:
       			THE ROBOT TURNS RIGHT
       		ELIF the nearest golden token is at right, THEN:
       			THE ROBOT TURNS LEFT
       		ELIF the robot is well aligned with the nearest golden token, THEN:
       			THE ROBOT COMES BACK FOR 2 SECONDS
       		ELIF the angle between the robot and the golden token is equal to 90 degrees or equal to -90 degrees, THEN:
       			THE ROBOT GOES ON FOR 3 SECONDS
       		ELSE:
       			THE ROBOT GOES ON FOR 0.5 SECONDS
       			
       	CONTROL THE NEAREST SILVER BOX AND THE NEAREST GOLDEN BOXES AROUND AND IN FRONT OF IT
       		
	        IF a silver block has been detected AND there is not a golden token between them, THEN:
		 	SILVER=TRUE


### 3. elif -a_th<= rot_y_silver <= a_th: ###
-----------------------------
IF the robot is well aligned with the token AND there is not golden token between the robot and the silver token, then:

	IT DETECTS IF THERE ARE GOLDEN BOXES AROUND OR IN FRONT OF IT
	
       1. WHILE the silver token is not closer AND there is not a golden box between the robot and the silver token AND the angle between the robot and the golden token is between -90 degrees to 90 degrees, 		then:
	       THE ROBOT GOES ON FOR 1 SECOND
	       CONTROL THE NEAREST SILVER BOX AND THE NEAREST GOLDEN BOXES AROUND AND IN FRONT OF IT


       2. WHILE the silver token is not closer AND there is a golden box between the robot and the silver token, then:
       	CALLING `aligned_but(rot_y_amoung)` function, WHERE:
       		IF the nearest golden token is at left, then:
       			THE ROBOT TURNS RIGHT
       		ELIF the nearest golden token is at right, then:
       			THE ROBOT TURNS LEFT
       		ELIF the robot is well aligned with the nearest golden token, then:
       			THE ROBOT COMES BACK FOR 2 SECONDS
       		ELSE:
       			THE ROBOT GOES ON FOR 0.5 SECONDS
       	CONTROL THE NEAREST SILVER BOX AND THE NEAREST GOLDEN BOXES AROUND AND IN FRONT OF IT


### 4. elif rot_y_silver < -a_th and dist_gold_amoung>d_th: ###
-----------------------------
IF the robot is NOT well aligned with the silver token (in particular the silver token in on the LEFT with respect to the robot), THEN:
	
	CALLING `control_orientation_distance(rot_y_gold, dist_gold, orientation)` function, WHERE:
		 IF the angle between the robot and the golden token is less than -2 (the golden box is on the left) AND the distance between the robot and the golden token is less than the threshold, then:
			 	THE ROBOT TURNS RIGHT
	 	 ELIF the angle between the robot and the golden token is bigger than 2 (the golden box is on the right) AND the distance between the robot and the golden token is less than the threshold, 			 then:
			 	THE ROBOT TURNS LEFT
		 ELIF the robot is well aligned with the nearest golden token, then:
			 	THE ROBOT COMES BACK FOR 2 SECONDS
		 ELSE: 
			 	THE ROBOT TURNS LEFT


### 5. elif rot_y_silver > a_th and dist_gold_amoung>d_th: ###
-----------------------------
IF the robot is not well aligned with the silver token (in particular the silver token in on the RIGHT with respect to the robot), THEN:

	CALLING `control_orientation_distance(rot_y_gold, dist_gold, orientation)` function, WHERE:
		 IF the angle between the robot and the golden token is less than -2 (the golden box is on the left) AND the distance between the robot and the golden token is less than the threshold, then:
			 	THE ROBOT TURNS RIGHT
		 ELIF the angle between the robot and the golden token is bigger than 2 (the golden box is on the right) AND the distance between the robot and the golden token is less than the threshold, 			 then:
			 	THE ROBOT TURNS LEFT
		 ELIF the robot is well aligned with the nearest golden token AND the distance between the robot and the golden token is less than the threshold, then:
			 	THE ROBOT COMES BACK FOR 2 SECONDS
		 ELSE: 
			 	THE ROBOT TURNS RIGHT

### 6. if dist_silver>=4: ###
-----------------------------
IF the distance between the robot and the silver token is bigger or equal than 4, THEN:

	WHILE the distance between the robot and the silver token is bigger than 1 AND there is a golden token between them, THEN:
		 CALLING `control_golden_token(rot_y_gold, seconds)` function, WHERE:
		 	IF the nearest golden token is at left, then:
       			THE ROBOT TURNS RIGHT
       	 	ELIF the nearest golden token is at right, then:
       			THE ROBOT TURNS LEFT
       	 	ELIF the robot is well aligned with the nearest golden token, then:
       			THE ROBOT COMES BACK FOR 2 SECONDS
       		ELIF the robot is parallel to the closer golden token, then: 
       			THE ROBOT GOES ON FOR 3 SECONDS
       	 	ELSE:
       	 		THE ROBOT GOES ON FOR 1 SECOND
       	 		
       	 CONTROL THE NEAREST SILVER BOX AND THE NEAREST GOLDEN BOXES AROUND AND IN FRONT OF IT
       
       
       WHILE the distance between the robot and the silver token is bigger than 1 AND there is not a golden token between them, THEN:
       	THE ROBOT GOES ON FOR 2 SECONDS
       	CALLING `control_golden_token(rot_y_gold, seconds)` function, WHERE:
       		IF the nearest golden token is at left AND the distance between the robot and the golden token is bigger than 0.6, THEN:
       			THE ROBOT TURNS RIGHT
       		ELIF the nearest golden token is at right AND the distance between the robot and the golden token is bigger than 0.6, THEN:
       			THE ROBOT TURNS LEFT
       		ELIF the robot is well aligned with the nearest golden token AND the distance between the robot and the golden token is bigger than 0.6, THEN:
       			THE ROBOT COMES BACK FOR 2 SECONDS
       		ELIF the robot is parallel to the closer golden token, then: 
       			THE ROBOT GOES ON FOR 3 SECONDS
       		ELSE:
       	 		THE ROBOT GOES ON FOR 1 SECOND
       	 		
       	CONTROL THE NEAREST SILVER BOX AND THE NEAREST GOLDEN BOXES AROUND AND IN FRONT OF IT
