
# Autometic Bangla and English Number Plate Recognition webapp with yolov5, fastapi and easyocr

This is is a numberplate recognition webapp where I have used yolov5 wieght for numberplate localization and easyocr to extract text from localized numberplate. With fastapi, I have developed the web backend. I have used mysql from xampp as database.  

### Install dependencies
1. Install the necesasry packages with the following command.

```bash
  pip install -r requirements.txt
```
2. Install xampp and start Apache and MySql

### Vehicle recognition through numberplate
Go to the "src/" folder inside project directory. Open the terminal and run the following command.

```bash
  python main.py
```
The command will start the fastapi webapp. Go to 
http://localhost:8000/ in you browser. You will see the option to Register new vehicle and Check an incoming vehicle. Continue from here. Keep in mind that, to check a vehicle, you must register the vehicle first. 

For simplicity, to check vehicle, I have taken a video from user. One can automate this to take video from camera. To do that, change the "VideoCapture()" parameter inside get_stream() funcition of app.py
