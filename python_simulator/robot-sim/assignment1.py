from __future__ import print_function

import time
from sr.robot import *


"""ASSIGNMENT1:
The aim of this assignment is to drive the robot (with view from -180 degrees to 180 degrees) around the circuit in the counter-clockwise direction, avoiding to touch the golden boxes grabbing the silver box when it is closer, and then the robot has to move it behind itself """



""" float: Threshold for the control of the orientation"""
a_th = 2.0

""" float: Threshold for the control of the linear distance"""
d_th = 0.4

""" boolean: variable for letting the robot know if it has to look for a silver or for a golden marker"""
silver = True

""" instance of the class Robot"""
R = Robot()


def drive(speed, seconds):
    """
    Function for setting a linear velocity
    
    Args: speed (int): the speed of the wheels
	  seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0


def turn(speed, seconds):
    """
    Function for setting an angular velocity
    
    Args: speed (int): the speed of the wheels
	  seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = -speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0


def find_silver_token():
    """
    Function to find the closest silver token

    Returns:
	dist (float): distance of the closest silver token (-1 if no silver token is detected)
	rot_y (float): angle between the robot and the silver token (-1 if no silver token is detected)
    """
    
    """
    I set 120 degrees (from -60 degrees to 60 degrees) as the robot view for silver tokens: in this way the robot can only detect the silver box in front of it, and it doesn't go back to grab the silver box 	   already taken (if closer).
    """
    dist=100
    for token in R.see():
        if token.dist < dist and token.info.marker_type is MARKER_TOKEN_SILVER and -60<token.rot_y<60:
            dist=token.dist
	    rot_y=token.rot_y
    if dist==100:
	return -1, -1
    elif rot_y<-90 or rot_y>90:
    	return -1,-1
    else:
   	return dist, rot_y


def find_golden_token():
    """
    Function to find the closest golden token

    Returns:
	dist (float): distance of the closest golden token (-1 if no golden token is detected)
	rot_y (float): angle between the robot and the golden token (-1 if no golden token is detected)
    """
    """
     I set 180 degrees (from -90 degrees to 90 degrees) as the robot view for golden tokens: in this way the robot doesn't care about the golden boxes behind it
    """
    
    dist=100
    for token in R.see():
        if token.dist < dist and token.info.marker_type is MARKER_TOKEN_GOLD and -90<token.rot_y<90:
            dist=token.dist
	    rot_y=token.rot_y
    if dist==100:
	return -1, -1
    else:
   	return dist, rot_y


def find_golden_token_amoung():
    """
    Function to find the closest golden token in front of the robot

    Returns:
	dist (float): distance of the closest golden token in front of the robot (-1 if no golden token is detected)
	rot_y (float): angle between the robot and the golden token in front of it(-1 if no golden token is detected)
    """
    
    """
    I set 60 degrees (from -30 degrees to 30 degrees) as the robot view for golden tokens in front of it: in this way the robot can detect if there is a closer golden token in front of it between the robot 	  itself and the silver token detected
    """
    dist=100
    for token in R.see():
        if token.dist < dist and token.info.marker_type is MARKER_TOKEN_GOLD and -30<token.rot_y<30:
            dist=token.dist
	    rot_y=token.rot_y
    if dist==100:
	return -1, -1
    else:
   	return dist, rot_y


def function_control_boundaries(rot_y):
    """
    This function was created for avoiding that the robot could turn itself in the worst direction when it moves in the circuit, so:

    - if the angle between the robot and the golden token is included between 60 degrees to 180 degrees, the robot must turn left,

    -if the angle between the robot and the golden token is included between -180 degrees to -60 degrees, the robot must turn right.

    """
    print("control boundaries ...")
    if 60<rot_y<180:
		print("angle, turn left!")
		turn(-2,3)
		
    elif -180<rot_y<-60:
		print("angle, turn right!") 
		turn(2,3)


