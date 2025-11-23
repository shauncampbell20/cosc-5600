import pandas as pd
import time
import os
import sys
from google import genai
from google.genai import types
from prompt_templates import (
        schema_linking_prompt, classification_prompt, easy_prompt, medium_prompt, hard_prompt
    )
import argparse
import sqlite3
from datetime import datetime

with open('gemini-key.txt','r') as f:
  API_KEY = f.read()
os.environ['GEMINI_API_KEY'] = API_KEY
client = genai.Client()

def load_data(DATASET):
    '''Load test dataset
    '''
    return pd.read_json(DATASET)

def hard_prompt_maker(test_sample_text,database,schema_links,sub_questions):
    '''Build a prompt for Hard questions
    '''
    instruction = "# Use the intermediate representation and the schema links to generate the SQL queries for each of the questions.\n"
    fields = find_fields_MYSQL_like("college_2", example_schema)
    fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like("college_2", example_foreign) + '\n'
    fields += find_fields_MYSQL_like(database, schema)
    fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like(database, foreign) + '\n'
    stepping = f'''\nA: Let's think step by step. "{test_sample_text}" can be solved by knowing the answer to the following sub-question "{sub_questions}".'''
    fields += "\n"
    fields += get_sample_rows(database)
    prompt = instruction +fields + hard_prompt + 'Q: "' + test_sample_text + '"' + '\nschema_links: ' + schema_links + stepping +'\nThe SQL query for the sub-question"'
    return prompt

def medium_prompt_maker(test_sample_text,database,schema_links):
    '''Build a prompt for Medium questions
    '''
    instruction = "# Use the the schema links and Intermediate_representation to generate the SQL queries for each of the questions.\n"
    fields = find_fields_MYSQL_like("college_2", example_schema)
    fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like("college_2", example_foreign) + '\n'
    fields += find_fields_MYSQL_like(database, schema)
    fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like(database, foreign) + '\n'
    fields += "\n"
    fields += get_sample_rows(database)
    prompt = instruction +fields + medium_prompt + 'Q: "' + test_sample_text + '\nSchema_links: ' + schema_links + '\nA: Let’s think step by step.'
    return prompt

def easy_prompt_maker(test_sample_text,database,schema_links):
    '''Build a prompt for Easy questions
    '''
    instruction = "# Use the the schema links to generate the SQL queries for each of the questions.\n"
    fields = find_fields_MYSQL_like("college_2", example_schema)
    fields += find_fields_MYSQL_like(database, schema)
    fields += "\n"
    fields += get_sample_rows(database)
    prompt = instruction +fields + easy_prompt + 'Q: "' + test_sample_text + '\nSchema_links: ' + schema_links + '\nSQL:'
    return prompt
  
def classification_prompt_maker(test_sample_text,database,schema_links):
    '''Build a prompt to classify a question as EASY, NON-NESTED, or NESTED
    '''
    instruction = "# For the given question, classify it as EASY, NON-NESTED, or NESTED based on nested queries and JOIN.\n"
    instruction += "\nif need nested queries: predict NESTED\n"
    instruction += "elif need JOIN and don't need nested queries: predict NON-NESTED\n"
    instruction += "elif don't need JOIN and don't need nested queries: predict EASY\n\n"
    fields = find_fields_MYSQL_like("college_2", example_schema)
    fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like("college_2", example_foreign) + '\n'
    fields += find_fields_MYSQL_like(database, schema)
    fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like(database, foreign) + '\n'
    fields += "\n"
    prompt = instruction + fields + classification_prompt + 'Q: "' + test_sample_text + '\nschema_links: ' + schema_links + '\nA: Let’s think step by step.'
    return prompt

def schema_linking_prompt_maker(test_sample_text,database):
    '''Build a prompt to generate schema links
    '''
    instruction = "# Find the schema_links for generating SQL queries for each question based on the database schema and Foreign keys.\n"
    fields = find_fields_MYSQL_like(database, schema)
    foreign_keys = "Foreign_keys = " + find_foreign_keys_MYSQL_like(database, foreign) + '\n'
    prompt = instruction + schema_linking_prompt + fields +foreign_keys+ 'Q: "' + test_sample_text + """"\nA: Let’s think step by step."""
    return prompt

def find_foreign_keys_MYSQL_like(db_name, foreign):
    '''Format foreign keys of database 
    '''
    df = foreign[foreign['Database name'] == db_name]
    output = "["
    for index, row in df.iterrows():
        output += row['First Table Name'] + '.' + row['First Table Foreign Key'] + " = " + row['Second Table Name'] + '.' + row['Second Table Foreign Key'] + ','
    output= output[:-1] + "]"
    return output

def find_fields_MYSQL_like(db_name, schema):
    '''Format fields of database 
    '''
    df = schema[schema['Database name'] == db_name]
    df = df.groupby(' Table Name')
    output = ""
    for name, group in df:
        output += "Table " +name+ ', columns = ['
        for index, row in group.iterrows():
            output += row[" Field Name"]+','
        output = output[:-1]
        output += "]\n"
    return output

