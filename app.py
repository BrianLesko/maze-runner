# By Brian Lesko , 11/28/2023
# This python script implements a simple sketchpad using a dualsense touchpad, conneceted via USB C. 

import io # used for the image download
import time # used for the sleep function
import numpy as np # used for the image and array making
import streamlit as st # used for the GUI
import matplotlib.pyplot as plt # used for saving the image
from skimage.transform import resize

import dualsense # Custom class by Brian Lesko for Wired DualSense controller communication
import customize_gui # Custom class by Brian Lesko for streamlit GUI modifications
DualSense = dualsense.DualSense
gui = customize_gui.gui()

vendorID, productID = int("0x054C", 16), int("0x0CE6", 16)

def get_level(filename):
    n, m = 1080-10, 1900-30 # x is 40 - 1900 y is 1100 - 10 
    with st.spinner(text="Importing the level..."): 
        # Create the maze walls by importing a jpg image
        maze = plt.imread(filename)
        resized_maze=resize(maze, (n, m))[:,:,0] # Resize and only use the red channel
        R, G, B = resized_maze[:,:,0], resized_maze[:,:,1], resized_maze[:,:,2]
    with st.spinner(text="Creating walls..."): 
        wall_coordinates=[]   # Wall Coordinates are created from black colors
        goal_coordinates=[]
        for i in range(n):
            for j in range(m):
                if G[i][j]  < .5 and R[i][j] < .5 and B[i][j] < .5:
                    wall_coordinates.append((i,j))
                if G[i][j]  > .5 and R[i][j] < .5 and B[i][j] < .5:
                    goal_coordinates.append((i,j))
    return resized_maze, wall_coordinates, goal_coordinates

def main():
    gui.clean_format(wide = True)
    gui.about(text = "This code implements a maze game with a wired ps5 controller, use the touchpad to navigate the maze.")
    with st.spinner(text="Setting up the app..."): 
        Title = st.empty()
        progress_bar = st.progress(0)
        image_placeholder = st.empty()
    with st.spinner(text="Connecting to your controller..."): 
        ds = DualSense(vendorID,productID)
        ds.connect()
        
    n, m = 1080-10, 1900-30
    loops = 1000
    pixel_size = 10
    switch_level = True
    wins = 0
    for i in range(loops): 
        if switch_level:
            with Title: st.title("Get ready...")
            if wins == 0: pixels, wall_coordinates, goal_coordinates = get_level("maze-01.jpg")
            if wins == 1: pixels, wall_coordinates, goal_coordinates = get_level("maze-02.jpg")
            if wins == 2: pixels, wall_coordinates, goal_coordinates = get_level("maze-02.jpg")
            with Title: st.title("Hurry, finish the maze!")
            switch_level = False
        ds.receive()
        ds.updateTouchpad(n=1)
        y, x = ds.touchpad_x[0], ds.touchpad_y[0]
        y1, x1 = ds.touchpad1_x[0], ds.touchpad1_y[0]

        ds.lights(rgb=(0,0,255))
        ds.send_outReport()

        if ds.touchpad_isActive:
            # Draw Pixels
            if 0 <= x < n and 0 <= y < m:  # Check that the touchpad values are within the image dimensions
                for dx in range(-pixel_size//2 + 1, pixel_size//2 + 1):
                    for dy in range(-pixel_size//2 + 1, pixel_size//2 + 1):
                        if 0 <= x + dx < n and 0 <= y + dy < m:  # Check that the coordinates are within the image dimensions
                            pixels[x + dx][y + dy] = 0 # Set the pixel to black  # Set the pixel to black 
            if (x,y) in wall_coordinates:   # You lose
                with Title: st.title("Dont touch the walls!")
                ds.rumble()
                ds.lights(rgb=(255,0,0))
                ds.send_outReport()

            else:
                ds.lights(rgb=(0,255,0))
                ds.send_outReport()
            if (x,y) in goal_coordinates:   # You win
                with Title: st.title("You won!")
                if wins == 0: st.balloons() 
                wins = wins + 1
                switch_level = True
        
        progress_bar.progress((i + 1)/loops)
        with image_placeholder: st.image(pixels, use_column_width=True)
        #time.sleep(.00005)
        progress_bar.progress((i + 1)/loops)

    with Title: st.title("You ran out of Time at level " + str(wins)+1 + "!")
    ds.disconnect()

main()