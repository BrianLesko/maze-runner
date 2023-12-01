# By Brian Lesko , 11/28/2023
# This python script implements a simple sketchpad using a dualsense touchpad, conneceted via USB C. 

import io # used for the image download
import time # used for the sleep function
import numpy as np # used for the image and array making
import streamlit as st # used for the GUI
import matplotlib.pyplot as plt # used for saving the image

import dualsense # Custom class by Brian Lesko for Wired DualSense controller communication
import customize_gui # Custom class by Brian Lesko for streamlit GUI modifications
gui = customize_gui.gui()
DualSense = dualsense.DualSense

vendorID, productID = int("0x054C", 16), int("0x0CE6", 16)

def main():
    gui.clean_format(wide = True)
    gui.about(text = "This code implements a maze game with a wired ps5 controller, use the touchpad to navigate the maze.")
    
    with st.spinner(text="Setting up the app..."): 
        col1, col2, col3 = st.columns([1,2.5,1])
        with col2: Title = st.empty()
        with Title: st.title("Get ready")
        progress_bar = st.progress(0)
        image_placeholder = st.empty()

    with st.spinner(text="Connecting to your controller..."): 
        ds = DualSense(vendorID,productID)
        ds.connect()
        # Create an empty image
        n, m = 1080-10, 1900-30 # x is 40 - 1900 y is 1100 - 10 
        pixels = np.ones((n,m))
    with st.spinner(text="Importing the level..."): 
        # Create the maze walls by importing a jpg image
        maze = plt.imread("maze-01.jpg")
        from skimage.transform import resize
        resized_maze=resize(maze, (n, m))
        maze=resized_maze
        greens=resized_maze[:,:,1]  # only use the second channel of the image
    with st.spinner(text="Creating walls..."): 
        wall_coordinates=[]   # Wall Coordinates are created from black colors
        for i in range(n):
            for j in range(m):
                if maze[:,:,0][i][j] > .5 and maze[:,:,1][i][j] >.5 and maze[:,:,2][i][j] >.5 : # if the pixel is black
                    wall_coordinates.append((i,j))
    with st.spinner(text="Placing the goal"):
        goal_coordinates = []   # Goal Coordinates are created from green colors
        for i in range(n):
            for j in range(m):
                if maze[:,:,0][i][j] < .5 and maze[:,:,1][i][j] >.5 and maze[:,:,2][i][j] < .5 :  # green color
                    goal_coordinates.append((i,j))

    pixels = maze # multiply the maze by the empty image to create the maze walls
    with Title: st.title("Hurry, finish the maze!")

    loops = 1000
    pixel_size = 10
    win = 0
    for i in range(loops): 
        ds.receive()
        ds.updateTouchpad(n=1)
        y, x = ds.touchpad_x[0], ds.touchpad_y[0]
        y1, x1 = ds.touchpad1_x[0], ds.touchpad1_y[0]

        if ds.touchpad_isActive:
            # Draw Pixels
            if 0 <= x < n and 0 <= y < m:  # Check that the touchpad values are within the image dimensions
                for dx in range(-pixel_size//2 + 1, pixel_size//2 + 1):
                    for dy in range(-pixel_size//2 + 1, pixel_size//2 + 1):
                        if 0 <= x + dx < n and 0 <= y + dy < m:  # Check that the coordinates are within the image dimensions
                            pixels[x + dx][y + dy] = max(0, pixels[x + dx][y + dy] - 1)  # Subtract 1 from the pixel value, but don't go below 0
            if (x,y) in wall_coordinates:   # You lose
                ds.rumble()
                ds.lights(rgb=(255,0,0))
            else:
                ds.lights(rgb=(0,255,0))
            if (x,y) in goal_coordinates:   # You win
                with Title: st.title("You won!")
                if win == 0: st.balloons() 
                win = 1
            ds.send_outReport()
        
        progress_bar.progress((i + 1)/loops)
        with image_placeholder: st.image(pixels, use_column_width=True)
        time.sleep(.00005)
        progress_bar.progress((i + 1)/loops)

    with Title: st.title("You ran out of Time!")
    # Download your image
    buffer = io.BytesIO()
    plt.imsave(buffer, pixels, cmap='gray', format='png')
    with st.sidebar: 
        st.write("")
        "---"
        st.write("")
        col1, col2, col3 = st.columns([1,1,1])
        with col2: 
            st.subheader("Download")
            st.download_button(
            label="as png",
            data=buffer.getvalue(),
            file_name='my_artwork.png',
            mime='image/png',
            )
        st.write("")
        "---"
    ds.disconnect()

main()