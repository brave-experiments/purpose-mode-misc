#!/usr/bin/env python3

import pandas as pd
import csv
import sys

def main(pid,week):
    if week == "1":
        has_intervention = False
    elif week == "2":
        has_intervention = True
    else:
        print("Unknown week parameter: ",week)
        return 
    
    # read file
    df = pd.read_json('../../purpose-mode-data/'+pid+'/esm.json', lines=True)
    with open('../../purpose-mode-data/'+pid+'/'+pid+'-interview.tsv', 'w') as out_file:
        tsv_writer = csv.writer(out_file, delimiter='\t')
        export_items = ['uid',"site","time","autoplay_video","notifications","newsfeed_recomm","infinite_newsfeed_scroll","cluttered_layout","saturation","Q1","Q2","Q3","Q4","Q5","Q6","Q7"]
        tsv_writer.writerow(export_items)
        for index, row in df.iterrows():
            data = row['data']
            if data["study_status_intervention"] != has_intervention:
                continue
            esm_data = [
                row['uid'],
                data['esm_site'],
                data['esm_time'],
                data['adjusted_distractions']['adj_autoplay_video'],
                data['adjusted_distractions']['adj_notifications'],
                data['adjusted_distractions']['adj_newsfeed_recommendations'],
                data['adjusted_distractions']['adj_infinite_newsfeed_scrolling'],
                data['adjusted_distractions']['adj_cluttered_layout'],
                data['adjusted_distractions']['adj_saturation'],
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

# use: python export_esm.py {pid} {week}
if __name__ == "__main__":
    pid = sys.argv[1]
    week = sys.argv[2]
    main(pid,week)