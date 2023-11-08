"Generate Response agains the question"
import os
import glob
import logging
import pandas as pd
import numpy as np
import openai
from openai.embeddings_utils import  cosine_similarity
from dotenv import load_dotenv


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
logging.basicConfig(filename="newfile.log",
                    format='%(asctime)s %(message)s',
                    filemode='a+')
# Creating an object
logger = logging.getLogger()
global df
df = None

def search_text(question, n=3):
    """
    Search relevant row,

    Parameters
    ----------
    question
        Search from embedding

    Return
    ------
    dataframe
    """
    global df
    if df is None:
        df = pd.read_csv("embedding.csv")
    embedding = openai.Embedding.create(input = [question], model="text-embedding-ada-002")['data'][0]['embedding']
    df['similarities'] = df.Embedding.apply(lambda x: cosine_similarity((np.array(eval(x))), embedding))
    res = df.sort_values('similarities', ascending = False).head(n)
    return res
 
def read_pdf_and_answer_questions(question : str, file_id : str ):
    """
    This function takes a PDF file path and a question as input, and uses OpenAI's GPT-3 API to 
    read the PDF and answer the question.
    
    Parameters:
    -----------
        pdf_path (str): The file path of the PDF file to be read
        question (str): The question to be answered
    
    Returns:
    --------
        str: The answer to the question
    """
    try:
        global df
        file_ids = []
        files_path = glob.glob("embedding/*.csv")
        file_ids = []
        file_name = []
        for path in files_path:
            token1 = path.split("_")
            token2 = token1[0].split('/')
            file_ids.append(token2[1])
            file_name.append("_".join(token1[1:]))
        file_index = None
        for  ids in file_ids:
            if ids == file_id:
                file_index = file_ids.index(ids)
                break
        if file_index is None:
            logger.info("File id not exist")
            return False
        path = f'embedding/{file_ids[file_index]}_{file_name[file_index]}'
        df = pd.read_csv(path)
        result = search_text(question)
        # Use OpenAI's GPT-3 API to answer the question
        context = ""
        for i in range(len(result)):
            print("--------------------------")
            chun = (result.iloc[i].Chunk).replace('\n', " ")
            print(chun)
            print("--------------------------")
            context = context +'\n Context' + str(i) + ': ' + chun + '\n'
        # print(context)
        prompt=f"Give answer according to given [context]\n  {context} "
        print(prompt)
        messages=[
        {
        "role": "system",
        "content": prompt
        },
        {
        "role": "user",
        "content": "[Answer thhe question from context only.] "+ question
        }
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = messages,
            temperature=0.5,
            max_tokens=500,
            frequency_penalty=0,
            presence_penalty=0
        )
        print("response", response)
        logger.info(response.usage)
        # Return the answer
        return response.choices[0].message["content"]
    except openai.APIError as e:
        print(f"Error: {e}")
        logging.error(e)
        return False   
    except Exception as e:
        # Log the error
        print(f"Error: {e}")
        logger.error(e)
        return False  # Return empty string if there was an error

def generate_response(question : str, pdf_path : str):
    """
    Generate response against id given by user.
     Parameters:
    -----------
        pdf_path : The file path of the PDF file to be read
        question : The question to be answered
    
    Returns:
    --------
        str: The answer to the question
    """
    resp = read_pdf_and_answer_questions(question, pdf_path)
    if resp is False:
        logging.error("Answer not generating")
        return resp

    else:
        logging.info("Answer generated from openai")
        return resp
     
