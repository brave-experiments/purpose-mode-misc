#!/usr/bin/env python3

import pandas as pd
import csv
import sys

def main(pid):
    
    # read file
    df = pd.read_json('../../purpose-mode-data/'+pid+'/feature_feedback_questionnaire.json', lines=True)
    with open('../../purpose-mode-data/'+pid+'/'+pid+'-feature_questionnaire.tsv', 'w') as out_file:
        tsv_writer = csv.writer(out_file, delimiter='\t')
        export_items = ['uid',"site","time","changes","Q1","Q2"]
        tsv_writer.writerow(export_items)
        for index, row in df.iterrows():
            data = row['data']
            esm_data = [
                row['uid'],
                data['sampled_site'],
                data['sampled_time'],
                data['feature_changed'],
                data['questionnaire_responses']['current_activity'], #Q1
                data['questionnaire_responses']['reason'] #Q2
            ]
            tsv_writer.writerow(esm_data)
            # print(esm_data)

# use: python export_esm.py {pid} {week}
if __name__ == "__main__":
    pid = sys.argv[1]
    main(pid)