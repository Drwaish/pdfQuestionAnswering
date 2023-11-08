""" Pdf processing"""
import os
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
import logging
import openai
from dotenv import load_dotenv


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
logging.basicConfig(filename="newfile.log",
                    format='%(asctime)s %(message)s',
                    filemode='a+')
# Creating an object
logger = logging.getLogger()
# Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)
EMBEDDING_FOLDER = "embedding"
os.makedirs(EMBEDDING_FOLDER, exist_ok = True)

def get_chunk_text(text):
    """
    Convert data into chunks

    Parameters
    ----------
    text
        Data to change into chunk

    Return
    ------
    Array 
    """
    text_splitter =  RecursiveCharacterTextSplitter(
    chunk_size = 500,
    chunk_overlap = 50,
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_pdf_text(pdf_file):
    """
    Extract data from pdf.

    Parameters
    ----------
    Pdf file to get data

    Return
    ------
    str
    """
    text = ""

    reader = PdfReader(pdf_file)
    for page in reader.pages:
        text += page.extract_text()
    return text
def get_embedding(chunks, file_id, file_name, model = "text-embedding-ada-002"):
    """
    Generate embedding and store in one file.
    
    Parameters
    ----------
    df
      Dataframe for searching
    model
      Text Search from Dataframe    """
    try:
        df_embed = {}
        embedding = []
        chunk_list = []
        for chunk in chunks:
            chunk_list.append(chunk)
            chunk = chunk.replace('\n', " ")
            result = openai.Embedding.create(input = chunk, model=model)['data'][0]['embedding']
            embedding.append(result)
        df_embed["Chunk"] = chunk_list
        df_embed['Embedding'] = embedding
        df_embed = pd.DataFrame(df_embed)
        df_embed.to_csv(f"embedding/{file_id}_{file_name}.csv", index = False)
        # df = pd.read_csv("embedding.csv")
        return True
    except FileNotFoundError:
        return False
    except FileExistsError:
        return False
    except Exception:
        print("Error in get_Embedding", Exception)
        return False

def save_embedding(file_name, file_id)->bool:
    """
    Get embedding and save files.

    Parameters
    ----------
    Pdf file to get data.

    Return
    ------
    bool
    """
    file_path = f'uploads/{file_id}_{file_name}'
    # uploads/4224268/4224268_The Gifts of Imperfection.pdf
    parent_name = file_name.split('.')
    text = get_pdf_text(pdf_file=file_path)
    chunk = get_chunk_text(text=text)
    resp = get_embedding(chunk, file_name=parent_name[0], file_id= file_id)
    logger.info("Embedding Created")
    return resp
    