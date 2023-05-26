import json
import os

from boxsdk import Client, OAuth2
from config import AppConfig
import requests

import quart
import quart_cors
from quart import request

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")


'''
    Take the access token from ChatGPT and generate a new Box SDK Auth object
'''
def get_auth(access_token):
    oauth = OAuth2(
        client_id=AppConfig().client_id,
        client_secret=AppConfig().client_secret,
        access_token=access_token.split()[1]
    )

    return oauth

'''
    Call the Box API to get a list of files and folders, build the response body, and return
    it to the calling function so it can send it to chatgpt
'''
def get_files_from_box(access_token, folder_id):
    print(f"build_json_response: access_token: {access_token}, folder_id: {folder_id}")
    
    oauth = get_auth(access_token)

    client = Client(oauth)

    items = client.folder(folder_id=folder_id).get_items()
    
    print(f"items {items}, objectType {type(items)}")

    itemsArray = []

    for item in items:
        itemsArray.append({
            "id": item.id,
            "type": item.type,
            "name": item.name
        })

    print(f"itemsArray {itemsArray}")

    return json.dumps(itemsArray)

'''
    Fetch the contents of the root folder
'''
@app.get("/folders")
async def get_folders():
    print(f"get_folders: access_token: {request.headers['Authorization']}")
    
    response_body=get_files_from_box(request.headers['Authorization'], 0)
    
    return quart.Response(response=response_body, status=200)

'''
    Fetch the contents of a specific folder
'''
@app.get("/folders/<string:folder_id>")
async def get_folders_by_id(folder_id):
    print(f"get_folders_by_id: access_token: {request.headers['Authorization']}, folder_id: {folder_id}")
    
    response_body=get_files_from_box(request.headers['Authorization'], folder_id)
    
    return quart.Response(response=response_body, status=200)

'''
    Get the contents of a file
'''
@app.get("/files/content/<string:file_id>")
async def get_file_content(file_id):
    print(f"get_file_content: access_token: {request.headers['Authorization']}, folder_id: {file_id}")

    content_url=f"https://dl.boxcloud.com/api/2.0/internal_files/{file_id}/versions/0/representations/extracted_text/content/?access_token={request.headers['Authorization'].split()[1]}"

    r = requests.get(url=content_url)

    return quart.Response(response=r.text, status=200)


# ChatGPT registration endpoints
@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")

@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")

def main():
    port = int(os.environ.get('PORT', 33507))
    app.run(debug=True, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
