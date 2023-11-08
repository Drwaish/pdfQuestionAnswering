# Flask API PDF Question/Answering

In this repo you will upload the pdf file and in response get id against your file. In future whenever you want to 
Question, send file id and question than our system will provide answer from that file.

Clone this repo 
```bash
git clone https://github.com/Drwaish/pdfQuestionAnswering.git
cd pdfQuestionAnswering
```
## Install Dependencies
```bash
pip install -r requirements.txt
```
## Upload file 

#### Post Request Body.
```
{
    data : <Attache file>
}
```
#### Response of above upload_file request
```
{
    message : File save successfully
    Access id : "<id>" 
}
```
## Query 
#### Post Request body
```
{
    data : <question>
    id   : "<id>"
}
```
#### Response of above query request
```
{
    "output" : predicted_data 
}
```
### Note
File id must be string type. 

### Set key in Header of request body.
```
api-key : "EnterMe"
```
