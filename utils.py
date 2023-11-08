""" Utility function for proper oprations"""
import os
import glob
import random as rd
import logging
from typing import Any
from flask import (
    json, make_response, Response
)


logging.basicConfig(filename="newfile.log",
                    format='%(asctime)s %(message)s',
                    filemode='a+')
# Creating an object
logger = logging.getLogger()
# Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok = True)

def validate_request(request_api: Any)-> bool:
    """
    method will take a json request and perform all validations if the any error 
    found then return error response with status code if data is correct then 
    return data in a list.

    Parameters:
    ----------
    request_api: Request
        contain the request data in file format.

    Return:
    ------
    bool
        return True or False.

    """

    if "data" in request_api.files:
        return True
    if "data" not in request_api.files:
        return False
def validate_text_request(request_api: Any)-> bool:
    """
    method will take a json request and perform all validations if the any error 
    found then return error response with status code if data is correct then 
    return data in a list.

    Parameters
    ----------
    request_api: Request
        contain the request data in file format.

    Return
    ------
    bool
        return True or False.

    """
    data = request_api.get_json()
    if "data" in data:
        if data["data"] == '':
            return False
        return True
    if "data" not in data:
        return False
def get_textdata(data: json)-> str:
    """
    method will take a json data and return text_data.

    Parameters:
    ----------
    data: json
        json data send in request.

    Return:
    ------
    text_data: str
        return text_data as string.

    """
    try :
        text_data = []
        text_data.append(data["data"]) # Question ask by user
        text_data.append(data['id'])   # id of document
        return True, text_data
    except Exception:
        logger.error("Missing Parameters")
        return False


    return text_data

def get_data(request_api: Any)-> str:
    """
    method will take request and get data from request then return thhe data.

    Parameters:
    ----------
    request_api: Request
        contain the request data in file format.

    Return:
    ------
    image_file: str
        return the data file as string.

    """
    data = request_api.files["data"]
    return data
def make_bad_params_value_response()-> Response:
    """
    method will make a error response a return it back.

    Parameters:
    ----------
    None

    Return:
    ------
    Response
        return a response message.

    """
    result = make_response(json.dumps(
                            {'message'  : 'data key error',
                            'category' : 'Bad Params'}),
                            400)
    return result
def make_file_save_error_response()-> Response:
    """
    method will make a error response a return it back.

    Parameters:
    ----------
    None

    Return:
    ------
    Response
        return a response message.

    """
    result = make_response(json.dumps(
        {'message'  : 'File not save sucesfully',
        'category' : 'Bad Params error'}),
        400)
    return result
def make_invalid_extension_response()-> Response:
    """
    method will make a error response a return it back.

    Parameters:
    ----------
    None

    Return:
    ------
    Response
        return a response message.

    """
    result = make_response(json.dumps(
        {'message'  : 'Invalid Extension',
        'category' : 'Params error',}),
        400)
    return result
def validate_extension(request_api: Any)-> bool:
    """
    method will take image and check its extension is .mp4, .avi, .FLV.

    Parameters
    ----------
    video: Any
        api request send by user.

    Return
    ------
    bool
        return the true or false video is has valid extension or not.

    """
    data_f = request_api.files["data"]
    data_list = data_f.filename.split(".")
    data_extension = data_list[len(data_list)-1]
    data_extensions = ['pdf']
    if data_extension in data_extensions:
        return True
    return False

def save_file(request_api)-> str:
    """
    method will take request and save file from request in specified folder.

    Parameters:
    ----------
    request_api: Request
        contain the request data in file format.
    Return:
    ------
    save_file_path: str
        file path save on our local sever.
    """
    try:
        data_f = request_api.files["data"]
        file_id = None
        # get_id = request_api.form.get("id")
        files_path = glob.glob("uploads/*.pdf")
        file_ids = []
        for path in files_path:
            token1 = path.split(".")
            file_ids.append(token1[0])
        # generate file ids for record
        while True:
            file_id = str(rd.randint(0 , 1000))
            if file_id not in file_ids:
                break
            # os.makedirs(f'{UPLOAD_FOLDER}/{file_id}')
            # os.makedirs(f'{UPLOAD_FOLDER}/{file_id}', exist_ok= True)
        # save_file_path = f"{UPLOAD_FOLDER}/{str(file_id)}/{str(file_id)}_{data_f.filename}"
        save_file_path = f"{UPLOAD_FOLDER}/{str(file_id)}_{data_f.filename}"

        print("save_file_path", save_file_path)
        data_f.save(save_file_path)
        # Dlete unused memory
        del files_path
        del save_file_path
        logger.info(f"Saving file with {file_id}, {data_f.filename}")
        return True, file_id, data_f.filename
    except Exception as eror:
        logger.error("Error in saving file" + eror)
        return False, None , None