def looking_for_silver_token(rot_y_amoung, dist_gold_amoung):
	"""
	This function was created for looking for a closer silver token:
	"""
	print("looking for silver token ...")
	
	if rot_y_amoung < -a_th and dist_gold_amoung<(d_th+0.3): #If the golden token in front of the robot is closer and on the left respect to it, then the robot turns right a little
        	print("turn a little to the right");
        	turn(+2, 0.5)
        	
        elif rot_y_amoung > a_th and dist_gold_amoung<(d_th+0.3): #If the golden token in front of the robot is closer and on the right respect to it, then the robot turns left a little
        	print("turn a little to the left");
        	turn(-2,0.5)
        						
        elif -a_th<= rot_y_amoung <= a_th and dist_gold_amoung<(d_th+0.3): #If the golden token in front of the robot is closer and well aligned with it, then the robot goes back a little
        	print("go back!")
   		drive(-20,2)
   		
   		dist_gold, rot_y_gold = find_golden_token() #control if there is a closer golden token around it
   		dist_gold_amoung, rot_y_amoung=find_golden_token_amoung() #control if there is a closer golden token in front of it
   		
   		if rot_y_amoung < -a_th: #If the golden token in front of the robot is closer and on the left respect to it, then the robot turns right a little
        		print("turn a little to the right");
        		turn(+2, 1)
        							
        	elif rot_y_amoung > a_th: #If the golden token in front of the robot is closer and on the right respect to it, then the robot turns left a little
        		print("turn a little to the left");
        		turn(-2,1)
   								
   	else: 				#Otherwise the robot goes on
		drive(10,1)


def control_golden_token(rot_y_gold, seconds):
	"""
	This function allows to control golden tokens around the robot while it drives in search of a new silver token:
	"""
	print("control golden token ..")
	if rot_y_gold<-a_th:	#If the closer golden token is on the left respect to the robot, then it turns right a little
   		print("turn right")
   		turn(+2,seconds)
   	elif rot_y_gold>a_th:	#If the closer golden token is on the right respect to the robot, then it turns left a little
   		print("turn left")
   		turn(-2,seconds)
   	elif -a_th<= rot_y_gold <= a_th:	#If the closer golden token is well aligned with the robot, then it goes back a little
   		print("go back")
   		drive(-20,2)
   	elif rot_y_gold ==90 or rot_y_gold==-90: #If the robot is parallel to the closer golden token, it goes on for 3 seconds
   		print("go on")
   		drive(20,3)	
   	else:				#Otherwise, the robot goes on for 1 second
   		print("go on")
   		drive(10,1)
   		
   		
def control_orientation_distance(rot_y_gold, dist_gold, orientation):
	"""
	This function controls that, when the robot wants to turn (i.e right), there is not a closer golden token, in that direction, that it could touch. If that happens, so the robot has to turn in the 		opposite direction:
	"""
	print("control orientation and distance ...")
	if rot_y_gold < -a_th and dist_gold<d_th: #If the closer golden token is on the left respect to the robot, then it turns right a little
		print("turn right")
        	turn(+2, 0.5)
        elif rot_y_gold > a_th and dist_gold<d_th: #If the closer golden token is on the right respect to the robot, then it turns left a little
        	print("turn left")
        	turn(-2,0.5)
        elif -a_th<= rot_y_gold <= a_th: #If the closer golden token is well aligned with the robot, then it goes back a little
        	print("go back")
   		drive(-20,2)
        else: 				#Otherwise, it turns in the direction of the silver token
        	print("turn of", orientation)
        	turn(orientation,0.5)


def after_grab(rot_y_gold, dist_gold):
	"""
	After releasing the silver token and returning to place, while the robot is away from the golden boxes, it moves forward always checking the angles and the distances with respect to them. 
	In fact, with these controls, and thanks to other controls, the robot doesn't touch golden tokens.
	"""
	print("after grabbing ...")
	if -a_th<= rot_y_gold <= a_th and dist_gold<=0.5: #If the robot is well aligned with golden box and this is closer, then the robot has to go back for 2 seconds and turn a little
        	print("go back")
   		drive(-20,2)
   		turn(-2,0.5)
	else: 						    #Otherwise the robot drives and then controls the angle and the distance with respect to closest golden token.
   		drive(40,0.5)
   		dist_gold, rot_y_gold=find_golden_token()
   		
   		if rot_y_gold < -a_th and dist_gold>0.6:  #If the golden token is closer and on the left respect to the robot, then the robot turns right a little
        		print("turn a little to right and then go on");
        		turn(+2, 1)
        		drive(10,0.5)
        	elif rot_y_gold > a_th and dist_gold>0.6: #If the golden token is closer and on the right respect to the robot, then the robot turns left a little
        		print("turn a little to left and then go on");
        		turn(-2,1)
        		drive(10,0.5)	
        	elif -a_th<= rot_y_gold <= a_th and dist_gold>0.6: #If the golden token is closer and well aligned respect to the robot, then the robot goes back a little
        		print("go back")
   			drive(-20,2)

