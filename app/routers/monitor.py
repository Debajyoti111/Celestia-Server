from fastapi import APIRouter, HTTPException
from ..models.monitor_model import MonitorModel
import re
import gspread
from ..config import Config
import pandas as pd

"""
Define all google sheet related constants here
"""
service_account = gspread.service_account(filename='service-key.json')
CELESTIA_SHEET = "https://docs.google.com/spreadsheets/d/155h6JyUsKZuiwuhPpYXfO3gCkTf1d16VBNHt4aIRcgI/edit#gid=0"
sheet = service_account.open_by_url(CELESTIA_SHEET)
WORKSHEET_TO_GAMETYPE = {
    "game1": sheet.worksheet("Game1"),
    "game2": sheet.worksheet("Game2"),
}

"""
End of google sheet related constants
"""
router = APIRouter()

# post route to register phone number for games or update the count
@router.post("/register-game",status_code=200)
async def register_game(monitor: MonitorModel):
    #check phone number if valid
    pattern = re.compile(r"(\+\d{1,3})?\s?\(?\d{1,4}\)?[\s.-]?\d{3}[\s.-]?\d{4}")
    match = re.search(pattern, monitor.phone_number)
    if not match:
        raise HTTPException(status_code=400, detail="Phone Number is not valid")
    
    # check if game type is valid
    if monitor.game_type not in WORKSHEET_TO_GAMETYPE.keys():
        raise HTTPException(status_code=400, detail="Game Type is not valid")
    worksheet = WORKSHEET_TO_GAMETYPE[monitor.game_type]

    # check if phone number already registered
    df = pd.DataFrame(worksheet.get_all_records())
    if not df.empty:
        number_list = map(str,df["phone_number"].values.tolist())
        if monitor.phone_number in list(number_list):
            # increment number of times played
            df["phone_number"] = df["phone_number"].astype(str)
            df.loc[df["phone_number"] == monitor.phone_number, "number_of_times_played"] += 1
            worksheet.update([df.columns.values.tolist()] + df.values.tolist())
            return {}

    try:
        # record entry in google sheet
        df2 = pd.DataFrame({"phone_number": [monitor.phone_number], "game_type": [monitor.game_type], "number_of_times_played": 1})
        if worksheet.row_count == 0:
            df = df2
        else:
            df = pd.concat([df, df2], ignore_index=True)
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    return {}

# get number of times played for a specific game type of a phone number
@router.post("/get-game-stats")
async def get_game_stats(monitor: MonitorModel):
    #check phone number if valid
    pattern = re.compile(r"(\+\d{1,3})?\s?\(?\d{1,4}\)?[\s.-]?\d{3}[\s.-]?\d{4}")
    match = re.search(pattern, monitor.phone_number)
    if not match:
        raise HTTPException(status_code=400, detail="Phone Number is not valid")
    
    # check if game type is valid
    if monitor.game_type not in WORKSHEET_TO_GAMETYPE.keys():
        raise HTTPException(status_code=400, detail="Game Type is not valid")
    worksheet = WORKSHEET_TO_GAMETYPE[monitor.game_type]

    # check if phone number already registered
    df = pd.DataFrame(worksheet.get_all_records())
    if not df.empty:
        number_list = map(str,df["phone_number"].values.tolist())
        if monitor.phone_number in list(number_list):
            # get number of times played
            df["phone_number"] = df["phone_number"].astype(str)
            number_of_times_played = df.loc[df["phone_number"] == monitor.phone_number, "number_of_times_played"].values.tolist()[0]
            return {"number_of_times_played": number_of_times_played}
    return {"number_of_times_played": 0}