## Environment

```
python -m venv .venv
.venv\scripts\activate
pip install -r requirements.txt

# or use conda if you want
```

## Setup
Get a gemini API key and put it in a text file called "gemini-key.txt". Directory should look like this:

```
shaun/
├── README.md
├── requirements.txt
├── gemini-key.txt
├── DIN-SQL.py
│
├── data/
│   ├── spider
│	  		├── dev.json
│	  		├── tables.json
│   ├── bird
│	  		├── dev.json
│	  		├── tables.json
```

## Run
Run these commands (I have it set up just to do 2 questions for testing purposes, line 644)
```
python DIN-SQL.py --dataset ./data/spider/ --output predicted_sql.txt

python DIN-SQL.py --dataset ./data/bird/ --output predicted_sql.txt
```
