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
- copy /spider_data/database to /data/spider/database
- copy /spider_data/dev.json to /data/spider/dev.json
- copy /spider_data/tables.json to /data/spider/tables.json
3. Download and unzip [BIRD mini dev](https://drive.usercontent.google.com/downloadid=1UJyA6I6pTmmhYpwdn8iT9QKrcJqSQAcX&export=download)
- copy /data_minidev/MINIDEV/dev_databases to data/bird/databases
- copy /data_minidev/MINIDEV/dev_tables.json to data/bird/tables.json
- copy /data_minidev/MINIDEV/mini_dev_sqlite.json to data/bird/dev.json

Directory should look like this:

```
shaun/
├── README.md
├── requirements.txt
├── gemini-key.txt
├── DIN-SQL.py
├── prompt_templates.py
│
├── data/
│   ├── spider
│	  		├── dev.json
│	  		├── tables.json
│	  		├── example_tables.json
│	  		├── database/
│	  		    ├── ...
│   ├── bird
│	  		├── dev.json
│	  		├── tables.json
│	  		├── example_tables.json
│	  		├── database/
│	  		    ├── ...
```

## Run
Run these commands (I have it set up just to do 2 questions for testing purposes, line 644)
```
python DIN-SQL.py --dataset ./data/spider/ --output predicted_sql.txt

python DIN-SQL.py --dataset ./data/bird/ --output predicted_sql.txt
```