def find_primary_keys_MYSQL_like(db_name, primary):
    '''Format primary keys of database 
    '''
    df = primary[primary['Database name'] == db_name]
    output = "["
    for index, row in df.iterrows():
        output += row['Table Name'] + '.' + row['Primary Key'] +','
    output = output[:-1]
    output += "]\n"
    return output

def flatten_list_of_lists_and_strings(nested_list):
    '''Flatten a list containing both lists and strings to a list of just strings
    '''
    for item in nested_list:
        if isinstance(item, list):
            yield from flatten_list_of_lists_and_strings(item)
        else:
            yield item

def creatiing_schema(DATASET_JSON):
    '''Parse schema dataframe, primary keys, and foreign keys from a tables.json file 
    '''
    schema_df = pd.read_json(DATASET_JSON)
    schema_df = schema_df.drop(['column_names','table_names'], axis=1)
    schema = []
    f_keys = []
    p_keys = []
    for index, row in schema_df.iterrows():
        tables = row['table_names_original']
        col_names = row['column_names_original']
        col_types = row['column_types']
        foreign_keys = row['foreign_keys']
        primary_keys = row['primary_keys']
        for col, col_type in zip(col_names, col_types):
            index, col_name = col
            if index == -1:
                for table in tables:
                    schema.append([row['db_id'], table, '*', 'text'])
            else:
                schema.append([row['db_id'], tables[index], col_name, col_type])
        for primary_key in list(flatten_list_of_lists_and_strings(primary_keys)):
            index, column = col_names[primary_key]
            p_keys.append([row['db_id'], tables[index], column])
        for foreign_key in foreign_keys:
            first, second = foreign_key
            first_index, first_column = col_names[first]
            second_index, second_column = col_names[second]
            f_keys.append([row['db_id'], tables[first_index], tables[second_index], first_column, second_column])
    schema = pd.DataFrame(schema, columns=['Database name', ' Table Name', ' Field Name', ' Type'])
    primary = pd.DataFrame(p_keys, columns=['Database name', 'Table Name', 'Primary Key'])
    foreign = pd.DataFrame(f_keys,
                        columns=['Database name', 'First Table Name', 'Second Table Name', 'First Table Foreign Key',
                                 'Second Table Foreign Key'])
    return schema,primary,foreign

def get_sample_rows(db_name):
    '''Get 3 sampple rows for each table in a database
    '''
    tables=schema[schema['Database name']==db_name][' Table Name'].unique()
    db = sqlite3.connect(os.path.join(DATABASES,db_name,db_name+'.sqlite'))
    cursor = db.cursor()
    s = ''
    for tab in tables:
        s += '3 sample rows from '+tab+' table.\n'
        rows = cursor.execute(f'''SELECT * FROM {tab} LIMIT 3''').fetchall()
        headers = [desc[1] for desc in cursor.execute(f'''PRAGMA table_info({tab});''').fetchall()]
        s += '\t'.join(headers)+'\n'
        for row in rows:
            s += str(row)+'\n'
        s += '\n\n'
    db.close()
    return s

def debuger(test_sample_text,database,sql):
  instruction = """#### For the given question, use the provided tables, columns, foreign keys, and primary keys to fix the given SQLite SQL QUERY for any issues. If there are any problems, fix them. If there are no issues, return the SQLite SQL QUERY as is.
#### Use the following instructions for fixing the SQL QUERY:
1) Use the database values that are explicitly mentioned in the question.
2) Pay attention to the columns that are used for the JOIN by using the Foreign_keys.
3) Use DESC and DISTINCT when needed.
4) Pay attention to the columns that are used for the GROUP BY statement.
5) Pay attention to the columns that are used for the SELECT statement.
6) Only change the GROUP BY clause when necessary (Avoid redundant columns in GROUP BY).
7) Use GROUP BY on one column only.

"""
  fields = find_fields_MYSQL_like(database, schema)
  fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like(database, foreign) + '\n'
  fields += "Primary_keys = " + find_primary_keys_MYSQL_like(database, primary)
  prompt = instruction + fields+ '#### Question: ' + test_sample_text + '\n#### SQLite SQL QUERY\n' + sql +'\n#### SQLite FIXED SQL QUERY\nSELECT'
  return prompt

def Gemini_generation(prompt):
    print('...sleeping 10 seconds for rate limit...')
    time.sleep(10)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            temperature=0.0,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop_sequences=["Q:"],
            thinking_config=types.ThinkingConfig(include_thoughts=False)
            ),
        contents=prompt
    )
    print('-----------GEMINI RESPONSE---------------')
    print(response.text)
    print('-----------------------------------------')
    return response.text

