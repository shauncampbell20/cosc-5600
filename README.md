## Environment

```
python -m venv .venv
.venv\scripts\activate
pip install -r requirements.txt

# or use conda if you want
```

## Setup
1. Get a gemini API key and put it in a text file called "gemini-key.txt".
2. Download and unzip [Spider dataset](https://drive.google.com/file/d/1403EGqzIDoHMdQF4c9Bkyl7dZLZ5Wt6J/view)
3. Copy the contents of /spider_data/test_database to /data/spider/database
4. Download and unzip [BIRD mini dev](https://drive.usercontent.google.com/downloadid=1UJyA6I6pTmmhYpwdn8iT9QKrcJqSQAcX&export=download)
5. Copy the contents of /data_minidev/MINIDEV/dev_databases to data/bird/databases

Directory should look like this:

```
shaun/
├── README.md
├── requirements.txt
├── gemini-key.txt
├── DIN-SQL.py
├── prompt_templates.py
├── .venv/
├── data/
│   ├── spider
│	  		├── dev.json
│	  		├── tables.json
│	  		├── example_tables.json
│	  		├── database/
│	  		    ├── <Spider database folders copied here>
│   ├── bird
│	  		├── dev.json
│	  		├── tables.json
│	  		├── example_tables.json
│	  		├── database/
│	  		    ├── <Bird database folders copied here>
```

## Run
Run these commands (change indexes in line 273)
```
# Spider dataset
python DIN-SQL.py --dataset ./data/spider/ --output ./results

# BIRD dataset
python DIN-SQL.py --dataset ./data/bird/ --output ./results
```

## Evaluation
Run these commands. Replace <spider_result_file.csv> and <bird_results_file.csv> with the files generated with the previous commands.
```
# Spider dataset
python evaluate.py --results "./results/<spider_result_file.csv>" --databases ./data/spider/database

# BIRD dataset
python evaluate.py --results "./results/<bird_result_file.csv>" --databases ./data/bird/database
```

## Results

### Spider Test Set
```
---- EXECUTION ACCURACY -----
0.8346530041918957

---- BY DATABASE -----
soccer_3 : 0.95
e_commerce : 0.9375
bbc_channels : 0.9375
tv_shows : 1.0
vehicle_driver : 0.9523809523809523
online_exams : 0.975
customers_and_orders : 0.9512195121951219
region_building : 0.975
government_shift : 0.675
vehicle_rent : 0.9545454545454546
cre_Students_Information_Systems : 0.881578947368421
book_1 : 0.9743589743589743
book_review : 0.9047619047619048
restaurant_bills : 0.9333333333333333
club_leader : 0.7647058823529411
cre_Doc_and_collections : 0.8
sing_contest : 0.95
address_1 : 0.7625
boat_1 : 0.7692307692307693
headphone_store : 0.8863636363636364
aan_1 : 0.7555555555555555
conference : 0.8636363636363636
pilot_1 : 0.7560975609756098
district_spokesman : 0.9523809523809523
art_1 : 0.6228070175438597
car_road_race : 0.9545454545454546
country_language : 0.975
real_estate_rentals : 0.7361111111111112
bike_racing : 0.8823529411764706
bakery_1 : 0.6826923076923077
car_racing : 0.7
institution_sports : 0.9
warehouse_1 : 0.7692307692307693
university_rank : 0.8636363636363636
movie_2 : 0.7692307692307693
planet_1 : 0.7763157894736842
video_game : 0.9523809523809523
book_press : 0.8181818181818182
cre_Doc_Workflow : 0.975
advertising_agencies : 0.8444444444444444
```

### BIRD Mini Dev
```
---- EXECUTION ACCURACY -----
0.432

---- BY DATABASE -----
debit_card_specializing : 0.5
student_club : 0.7083333333333334
thrombosis_prediction : 0.14
european_football_2 : 0.43137254901960786
formula_1 : 0.5
superhero : 0.7692307692307693
codebase_community : 0.5714285714285714
card_games : 0.36538461538461536
toxicology : 0.225
california_schools : 0.13333333333333333
financial : 0.15625

---- BY DIFFICULTY -----
simple 0.6148648648648649
moderate 0.384
challenging 0.28431372549019607
```



