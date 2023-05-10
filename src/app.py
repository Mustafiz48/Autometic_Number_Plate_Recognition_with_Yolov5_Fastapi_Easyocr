import numpy as np
import cv2
import base64

from fastapi import Depends, FastAPI, HTTPException, Body, Request, Form, UploadFile, WebSocket, WebSocketDisconnect, \
    status
from starlette.responses import RedirectResponse, Response

from typing import Annotated

from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import crud, models, schemas
from database import SessionLocal, engine

from License_Recognizer import License_Recognizer

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="../templates")  # Change this path accordingly
app.mount("/assets", StaticFiles(directory="../templates/assets"), name="assets")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# @app.get("/registration", response_class=HTMLResponse)
# def index(request: Request):
#     return templates.TemplateResponse("Registration.html", {"request": request})


@app.post("/create_user/")
def create_user(
        # user : schemas.New_User
        name: Annotated[str, Form()],
        phone: Annotated[str, Form()],
        designation: Annotated[str, Form()],
        department: Annotated[str, Form()],
):
    user = schemas.New_User(name=name, phone=phone, designation=designation, department=department)
    print("User info:", name)
    print("Haahaahaa", user)
    return "Success!"


@app.post("/user/", response_model=schemas.User)
def create_user(
        request: Request,

        name: Annotated[str, Form()],
        phone: Annotated[str, Form()],
        designation: Annotated[str, Form()],
        department: Annotated[str, Form()],
        db: Session = Depends(get_db)):
    user = schemas.UserCreate(name=name, phone=phone, designation=designation, department=department)
    db_user = crud.get_user_by_phone(db, phone=user.phone)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered with given phone number")
    print(user)
    created_user = crud.create_user(db=db, user=user)
    return templates.TemplateResponse("Registration_step_2.html", {"request": request, "user": created_user})


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/cars/", response_model=list[schemas.Car])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cars = crud.get_cars(db, skip=skip, limit=limit)
    return cars


@app.get("/users/cars/{license_number}", response_model=schemas.User)
def get_user_by_license_number(license_number: str, db: Session = Depends(get_db)):
    return crud.get_user_by_license(db, license_number=license_number)


def get_license_number(image):
    # AI module to get number plate
    license_recognizer = License_Recognizer()
    _, license_number, _ = license_recognizer.get_license_number(image)
    try:
        license_number = license_number[0]
        language = license_number[0]  # The first character indicates the language
        final_license_number = None
        if language == "B":
            final_license_number = f"{license_number[1]}_{license_number[-9]}_{license_number[-7:]}"
        elif language == "E":
            final_license_number = license_number[0:]

        b64encoded_license = base64.b64encode(bytes(final_license_number, 'utf-8'))
        return b64encoded_license
    except Exception as e:
        return f"Couldn't read the license number,please try again with clear license plate! The Error: {e}"


@app.post("/users/{user_id}/cars/", )
def create_item_for_user(
        request: Request,
        user_id: int,
        image: Annotated[UploadFile, Form()],
        db: Session = Depends(get_db),
):
    image_bytes = image.file.read()
    image_file = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), flags=1)
    # print(image_file.shape)
    # print(type(image_file))
    # AI module to get number plate
    encoded_license_number = get_license_number(image_file)    
    if isinstance(encoded_license_number, str):  # Exception occurred, just return the exception message
        return encoded_license_number
    # try:
    #     license_number = license_number[0]
    # except Exception as e:
    #     return f"Couldn't read the license number,please try again with clear license plate! The Error: {e}"
    # print(license_number)
    # b64encoded_license = base64.b64encode(bytes(license_number, 'utf-8'))
    print("Encoded License: ", encoded_license_number)
    decoded_license_number = base64.b64decode(encoded_license_number)
    print("Decoded License: ", decoded_license_number.decode('utf8'))
    car = schemas.CarCreate(license_number=encoded_license_number)
    try:
        created_car = crud.create_user_car(db=db, car=car, user_id=user_id)
        return templates.TemplateResponse("Success.html", {"request": request})
    except Exception as e:
        return f"Something went wrong. May be the user or the license number already exists! Please try again. The Error: {e}"


@app.websocket("/ws")
async def get_stream(websocket: WebSocket, db: Session = Depends(get_db)):
    camera = cv2.VideoCapture("temp_videos/test_video.mp4")

    await websocket.accept()
    try:
        i = 0
        while True:
            success, frame = camera.read()

            if i == 10:
                encoded_license_number = get_license_number(frame)
                if isinstance(encoded_license_number, str):  # Exception occurred, just return the exception message
                    return encoded_license_number
                                
                # b64encoded_license = base64.b64encode(bytes(license_number, 'utf-8'))
                # print("lalala")
                # print(license_number.decode('utf-8'))
                # print("\n\n") 
                # print("Encoded:", encoded_license_number)
                decoded_license_number = base64.b64decode(encoded_license_number)
                license = decoded_license_number.decode('utf8')
                print("Lincese number: ", license)
                user = crud.get_user_by_license(db, license_number=encoded_license_number)
                if user:
                    print("Car Owner: ", user.name)
                    await websocket.send_text(f"Success! Car information:<br>License Number: <b>{license}</b>, <br>Owner: <b>{user.name}</b> <br>Deparment: <b>{user.department}</b> <br>Designation: <b>{user.designation}</b>")
                else:
                    await websocket.send_text(f"Failed! {str(license)}")

            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                await websocket.send_bytes(buffer.tobytes())

            i += 1
    except WebSocketDisconnect:
        print("Client disconnected")


@app.get("/display_video/")
def display_video(request: Request):
    return templates.TemplateResponse("Video_feed.html", {"request": request})


@app.post("/varify_car/", )
def create_item_for_user(
        request: Request,
        video: Annotated[UploadFile, Form()],
        db: Session = Depends(get_db),
):
    video_bytes = video.file.read()
    with open(f"temp_videos/test_video.mp4", "wb") as video_file:
        video_file.write(video_bytes)

    response = RedirectResponse(url='/display_video', status_code=status.HTTP_303_SEE_OTHER)
    return response  # templates.TemplateResponse("Success.html", {"request": request})


@app.get("/upload_video/")
def registraion_page(request: Request):
    return templates.TemplateResponse("Video_Upload.html", {"request": request})


@app.get("/registration/")
def registraion_page(request: Request):
    return templates.TemplateResponse("Registration.html", {"request": request})


@app.post("/{license_number}/create_guest/")
def add_guest(        
    request: Request,
    name: Annotated[str, Form()],
    phone: Annotated[str, Form()],
    license_number: str,
    db: Session = Depends(get_db)):

    guest = models.Guest(name=name, phone = phone, license_number = license_number)
    crud.create_guest(db=db, guest=guest)

    return templates.TemplateResponse("Success.html",{"request":request})

@app.get("/{license_number}/guest_registration/")
def add_guest(        
    request: Request,
    license_number: str):

    return templates.TemplateResponse("Guest_Registration.html", {"request":request, "license_number":license_number})


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("Home.html", {"request": request})


