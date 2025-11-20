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
3. Copy the contents of /spider_data/database to /data/spider/database
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



