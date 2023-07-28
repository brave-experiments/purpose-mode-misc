import json
import pandas as pd
from prettytable import PrettyTable
import time

def get_unixtime(dt64):
    return dt64.astype('datetime64[s]').astype('int')

def getActivatedFeatures(site,data):
    feature_list = [
            "Compact",
            "Infinite",
            "Notif",
            "Feed",
            "Desaturate",
            "Autoplay"
        ]
    active = []
    if site == "Twitter":
        for feature in feature_list:
            if(data[site+feature].values[0]):
                active.push(feature)
    return active

table = PrettyTable()
table.field_names = ["UID",
                     "Last Act (min)",
                     "Enab",
                     "Inter",
                     "#ESM",
                     "#Feature_Q",
                     "TwitterFeature",
                     "YouTubeFeature",
                     "LinkedInFeature",
                     "FacebookFeature",
                     ]

active_pid = [
    "Hank",
    "Pilot_1v4",
    "Harald",
    "Pilot_3",
    "sreehari"
]

for pid in active_pid:
    current_time = int(time.time())
    # read file
    df = pd.read_json('../../purpose-mode-data/'+pid+'/ping.json', lines=True)

    try: 
        feature_questionnaire = pd.read_json('./'+pid+'/feature_questionnaire.json', lines=True)
        feature_q_counter = feature_questionnaire.index
    except:
        feature_q_counter = 0

    last_ping = df.iloc[-1:]

    user = [
        last_ping['uid'].values[0],
        int((current_time - get_unixtime(last_ping["timestamp"].values[0]))/60),
        last_ping['Enable'].values[0],
        last_ping['enableIntervention'].values[0],
        last_ping['esm_counter_total'].values[0],
        feature_q_counter,
        getActivatedFeatures("Twitter",last_ping),
        getActivatedFeatures("YouTube",last_ping),
        getActivatedFeatures("LinkedIn",last_ping),
        getActivatedFeatures("Facebook",last_ping),
    ]

    table.add_rows([user])

print(table)
