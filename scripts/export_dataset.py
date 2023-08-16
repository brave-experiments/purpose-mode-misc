#!/usr/bin/env python3

import pandas as pd
import csv
from datetime import datetime, timedelta
import sys

pids = [
    "Pilot_1",
    "Pilot_1v4",
    "Pilot_1v5",
    "Harald",
    "Harald_v2",
    "sreehari",
    "Masood",
    "Pilot_3",
    "Pilot_3v3"
]

def main():
    
    timestr = datetime.now().strftime("%Y%m%d-%H%M%S")
    with open('../../purpose-mode-data/'+f'dataset-{timestr}.tsv', 'w') as out_file:
        tsv_writer = csv.writer(out_file, delimiter='\t')
        export_items = [
            'uid',
            "site",
            # "is homepage",
            # "is youtube video",
            "time",
            "hour_of_day",
            "day_of_week",
            "is_weekend",
            "has_interventions",
            
            # original distractions
            "original_autoplay_video",
            "original_notifications",
            "original_newsfeed_recomm",
            "original_infinite_newsfeed_scroll",
            "original_cluttered_layout",
            "original_saturation",
            
            # features
            "feature_compact_layout",
            "feature_hide_notification",
            "feature_finite_newsfeed_scrolling",
            "feature_hide_newsfeed",
            "feature_desaturate",
            "feature_block_autoplay",

            # adjusted distractions
            "adj_autoplay_video",
            "adj_notifications",
            "adj_newsfeed_recomm",
            "adj_infinite_newsfeed_scroll",
            "adj_cluttered_layout",
            "adj_saturation",
            
            # esm responses
            "Q1","Q2","Q3","Q4","Q5","Q6","Q7"]
        
        tsv_writer.writerow(export_items)
        for pid in pids:
            # read file
            df = pd.read_json('../../purpose-mode-data/'+pid+'/esm.json', lines=True)
            for index, row in df.iterrows():
                data = row['data']
                if data['esm_responses']['purpose'] == "Others":
                    data['esm_responses']['purpose'] = data['esm_responses']['purpose'] + ": "+data['esm_responses']['purpose_other']
                q_timestamp = datetime.strptime(data['esm_time'],'%a %b %d %Y %H:%M:%S GMT%z')
                day_time_hour = q_timestamp.hour
                day_of_week = q_timestamp.weekday()
                is_weekend = 1 if (q_timestamp.weekday() >= 5 and q_timestamp.weekday() <= 6) else 0
                if("study_status_intervention" in data):
                    has_intervention = data["study_status_intervention"]
                else:
                    has_intervention = "NA"
                
                esm_data = [
                    row['uid'],
                    data['esm_site'],
                    # data['esm_is_homepage'],
                    # data['esm_is_youtube_watch'],
                    data['esm_time'],
                    day_time_hour,
                    day_of_week,
                    is_weekend,
                    has_intervention,

                    # origianl distractions
                    data['distractions']['autoplay_video'],
                    data['distractions']['notifications'],
                    data['distractions']['newsfeed_recommendations'],
                    data['distractions']['infinite_newsfeed_scrolling'],
                    data['distractions']['cluttered_layout'],
                    data['distractions']['saturation'],

                    # features
                    data['features']["compact_layout"],
                    data['features']["finite_newsfeed_scrolling"],
                    data['features']["hide_newsfeed"],
                    data['features']["hide_notification"],
                    data['features']["desaturate"],
                    data['features']["block_autoplay"],

                    # adjusted distractions
                    data['adjusted_distractions']['adj_autoplay_video'],
                    data['adjusted_distractions']['adj_notifications'],
                    data['adjusted_distractions']['adj_newsfeed_recommendations'],
                    data['adjusted_distractions']['adj_infinite_newsfeed_scrolling'],
                    data['adjusted_distractions']['adj_cluttered_layout'],
                    data['adjusted_distractions']['adj_saturation'],

                    # ESM response
                    data['esm_responses']['current_activity'], #Q1
                    data['esm_responses']['purpose'], #Q2
                    data['esm_responses']['distraction'], #Q3
                    data['esm_responses']['distraction_text'], #Q4
                    data['esm_responses']['agency'], #Q5
                    data['esm_responses']['satisfaction'], #Q6
                    data['esm_responses']['goal_alignment'] #Q7
                ]
                tsv_writer.writerow(esm_data)
                # print(esm_data)

# use: python export_dataset.py
if __name__ == "__main__":
    main()