def aligned_but(rot_y_amoung):
	"""
	This function is called when the robot is well aligned with a silver token but there is a golden token between them. 
	So in this condition, the robot has to turn in the opposite direction and then it has to go on in order to move away from the golden token
	"""
	print("aligned but ... ops a golden token ...")
	if rot_y_amoung < -a_th:  #If the golden token in front of the robot is on the left respect to it, then the robot goes a little back, then turns right and then goes on
        	print("turn right and then go on")
        	drive(-20,1) # it goes a little back to avoid touching possible closer goldent tokens
        	turn(+2, 10)
        	drive(10,7)
        elif rot_y_amoung > a_th: #If the golden token in front of the robot is on the right respect to it, then the robot goes a little back, then turns left and then goes on
        	print("turn left and then go on")
        	drive(-20,1) # it goes a little back to avoid touching possible closer goldent tokens
        	turn(-2,10)	
        	drive(10,7)
        elif -a_th<= rot_y_amoung <= a_th: #If the golden token in front of the robot is aligned with it, then the robot goes back a little
        	print("go back a little")
   		drive(-20,2)
   	else:				  #Otherwise, the robot goes on a little
   		print("go on a little")
   		drive(10,0.5)





while 1:	
	silver=True
	
	dist_silver, rot_y_silver= find_silver_token() #control if there is a closer silver token
	dist_gold, rot_y_gold = find_golden_token() #control if there is a closer golden token
	dist_gold_amoung, rot_y_amoung=find_golden_token_amoung() #control if there is a closer golden token in front of the robot
	
	
	"""
	If no silver token is detected, the robot has to move in the circuit in search of one of them:
	"""
	if dist_silver==-1: 
			print("I don't see any silver token!!")
			
			function_control_boundaries(rot_y_gold) #First control boundaries
	
			looking_for_silver_token(rot_y_amoung, dist_gold_amoung) #Start looking for a silver token
			
			dist_gold, rot_y_gold = find_golden_token() #control if there is a closer golden token
			dist_silver, rot_y_silver= find_silver_token() #control if there is a closer silver token
			dist_gold_amoung, rot_y_amoung=find_golden_token_amoung() #control if there is a closer golden token in front of the robot
	
		
	"""
	If the robot is well aligned with a silver token and it is closer to it, so it must grab it:
	"""			
        if dist_silver <d_th and -a_th<= rot_y_silver <= a_th: 
        		if silver==True:
        			if R.grab(): # if we grab the token, we move the robot forward and on the right, we release the token, and we go back to the initial position	 	
            				print("Gotcha!")
            				
	    				turn(20, 2)
	    				turn(10,2)
	    				R.release() #release the silver token
	    				turn(-20,2)
	    				turn(-10,1.6)
	    				
	    				dist_gold, rot_y_gold=find_golden_token() #control if there is a closer golden token
	    				dist_gold_amoung, rot_y_amoung=find_golden_token_amoung() #control if there is a closer golden token in front of the robot
	    				
	    				"""
	    				After grabbing, while the robot is not closer to a golden token, it goes on:
	    				"""
	    				while dist_gold>d_th:
						
						after_grab(rot_y_gold, dist_gold) 	
        			
   						dist_gold, rot_y_gold=find_golden_token()  #control if there is a closer golden token
   						dist_gold_amoung, rot_y_amoung=find_golden_token_amoung() #control if there is a closer golden token in front of the robot
   				
						dist_gold=dist_gold-0.35; #in this way the robot avoids to touch golden box when it drives
						
   					silver=not silver #once the robot has exited from the while loop, silver = False, so as to identify a new silver token
   					
   					"""
   					While silver==False, the robot turn and drive in order to detect a new silver token:
   					"""
   					while silver==False:
   							
   							function_control_boundaries(rot_y_gold)
   							
   							control_golden_token(rot_y_gold, 2)
   							
   							dist_silver, rot_y_silver=find_silver_token() #control if there is a closer silver token
   							dist_gold, rot_y_gold=find_golden_token() #control if there is a closer golden token
   							dist_gold_amoung, rot_y_gold_amoung = find_golden_token_amoung() #control if there is a closer golden token in front of the robot
   							
   							print("dist_silver= ", dist_silver)
   							print("dist_gold_amoung= ", dist_gold_amoung)
   
   							"""
   							If a silver token is detected and there is not a golden token between the robot and the silver token (in front of the robot), then
   							that silver token is considered valid
   							"""
   							if dist_silver!=-1 and dist_gold_amoung>=1: 
   								silver=True
   									
   								
   								
   	
   	""" If the robot is well aligned with a silver token, it has to get close to it, but it's important that there are not golden boxes between them: """						
	if -a_th<= rot_y_silver <= a_th:
				print("Ah, that'll do.")
				dist_gold, rot_y_gold=find_golden_token() #control if there is a closer golden token
				dist_gold_amoung, rot_y_amoung= find_golden_token_amoung() #control if there is a closer golden token in front of the robot
					
				"""
				While the silver token is not closer and there are not closer golden tokens between the silver token and the robot, it goes on:
				"""
				while dist_gold_amoung>1 and dist_silver>d_th and -90<rot_y_amoung<90:
					print("Green light, go on!")
						
					drive(20,1)
						
					dist_silver, rot_y_silver = find_silver_token()
        				dist_gold_amoung, rot_y_amoung= find_golden_token_amoung()
        				dist_gold, rot_y_gold=find_golden_token()
        					
				"""
				While, instead, the robot is well aligned with a silver token that is not yet closer to it, but there is a golden token between them, the robot has to turn in the 					opposite direction and go on, in order to avoid to touch it:
				"""
        			while dist_gold_amoung<1 and dist_silver>d_th:
        				
        				aligned_but(rot_y_amoung)
        						
   					dist_gold, rot_y_gold=find_golden_token()
   					dist_silver, rot_y_silver = find_silver_token()
   					dist_gold_amoung, rot_y_amoung= find_golden_token_amoung()
   	
   	"""
   	If the robot is not well aligned with the silver token, in particular the token is on the left, the robot has to turn left, but it's important to control also golden tokens in order to avoid to 		touch them when it turns:
   	"""				
    	if rot_y_silver < -a_th and dist_gold_amoung>d_th: 
        				print("Left a bit...")
    
        				control_orientation_distance(rot_y_gold, dist_gold, -2)
        
        
        """
   	If the robot is not well aligned with the silver token, in particular the token is on the right, the robot has to turn right, but it's important to control also golden tokens in order to avoid to 		touch them when it turns:
   	"""										
        if rot_y_silver > a_th and dist_gold_amoung>d_th:
        				print("Right a bit...")

        				control_orientation_distance(rot_y_gold, dist_gold, +2)
        				
        
        """
        If the distance between the robot and the silver token is big (bigger than 4), so there is this if in order to bring the robot as close as possible to it:			
   	"""						
        if dist_silver>=4:
        	
        	"""
        	While the distance between the robot and the silver token is bigger than 1 and there is a closer golden token between them, so the robot has to strighten up:
        	"""
        	while dist_gold_amoung<1 and dist_silver>1:
   						print("Straighten up ...")
   						
   						control_golden_token(rot_y_gold, 1)
   						
   						dist_gold_amoung, rot_y_amoung=find_golden_token_amoung()
   						dist_gold, rot_y_gold=find_golden_token()
   						dist_silver, rot_y_silver= find_silver_token()
   		
   		
   		"""
   		While the distance between the robot and the silver token is bigger than 1 and there is not a closer golden token between them, so the robot can go on for 2 seconds and then it can straighten 		up its direction in order to avoid touching the golden tokens:
   		"""		
   		while dist_gold_amoung>1 and dist_silver>1:
   						print("Green light, go on")
   						drive(10,2)
   					
        					control_golden_token(rot_y_gold, 0.5)
        						
        					dist_gold_amoung, rot_y_amoung=find_golden_token_amoung()
        					dist_gold, rot_y_gold=find_golden_token()
        					dist_silver, rot_y_silver=find_silver_token()
        						




