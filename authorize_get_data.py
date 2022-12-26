#! /usr/bin/env python
#-*- coding: utf-8 -*-

import json
import httplib2
import os,json
from datetime import datetime
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
import pandas as pd 
from simple_modules.nanosecond_format import format_my_nanos
# Get the OAuth credentials from the file (not committed to git)
client_secrets_path = os.getcwd()+"/client_secret.json"
with open(client_secrets_path, 'r') as file: 
    secret_keys = json.load(file)

CLIENT_ID = secret_keys['installed']['client_id']
CLIENT_SECRET = secret_keys['installed']['client_secret']

# Check https://developers.google.com/fit/rest/v1/reference/users/dataSources/datasets/get
# for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/fitness.heart_rate.read'

# O_AUTH_SCOPE = {
#     "activity": "https://www.googleapis.com/auth/fitness.activity.read",
#     "location" : "https://www.googleapis.com/auth/fitness.location.read",
#     "blood_pressure" : "https://www.googleapis.com/auth/fitness.blood_pressure.read"
# }
# DATA SOURCE
DATA_SOURCE = "derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm"

# DATA_SOURCE = {
#     "steps": "derived:com.google.step_count.delta:com.google.android.gms:merge_step_deltas",
#     "dist": "derived:com.google.distance.delta:com.google.android.gms:from_steps<-merge_step_deltas",
#     "bpm": "derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm",
#     "rhr": "derived:com.google.heart_rate.bpm:com.google.android.gms:resting_heart_rate<-merge_heart_rate_bpm",
#     "sleep" : "derived:com.google.sleep.segment:com.google.android.gms:sleep_from_activity<-raw:com.google.activity.segment:com.heytap.wearable.health:stream_sleep",
#     "cal" : "derived:com.google.calories.expended:com.google.android.gms:from_activities",
#     "move": "derived:com.google.active_minutes:com.google.android.gms:from_steps<-estimated_steps",
#     "points" : "derived:com.google.heart_minutes:com.google.android.gms:merge_heart_minutes",
#     "weight" : "derived:com.google.weight:com.google.android.gms:merge_weight"
# }


# The ID is formatted like: "startTime-endTime" where startTime and endTime are
# 64 bit integers (epoch time with nanoseconds).
DATA_SET = "1051700038292387000-1670718763224489000"

# Redirect URI for installed apps - below for offline OAuth 
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

def retrieve_data():
    """
    Run through the OAuth flow and retrieve credentials.
    Returns a dataset (Users.dataSources.datasets):
    https://developers.google.com/fit/rest/v1/reference/users/dataSources/datasets
    """
    flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
    authorize_url = flow.step1_get_authorize_url()
    print('Go to the following link in your browser:')
    print(authorize_url) 
    code = input('Enter verification code: ').strip()
    credentials = flow.step2_exchange(code)

    # Create an httplib2.Http object and authorize it with our credentials
    http = httplib2.Http()
    http = credentials.authorize(http)

    fitness_service = build('fitness', 'v1', http=http)

    return fitness_service.users().dataSources(). \
              datasets(). \
              get(userId='me', dataSourceId=DATA_SOURCE, datasetId=DATA_SET). \
              execute()

def nanoseconds(nanotime):
    """
    Convert epoch time with nanoseconds to human-readable.
    """
    dt = datetime.fromtimestamp(nanotime // 1000000000)
    return dt.strftime('%Y-%m-%d %H:%M:%S')

if __name__ == "__main__":
    # Point of entry in execution mode:
    dataset = retrieve_data()

    #Create DF 
    data_df = pd.DataFrame.from_dict(dataset["point"], orient='columns')

    # Convert the 'value' column into separate columns 
    data_df[["fpVal",'mapVal']] = data_df["value"].apply(lambda x : pd.Series(x[0]))

    # Delete unnecessary columns 
    data_df.drop(["modifiedTimeMillis","mapVal", "value"],axis=1, inplace=True)

    # Change Column names to readable format
    data_df.columns = ["start_time", "end_time", "data_type", "originDataSourceId", "heart_rate"]

    # Convert Nanoseconds to timestamp
    data_df[["start_time","end_time"]] = data_df[["start_time","end_time"]].apply(pd.to_numeric)
    data_df["start_time"] = data_df["start_time"].apply(format_my_nanos)
    data_df["end_time"] = data_df["end_time"].apply(format_my_nanos) 

    # Save to csv file
    data_df.to_csv(f"heart_rate_{datetime.now()}.csv")
    

    print(data_df)
    