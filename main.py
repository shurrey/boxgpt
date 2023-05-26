import json
import os

from boxsdk import Client, OAuth2
from config import AppConfig

import quart
import quart_cors
from quart import request

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

_TODOS = {}

# Keep track of todo's. Does not persist if Python session is restarted.
def get_auth(token):
    oauth = OAuth2(
        client_id=AppConfig().client_id,
        client_secret=AppConfig().client_secret,
        access_token=token.split()[1]
    )

    return oauth

@app.post("/todos/<string:username>")
async def add_todo(username):
    request = await quart.request.get_json(force=True)
    if username not in _TODOS:
        _TODOS[username] = []
    _TODOS[username].append(request["todo"])
    return quart.Response(response='OK', status=200)

@app.get("/folders")
async def get_folders():
    print(request.headers)
    print(request.headers['Authorization'])
    return quart.Response(response='OK', status=200)

@app.get("/files")
async def get_files():
    print(request.headers)
    print(request.headers['Authorization'])

    oauth = get_auth(request.headers['Authorization'])

    client = Client(oauth)

    items = client.folder(folder_id='0').get_items()

    itemsArray = []

    for item in items['entries']:
        itemsArray.append({
            "id": item.id,
            "type": item.type,
            "name": item.name
        })
    
    return quart.Response(itemsArray, status=200)

@app.delete("/todos/<string:username>")
async def delete_todo(username):
    request = await quart.request.get_json(force=True)
    todo_idx = request["todo_idx"]
    # fail silently, it's a simple plugin
    if 0 <= todo_idx < len(_TODOS[username]):
        _TODOS[username].pop(todo_idx)
    return quart.Response(response='OK', status=200)

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
