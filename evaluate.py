import sqlite3
from sqlite3 import OperationalError
from tqdm import tqdm
import pandas as pd
import argparse
import os
import numpy as np

def calculate_ex(db_path, predicted, gold):
    '''Calculate execution accuracy for a predicted query versus gold query
       Return 1 if execution results match else 0
    '''
    conn = sqlite3.connect(db_path)
    conn.text_factory = lambda b: b.decode(errors = 'ignore')
    cursor = conn.cursor()
    try:
        cursor.execute(predicted)
        predicted_res = cursor.fetchall()
        cursor.execute(gold)
        ground_truth_res = cursor.fetchall()
    except OperationalError as e:
        print(predicted)
        print(e)
        return 0
    conn.close()
    res = 0
    if set(predicted_res) == set(ground_truth_res):
        res = 1
    return res

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', help='Path to result file')
    parser.add_argument('--databases', help='Path to database directory')
    parser.add_argument('--difficulties', help='Path to difficulties file')
    args = parser.parse_args()

    if args.results and args.databases:
        results = pd.read_csv(args.results)
        DATABASES = args.databases
        if not os.path.exists(DATABASES):
            raise Exception(DATABASES+' not found')
    else:
        raise Exception("Please use this format python evaluate.py --dataset ./results/results.csv --databases ./data/bird/database")
    if args.difficulties:
        try:
            with open(args.difficulties,'r') as f:
                difficulty_key = f.read().splitlines()
        except:
            raise Exception(args.dataset+' not found')
    else:
        difficulty_key = []

    # evaluate each pair of predicted/gold queries
    res = []
    by_db = {}
    for database_name in results['DATABASE'].unique():
        by_db[database_name] = []
    for ind in tqdm(results.index):
        predicted = results.loc[ind,'PREDICTED SQL']
        gold = results.loc[ind,'GOLD SQL']
        database_name = results.loc[ind, 'DATABASE']
        db_path = os.path.join(DATABASES, database_name, database_name+'.sqlite')
        ex = calculate_ex(db_path, predicted, gold)
        res.append(ex)
        by_db[database_name].append(ex)

    print('---- EXECUTION ACCURACY -----')
    print(sum(res)/len(res))
    print('\n')
    for db_name in by_db.keys():
        print(db_name,':',sum(by_db[db_name])/len(by_db[db_name]))
    
    if difficulty_key:
        difficulty_res = {}
        for diff in list(np.unique(difficulty_key)):
            difficulty_res[str(diff)] = []
        for ind in range(len(res)):
            difficulty_res[difficulty_key[ind]].append(res[ind])
        for key, val in difficulty_res.items():
            print(key, sum(val)/len(val))
    