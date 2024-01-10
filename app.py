import cv2
import requests
import base64
import json
import time
import numpy as np

import matplotlib.pyplot as plt
from collections import defaultdict
def plot_emotions_over_time(emotions_over_time, image):
    # Convert the emotions dictionary to a format suitable for plotting
    labels = list(emotions_over_time.keys())
    data = np.array(list(emotions_over_time.values())).T  # Transpose for stacking

    print( data )


cap = cv2.VideoCapture(1)  # 0 is usually the default camera

def capture_image():

    global cap
  
    success, image = cap.read()

    if success:

        ## resize image
        # resize image to width 320 keeping aspect ratio
        # max_width = 480
        # image = cv2.resize(image, (max_width, int(max_width * image.shape[0] / image.shape[1])))

        cv2.imshow("image", image)
        cv2.waitKey(1)

        cv2.imwrite("capture.jpg", image)



    return success, image

def encode_image_to_base64(image):
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')

def send_image_to_server(image_data):
    start_time = time.time()
    print( 'sending image to server')
    url = 'http://localhost:5000/analyze'
    headers = {'Content-Type': 'application/json'}
    data = {"image": f"data:image/jpeg;base64,{image_data}"}
    response = requests.post(url, timeout=2, headers=headers, data=json.dumps(data))
    print(f"Response time: {time.time() - start_time}")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Request failed with status code: {response.status_code}")


import matplotlib.pyplot as plt
import numpy as np


def plot(data):
    # Labels for the 7 dimensions
    labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']

    colors = ['red', 'green', 'blue', 'yellow', 'orange', 'purple', 'cyan']


    # Number of variables (7 dimensions)
    num_vars = len(labels)

    # Compute angle for each axis
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    # Radar chart setup
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

    alpha = 1.0
    for d in reversed(data):
        bars = ax.bar(angles, d, width=1)  # Example width of bars

        # Use custom colors and opacity
        index = 0
        for bar in bars:
            bar.set_facecolor(colors[index])
            bar.set_alpha(alpha)
            index += 1

        alpha -= 0.1

    # Set the labels for each bar
    plt.xticks(angles, labels)
     # Draw ylabels
    ax.set_rlabel_position(30)
    plt.yticks([0.2, 0.4, 0.6, 0.6], ["20", "40", "60", "80"], color="grey", size=7)
    plt.ylim(0, 1)


    # Draw the plot on the canvas and save
    fig.canvas.draw()
    plt.savefig('my_plot.png')

    # Show the plot using OpenCV
    cv2.imshow("plot", cv2.imread('my_plot.png'))
    cv2.waitKey(1)

    # Close the figure to free memory
    plt.close(fig)

data = []

# Main loop to capture and process images
while True:
    success, image = capture_image()
    if success:
        image_data = encode_image_to_base64(image)
        try:
            result = send_image_to_server(image_data)
        except Exception as e:
            print(e)
            continue

        print( result )

        if 'emotion' in result:
            print(result['emotion'])

         
            # Create a list of emotion values scaled to range [0, 1]
            d = []

            for emotion, value in result['predictions'][0].items():
                d.append( value )

            # Append the new data to the list
            data.append(d)

            # dicard the oldest data point
            if len(data) > 10:
                data.pop(0)

            plot(data)  # Call your plot function
#                 emotions_over_time[emotion].pop(0)  # Maintain constant size

#             plot_emotions_over_time(emotions_over_time, image)

#     if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
#         break

#     time.sleep(1)

# cv2.destroyAllWindows()