#!/usr/bin/env python3

import pandas as pd
import csv
from datetime import datetime, timedelta
import sys

from pid import done_pid

def main():
    
    # import data cleaning logs
    remove_id    = []
    duplicate_id_check   = {}
    distraction_relabel  = {}
    feature_relabel      = {}
    browsing_activity_relabel = {}
    dark_pattern_relabel = {
        "P17_Thu Aug 24 2023 23:01:15 GMT-0700": ["autoplay_video"],
        "P25_Wed Aug 30 2023 15:12:25 GMT-0400": ["newsfeed_recommendations","infinite_newsfeed_scrolling"]
    }

    with open('removal.tsv') as f:
        f.readline()
        fp = csv.reader(f, delimiter='\t')
        for i in fp:
            id, time, reason = [x.strip() for x in i]
            remove_id.append(id+'_'+time)
    
    with open('duplicated.tsv') as f:
        f.readline()
        fp = csv.reader(f, delimiter='\t')
        for i in fp:
            id, time = [x.strip() for x in i]
            duplicate_id_check[id+'_'+time] = False

    with open('distraction.tsv') as f:
        f.readline()
        fp = csv.reader(f, delimiter='\t')
        for i in fp:
            id, time, updated_value = [x.strip() for x in i]
            distraction_relabel[id+'_'+time] = updated_value
    
    with open('feature.tsv') as f:
        f.readline()
        fp = csv.reader(f, delimiter='\t')
        for i in fp:
            id, time, feature, updated_value = [x.strip() for x in i]
            feature_relabel[id+'_'+time] = (feature,updated_value)

    with open('browsing_activity.tsv') as f:
        f.readline()
        fp = csv.reader(f, delimiter='\t')
        for i in fp:
            id, time, updated_value = [x.strip() for x in i]
            browsing_activity_relabel[id+'_'+time] = updated_value

    # print(feature_relabel)
    # return

    timestr = datetime.now().strftime("%Y%m%d-%H%M%S")
    with open('../../purpose-mode-data/dataset/'+f'dataset-{timestr}.tsv', 'w') as out_file:
        tsv_writer = csv.writer(out_file, delimiter='\t')
        export_items = [
            "id",
            "uid",
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
            "Q1","browsing_purpose","perceived_distraction","Q4","agency","satisfaction","goal_alignment"]
        
        tsv_writer.writerow(export_items)
        for pid in done_pid:
            if pid == "P23_work": # no datapoint from the pid
                continue
            # print(pid)
            # read file
            df = pd.read_json('../../purpose-mode-data/'+pid+'/esm.json', lines=True)
            for index, row in df.iterrows():
                data = row['data']
                # skip study onboarding
                if data['esm_responses']['current_activity'] == "study onboarding":
                    continue
                
                record_id = row['uid']+'_'+data['esm_time']
                # skip removed records
                if record_id in remove_id:
                    continue

                # skip duplicated records
                if record_id in duplicate_id_check:
                    if(duplicate_id_check[record_id] == False):
                        # print(record_id, "first record")
                        duplicate_id_check[record_id] = True
                    else:
                        # print(record_id, "duplicated record")
                        continue

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

                # Q2 (purpose) relabel
                Q2 = data['esm_responses']['purpose']
                if record_id in browsing_activity_relabel:
                    Q2 = browsing_activity_relabel[record_id]

                # Q3 (distractions) relabel
                Q3 = data['esm_responses']['distraction']
                if record_id in distraction_relabel:
                    Q3 = distraction_relabel[record_id]
                
                # feature relabel
                if record_id in feature_relabel:
                    update_feature, update_value = feature_relabel[record_id]
                    data['features'][update_feature] = update_value
                
                # dark pattern relabel
                if record_id in dark_pattern_relabel:
                    patterns = dark_pattern_relabel[record_id]
                    for pattern in patterns:
                        data['distractions'][pattern] = True
                
                # recalculate adjusted_distractions if feature or dark pattern got updated
                

                if ((record_id in feature_relabel) or (record_id in dark_pattern_relabel)):
                    # origianl distractions
                    autoplay_video              = data['distractions']['autoplay_video']
                    notifications               = data['distractions']['notifications']
                    newsfeed_recommendations    = data['distractions']['newsfeed_recommendations']
                    infinite_newsfeed_scrolling = data['distractions']['infinite_newsfeed_scrolling']
                    cluttered_layout            = data['distractions']['cluttered_layout']
                    saturation                  = data['distractions']['saturation']

                    # features
                    compact = data['features']["compact_layout"]
                    finite  = data['features']["finite_newsfeed_scrolling"]
                    feed    = data['features']["hide_newsfeed"]
                    notif   = data['features']["hide_notification"]
                    autoplay = data['features']["block_autoplay"]
                    desaturate  = data['features']["desaturate"]

                    # Adjusted infinite scrolling
                    data['adjusted_distractions']['adj_infinite_newsfeed_scrolling'] = infinite_newsfeed_scrolling and (not finite) and (not feed)
                    # Adjusted autoplay video
                    if(newsfeed_recommendations and feed):
                        data['adjusted_distractions']['adj_autoplay_video'] = False
                    else:
                        data['adjusted_distractions']['adj_autoplay_video'] = autoplay_video and (not autoplay)
                                                                                            
                    # Adjusted notifications
                    data['adjusted_distractions']['adj_notifications'] = notifications and (not notif)
                    # Adjusted newsfeed recommendations
                    data['adjusted_distractions']['adj_newsfeed_recommendations'] = newsfeed_recommendations and (not feed)
                    # Adjusted cluttered layout
                    data['adjusted_distractions']['adj_cluttered_layout'] = (not compact)
                    # Adjusted Saturation
                    data['adjusted_distractions']['adj_saturation'] = (not desaturate)


                esm_data = [
                    record_id,
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
                    Q2, #Q2 (browsing purpose)
                    Q3, #Q3 (distraction)
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