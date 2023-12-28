from flask import Flask, request, jsonify, send_from_directory
import whisper
from io import BytesIO
import os
import openai
import sqlite3
from werkzeug.local import Local

openai.api_key="56bf5150b5584c7983e8af95dc2216c6"
openai.api_base="https://ai-dictate.openai.azure.com/" # your endpoint should look like the following https://YOUR_RESOURCE_NAME.openai.azure.com/
openai.api_type='azure'
openai.api_version = '2023-05-15' # this might change in the future
sqlite_db_path = 'JEOPARDY.db'

#db_connection = sqlite3.connect(sqlite_db_path)
#db_cursor = db_connection.cursor()

def init_db():
    if not hasattr(local_storage, 'db_connection') or local_storage.db_connection is None:
        local_storage.db_connection = sqlite3.connect(sqlite_db_path)
        local_storage.db_cursor = local_storage.db_connection.cursor()


local_storage = Local()
local_storage.db_connection = None
local_storage.db_cursor = None


deployment_name='ai-dictate' #This will correspond to the custom name you chose for your deployment when you deployed a model. 

app = Flask(__name__, static_folder='static')
model = whisper.load_model("base")

@app.route('/ask_question', methods=['POST'])
def askquestion():

    # Get the question from the request
    question = request.json.get('question')        
        
    print(question)


    response = openai.ChatCompletion.create(
        engine=deployment_name, # engine = "deployment_name".
        messages=[
            {"role": "system", "content": """I want you to generate a SQL query from the following table called QuestionsAnswers columns for a SQLLite database

ShowNumber,
AirDate,
Round -- Possible Values "Jeopardy!", "Double Jeopardy!", "Final Jeopardy!"
Category,
Value,
Question,
Answer

Rreturn just the SQL. Include all the fields. Limit the results to 500
"""},
            {"role": "user", "content": question}
        ]
    )        
    
    print(response)
    # print(response['choices'][0]['message']['content'])
    
    init_db()


    sql_query = response['choices'][0]['message']['content']

    #db_cursor.execute(sql_query)
    #results = db_cursor.fetchall()
    
    local_storage.db_cursor.execute(sql_query)
    results = local_storage.db_cursor.fetchall()    
    

    # Format and return the results as JSON
    result_data = []
    for row in results:
        result_data.append({
            'ShowNumber': row[0],
            'AirDate': row[1],
            'Round': row[2],
            'Category': row[3],
            'Value': row[4],
            'Question': row[5],
            'Answer': row[6]
        })

    return jsonify(result_data)    



@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
