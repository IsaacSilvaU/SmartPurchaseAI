# Smart Spending Control Project
## Description
This project is designed to help users keep track of their purchasing products spending. Using the device's camera, users capture images of the products they wish to purchase. Using the YOLOv5 model, the system detects objects (products) within the images. Once detected, users have the option to manually input the price of each product and decide if they wish to include it in the final shopping list. Moreover, the system stores a monthly spending history for each user, thus allowing detailed review and control of their purchases.

## Features
- User registration and login.
- Product image capture through the device's camera.
- Product detection using YOLOv5.
- Option for the user to manually add the price of detected products.
- Filtering of certain non-relevant objects to not be shown in the results.
- Automatic calculator that sums up the value of the products selected and - assigned by the user.
- Monthly spending history for each user.
- Display of the processed image with highlighted detected products.

## Installation and Setup
1. Clone this repository:
```: git clone [repository link]```

2. Navigate to the project directory:
```: cd [project directory name]```

3. Install the required dependencies:
```: pip install -r requirements.txt```

4. Run the application:
```: flask run```

## Usage
1. Open your browser and navigate to http://localhost:5000 (or the address you have configured).
2. Register or log in with your account.
3. Use your device's camera to capture an image of your products.
4. Wait for the system to process the image and detect the products.
5. Decide which products you want to add to your list and manually enter the price for each one.
6. Review the monthly spending history in the corresponding section.

## Credits
Hardvard CS50: For all the quality content offered in your course.
YOLOv5: Used for object detection.
Flask: For creating the web server.
SQLite: For creating the Data Base.
Bing Chat: For questions during development such as the creation of macros in Jinja and questions about the implementation of Yolo, additionally used for the creation of the logos and images of the project.