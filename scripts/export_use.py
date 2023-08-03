#!/usr/bin/env python3

import pandas as pd
import csv
import sys
import math

def get_unixtime(dt64):
    return dt64.astype('datetime64[s]').astype('int')

def main(pid):
    df = pd.read_json('../../purpose-mode-data/'+pid+'/ping.json', lines=True)
    with open('../../purpose-mode-data/'+pid+'/'+pid+'-log.tsv', 'w') as out_file:
            tsv_writer = csv.writer(out_file, delimiter='\t')
            export_items = ['',
                            "Twitter",
                            "YouTube",
                            "LinkedIn",
                            "Facebook"]
            tsv_writer.writerow(export_items)

            phase_1_use = {}
            phase_1_use["Twitter"] = 0
            phase_1_use["YouTube"] = 0
            phase_1_use["LinkedIn"] = 0
            phase_1_use["Facebook"] = 0

            phase_2_use = {}
            phase_2_use["Twitter"] = 0
            phase_2_use["YouTube"] = 0
            phase_2_use["LinkedIn"] = 0
            phase_2_use["Facebook"] = 0

            first_timestamp = 0
            last_timestamp = 0

            phase_1_df = df.loc[df['enableIntervention'] == False]
            phase_1_df = phase_1_df.iloc[30:,:] # drop the first 30 minutes to account for the onboarding session

            if phase_1_df.empty:
                tsv_writer.writerow([
                    "Phase 1 time spent (min/day)","NA","NA","NA","NA"
                ])
            else:
                phase_1_df_first = phase_1_df.iloc[0:]
                phase_1_df_last  = phase_1_df.iloc[-1:]
                if('TimeSpentOnTwitter' in phase_1_df_last.keys()):
                    phase_1_use["Twitter"]  = phase_1_df_last['TimeSpentOnTwitter'].values[0]/60
                    if math.isnan(phase_1_use["Twitter"]):
                        print("Last Twitter spent time is Nan")
                        phase_1_use["Twitter"] = 0
                if('TimeSpentOnYouTube' in phase_1_df_last.keys()):
                    phase_1_use["YouTube"]  = phase_1_df_last['TimeSpentOnYouTube'].values[0]/60
                    if math.isnan(phase_1_use["YouTube"]):
                        print("Last YouTube spent time is Nan")
                        phase_1_use["YouTube"] = 0
                if('TimeSpentOnLinkedIn'in phase_1_df_last.keys()):
                    phase_1_use["LinkedIn"] = phase_1_df_last['TimeSpentOnLinkedIn'].values[0]/60
                    if math.isnan(phase_1_use["LinkedIn"]):
                        print("Last LinkedIn spent time is Nan")
                        phase_1_use["LinkedIn"] = 0
                if('TimeSpentOnFacebook' in phase_1_df_last.keys()):
                    phase_1_use["Facebook"] = phase_1_df_last['TimeSpentOnFacebook'].values[0]/60
                    if math.isnan(phase_1_use["Facebook"]):
                        print("Last Facebook spent time is Nan")
                        phase_1_use["Facebook"] = 0
                # print("Twitter use time:",phase_1_df_last['TimeSpentOnFacebook'].values[0])

                time_diff = (get_unixtime(phase_1_df_last['timestamp'].values[0]) - get_unixtime(phase_1_df_first['timestamp'].values[0]))/(60*60*24) # days
                tsv_writer.writerow([
                    "Phase 1 time spent (min/day)", 
                    phase_1_use["Twitter"]/time_diff, 
                    phase_1_use["YouTube"]/time_diff, 
                    phase_1_use["LinkedIn"]/time_diff, 
                    phase_1_use["Facebook"]/time_diff
                ])

            phase_2_df = df.loc[df['enableIntervention'] == True]
            phase_2_df = phase_2_df.iloc[30:,:]   # drop the first 30 minutes to account for the onboarding session
            
            if phase_2_df.empty:
                tsv_writer.writerow([
                    "Phase 2 time spent (min/day)","NA","NA","NA","NA"
                ])
            else:
                phase_2_df_first = phase_2_df.iloc[0:]
                phase_2_df_last  = phase_2_df.iloc[-1:]

                if('TimeSpentOnTwitter' in phase_2_df_last.keys()):
                    phase_2_use["Twitter"]  = phase_2_df_last['TimeSpentOnTwitter'].values[0]/60  - phase_1_use["Twitter"]
                if('TimeSpentOnYouTube' in phase_2_df_last.keys()):
                    phase_2_use["YouTube"]  = phase_2_df_last['TimeSpentOnYouTube'].values[0]/60  - phase_1_use["YouTube"]
                if('TimeSpentOnLinkedIn' in phase_2_df_last.keys()):
                    phase_2_use["LinkedIn"] = phase_2_df_last['TimeSpentOnLinkedIn'].values[0]/60 - phase_1_use["LinkedIn"]
                if('TimeSpentOnFacebook' in phase_2_df_last.keys()):
                    phase_2_use["Facebook"] = phase_2_df_last['TimeSpentOnFacebook'].values[0]/60 - phase_1_use["Facebook"]

                time_diff = (get_unixtime(phase_2_df_last['timestamp'].values[0]) - get_unixtime(phase_2_df_first['timestamp'].values[0]))/(60*60*24) # days
                tsv_writer.writerow([
                    "Phase 2 time spent (min/day)", 
                    phase_2_use["Twitter"]/time_diff, 
                    phase_2_use["YouTube"]/time_diff, 
                    phase_2_use["LinkedIn"]/time_diff, 
                    phase_2_use["Facebook"]/time_diff
                ])

            # calculate feature usage rate
            total_ping = phase_2_df.shape[0]
            features = ["Compact","Infinite","SeeMoreClick","Notif","Feed","Desaturate","Autoplay"]
            for feature in features:
                if(feature == "SeeMoreClick"):
                    tsv_writer.writerow([
                        feature,
                        phase_2_df_last["Twitter"+feature].values[0],
                        phase_2_df_last["YouTube"+feature].values[0],
                        phase_2_df_last["LinkedIn"+feature].values[0],
                        phase_2_df_last["Facebook"+feature].values[0]
                    ])
                else:
                    tsv_writer.writerow([
                        feature,
                        phase_2_df.loc[phase_2_df["Twitter"+feature] == True].shape[0]/total_ping,
                        phase_2_df.loc[phase_2_df["YouTube"+feature] == True].shape[0]/total_ping,
                        phase_2_df.loc[phase_2_df["LinkedIn"+feature] == True].shape[0]/total_ping,
                        phase_2_df.loc[phase_2_df["Facebook"+feature] == True].shape[0]/total_ping
                    ])
             

# use: python export_use.py {pid}
if __name__ == "__main__":
    pid = sys.argv[1]
    main(pid)