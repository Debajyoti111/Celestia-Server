from fastapi import APIRouter, HTTPException
import qrcode
from ..models.registration_model import RegistrationModel
import re
import gspread
from ..config import Config
import pandas as pd

service_account = gspread.service_account(filename='service-key.json')
CELESTIA_SHEET = "https://docs.google.com/spreadsheets/d/155h6JyUsKZuiwuhPpYXfO3gCkTf1d16VBNHt4aIRcgI/edit#gid=0"
worksheet = service_account.open_by_url(CELESTIA_SHEET).sheet1

router = APIRouter()

# post route to generate qr for individual using phone number
@router.post("/generate_qr")
async def generate_qr(registration: RegistrationModel):
    # check if phone number already registered
    df = pd.DataFrame(worksheet.get_all_records())
    if not df.empty:
        number_list = map(str,df["phone_number"].values.tolist())
        if registration.phone_number in list(number_list):
            print("Phone Number already registered")
            raise HTTPException(status_code=400, detail="Phone Number already registered")
    
    #check phone number if valid
    pattern = re.compile(r"(\+\d{1,3})?\s?\(?\d{1,4}\)?[\s.-]?\d{3}[\s.-]?\d{4}")
    match = re.search(pattern, registration.phone_number)
    if not match:
        raise HTTPException(status_code=400, detail="Phone Number is not valid")
    try:
        # generate qr code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4
        )
        qr.add_data(registration.phone_number)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        # save qr code in static folder
        img.save(f"static/qrcodes/{registration.phone_number}.png")
        # record entry in google sheet
        qr_link =  f"http://{Config.SERVER_IP}:{Config.SERVER_PORT}/static/qrcodes/{registration.phone_number}.png"
        df2 = pd.DataFrame({"phone_number": [registration.phone_number], "qr_link": [qr_link]})
        if worksheet.row_count == 0:
            df = df2
        else:
            df = pd.concat([df, df2], ignore_index=True)
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    return {"qr_link": qr_link}

# check if registered using phone number
@router.post("/check_registered")
async def check_registered(entry: RegistrationModel):
    # check if phone number already registered
    worksheet = service_account.open_by_url(CELESTIA_SHEET).sheet1
    df = pd.DataFrame(worksheet.get_all_records())
    if not df.empty:
        number_list = map(str,df["phone_number"].values.tolist())
        if entry.phone_number in list(number_list):
            return {"registered": True}
    return {"registered": False}
