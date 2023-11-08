"""
Main module of flask API.
"""
# Third party modules
import os
import glob
from typing import Any
from functools import wraps
import logging
from dotenv import load_dotenv
from flask import (
    Flask, request,abort,
    json, make_response, Response
)
from flask_cors import CORS, cross_origin
from asgiref.wsgi import WsgiToAsgi
from utils import (validate_request, validate_text_request,
                   get_textdata, make_bad_params_value_response,
                   make_file_save_error_response, make_invalid_extension_response,
                   validate_extension, save_file)

from generator import generate_response
from doc_processing import save_embedding


logging.basicConfig(filename="newfile.log",
                    format='%(asctime)s %(message)s',
                    filemode='a+')
# Creating an object
logger = logging.getLogger()
# Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)

# Module
app = Flask(__name__)
cors = CORS(app)
#asgi_app = WsgiToAsgi(app)
api_cors = {
  "origins": ["*"],
  "methods": ["OPTIONS", "GET", "POST"],
  "allow_headers": ["Content-Type"]
}
#app.config['PROPAGATE_EXCEPTIONS'] = True

def authorize(token: str)-> bool:
    """
    method take header token as input and check valid ot not.

    Parameters:
    ----------
    toekn: str 
        token pass by the user in header.

    Return:
    ------
        return True if the toekn is valid otherwise return False.

    """
    load_dotenv()
    my_key = os.getenv('api-key')
    if token != my_key:
        return True
    return False

def token_required(func: Any)-> Any:
    """
    method token required will perform the authentication based on taoken.

    Parameters:
    ----------
    func: Any
        arguement ass to the function from request header.

    Return:
    ------
        return the the response of the token authentication.

    """
    @wraps(func)
    def decorated(*args, **kwargs):
        token = None
        if 'api-key' in request.headers:
            token = request.headers['api-key']
        if not token:
            result = make_response(json.dumps(
            {'message'  : 'Token Missing',
            'category' : 'Authorization error',}),
            401)
            return result
        if authorize(token):
            result = make_response(
            json.dumps(
            {'message'  : 'UnAuthorized',
            'category' : 'Authorization error',}),
            401)
            return result
        return func(*args, **kwargs)
    return decorated



@app.route('/upload_file', methods = ['POST'])
@cross_origin(**api_cors)
def upload_file():
    """
    method will take the file as input and save file on local server.

    Parameters:
    ----------
    None

    Return:
    ------
    str
        return the reponse.

    """
    try:
        if validate_request(request):
            print("1")
            if validate_extension(request):
                print("2.")
                resp, file_id, file_name = save_file(request)
                if resp:
                    save_embedding(file_name=file_name, file_id=file_id)
                    output_dict = {}
                    output = {
                    'message' : "File Save Sucesfully",
                    "Acceess id": file_id

                    }
                    output_dict["output"] = output
                    return Response(
                        json.dumps(output_dict),
                        mimetype = 'application/json'
                        )
                else :
                    print("Exception in Save File")
                return make_file_save_error_response()
            return make_invalid_extension_response()
        return make_bad_params_value_response()
    except Exception as exception:
        result = make_response(json.dumps(
                    {'message'  : str(exception),
                    'category' : 'Internal server error'}),
                    500)
        return result

@app.route('/query', methods = ['POST'])
@cross_origin(**api_cors)
def create_answer():
    """
    method will take the text as input and return the response generated
    by the openai.

    Parameters:
    ----------
    None

    Return:
    ------
    str
        return the reponse.

    """
    try:
        if validate_text_request(request):
            query = request.get_json()
            resp, text_data = get_textdata(query)
            if resp:
                predicted_data = generate_response(text_data[0], text_data[1])
                if predicted_data is False:
                    result = make_response(json.dumps(
                        {'message'  : "Error in generating response",
                        'category' : 'Internal server error',}),
                        500)
                    return result
                output = {
                    "output" : predicted_data
                }
                return Response(
                    json.dumps(output),
                    mimetype = 'application/json'
                    )
            return make_bad_params_value_response()
        #   return make_bad_params_value_response()

    except Exception as exception:
        result = make_response(json.dumps(
                    {'message'  : str(exception),
                    'category' : 'Internal server error',}),
                    500)
        return result
# @app.route("/generate_embedding",methods = ["POST"])
# @cross_origin(**api_cors)
# def create_embedding():
#     """
#     Generate Embedding of input file

#     Parameters:
#     None

#     Return:
#     str
#     """
#     try:
#         if request.method =="POST":
#             if os.path.exists('embedding.csv'):
#                os.remove('embedding.csv')
#             path_excel = glob.glob("uploads/*.xlsx")
#             path_csv = glob.glob("uploads/*.csv")
#             excel_file = len(path_excel)
#             csv_file = len(path_csv)
#             df_file = None
#             frame = []
#             if excel_file>0:
#                 for file in path_excel:
#                     frame.append(pd.read_excel(file))
#                 print(len(frame))
#                 print(csv_file)
#             elif csv_file>0:
#                 for file in path_excel:
#                     frame.append(pd.read_excel(file))
#             df_file = pd.concat(frame) 
#             if len(df_file)>0:
#                 resp = get_embedding(df_file)
#             if resp is False:
#                 result = make_response(json.dumps(
#                     {'message'  : 'File not created',
#                     'category' : 'Internal server error',}),
#                     500)
#                 return result
#             result = make_response(json.dumps(
#                     {'message'  : 'File created sucessfully',
#                     'category' : 'Ok',}),
#                     200)
#             return result
#     except FileNotFoundError:
#         result = make_response(json.dumps(
#                     {'message'  : "File not found",
#                     'category' : 'Internal server error',}),
#                     500)
#         return result
@app.errorhandler(404)
def page_not_found():
    """
    Not route Found Error 

    Parameters
    ----------
    None

    Return
    ------
    None
    """
    # note that we set the 404 status explicitly
    abort(400, {'message': 'custom error message to appear in body'})

if __name__ == "__main__":
    app.run(debug = True, host="0.0.0.0", port = 5001)