def Gemini_debug(prompt):
    print('...sleeping 10 seconds for rate limit...')
    time.sleep(10)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            temperature=0.0,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop_sequences=["#", ";","\n\n"],
            thinking_config=types.ThinkingConfig(include_thoughts=False)
        ),
    contents=prompt
    )
    print('-----------GEMINI RESPONSE---------------')
    print(response.text)
    print('-----------------------------------------')
    return response.text

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', help='Path to dataset files')
    parser.add_argument('--output', help='Desired path to output directory')
    args = parser.parse_args()
    
    if args.dataset and args.output:
        DATASET_SCHEMA = os.path.join(args.dataset,'tables.json')
        DATASET = os.path.join(args.dataset, 'dev.json')
        DATABASES = os.path.join(args.dataset, 'database')
        OUTPUT_FILE = args.output
        EXAMPLE_SCHEMA = os.path.join(args.dataset,'example_tables.json')
        dataset_name = os.path.split(args.dataset)[-1]
        if not os.path.exists(args.output):
            try:
                os.mkdir(args.output)
            except:
                raise Exception("Unable to find/create "+args.output)
        output_file = os.path.join(args.output, dataset_name+'_results_'+datetime.today().strftime('%Y%m%d%H%M%S')+'.csv')
    else:
        raise Exception("Please use this format python CoT.py --dataset ./data/dataset --output ./results")
      
    schema,primary,foreign = creatiing_schema(DATASET_SCHEMA)
    example_schema,example_primary,example_foreign = creatiing_schema(EXAMPLE_SCHEMA)
    
    val_df = load_data(DATASET)
    if 'SQL' in val_df.columns:
      val_df.rename(columns={'SQL':'query'}, inplace=True)
    print(f"Number of data samples {val_df.shape[0]}")
    CODEX = []

    for index, row in val_df.iloc[6:40].iterrows():
        print(f"index is {index}")
        print('***Question: ',row['question'])
        
        # Schema links
        print('***generate schema links')
        schema_links = None
        while schema_links is None:
            try:
                schema_links = Gemini_generation(
                    schema_linking_prompt_maker(row['question'], row['db_id']))
            except Exception as e:
                print(e)
                time.sleep(3)
                pass
        try:
            schema_links = schema_links.split("Schema_links: ")[1]
        except:
            print("Slicing error for the schema_linking module")
            schema_links = "[]"
        
        # Question classification
        print('***generate question classification')
        classification = None
        while classification is None:
            try:
                classification = Gemini_generation(
                    classification_prompt_maker(row['question'], row['db_id'], schema_links))
            except Exception as e:
                print(e)
                time.sleep(3)
                pass
        try:
            predicted_class = classification.split("Label: ")[1]
        except:
            print("Slicing error for the classification module")
            predicted_class = '"NESTED"'
        
        # Easy prompt
        if '"EASY"' in predicted_class:
            print('***generate Easy prompt')
            SQL = None
            while SQL is None:
                try:
                    SQL = Gemini_generation(easy_prompt_maker(row['question'], row['db_id'], schema_links))
                except Exception as e:
                    print(e)
                    time.sleep(3)
                    pass
                    
        # Medium prompt            
        elif '"NON-NESTED"' in predicted_class:
            print('***generate Medium prompt')
            SQL = None
            while SQL is None:
                try:
                    SQL = Gemini_generation(medium_prompt_maker(row['question'], row['db_id'], schema_links))
                except Exception as e:
                    print(e)
                    time.sleep(3)
                    pass
            try:
                SQL = SQL.split("SQL: ")[1]
            except Exception as e:
                print(e)
                print("SQL slicing error")
                SQL = "SELECT"
                
        # Hard prompt        
        else:
            sub_questions = classification.split('questions = ["')[1].split('"]')[0]
            print('***generate Hard prompt')
            SQL = None
            while SQL is None:
                try:
                    SQL = Gemini_generation(
                        hard_prompt_maker(row['question'], row['db_id'], schema_links, sub_questions))
                except Exception as e:
                    print(e)
                    time.sleep(3)
                    pass
            try:
                SQL = SQL.split("SQL:")[1]
            except Exception as e:
                print(e)
                print("SQL slicing error")
                SQL = "SELECT"
        
        # Debug
        print('***generate Debug prompt')
        debugged_SQL = None
        while debugged_SQL is None:
            try:
                debugged_SQL = Gemini_debug(debuger(row['question'], row['db_id'], SQL)).replace("\n", " ")
            except Exception as e:
                print(e)
                time.sleep(3)
                pass
        SQL = debugged_SQL.replace('```sqlite','').replace('```','').strip()
        if SQL[:7] != 'SELECT ':
          SQL = 'SELECT '+SQL
        print('***Final SQL:', SQL)
        CODEX.append([index, row['question'], SQL, row['query'], row['db_id']])

        # save results every iter in case of crash
        df = pd.DataFrame(CODEX, columns=['Index', 'NLQ', 'PREDICTED SQL', 'GOLD SQL', 'DATABASE'])
        df.to_csv(output_file, index=False)
