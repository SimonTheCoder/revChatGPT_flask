from flask import Flask, request, jsonify
import json
import os
import sys

app = Flask(__name__)
from revChatGPT.V1 import Chatbot
__chatbot = None
__session_list = None
def get_chatbot() -> Chatbot:

    if __chatbot is not None:
        return __chatbot, __session_list

    # load __seesion_list from ./session_list.json. If not found, create a new one
    if os.path.exists('./session_list.json'):
        with open('./session_list.json') as f:
            __session_list = json.load(f)
    else:
        __session_list = []
        #save __session_list to ./session_list.json
        with open('./session_list.json', 'w') as f:
            json.dump(__session_list, f)


    # read config from "~/.config/revChatGPT/config.json"

    # check if config file exists
    if  os.path.exists( os.path.expanduser('~/.config/revChatGPT/config.json')):    
        with open(os.path.expanduser('~/.config/revChatGPT/config.json')) as f:
            config = json.load(f)
    else:
        config = {
              "email": "email",
              "password": "your password"
        }
    print(config)
    return Chatbot(config),__session_list

@app.route('/chat', methods=['POST'])
def handle_post():
    data = request.get_json()
    prompt = data.get("prompt", "")

    result = {}

    if len(prompt) == 0:
        result["error"] = "prompt is empty"
        return jsonify(result)

    session_id = data.get("session_id", "")

    chatbot,session_list = get_chatbot()

    # search session_id from session_list which with the structure:
    #  [ {"session_id": "<session_id>","parenet_id": "<session_id>"}, "conversation_id": "<conversation_id>"} ]
    for session in session_list:
        if session["session_id"] == session_id:
            parent_id = session["parent_id"]
            conversation_id = session["conversation_id"]
            break
    else:
        parent_id = None
        conversation_id = None        

    # print a log about conversation_id and parent_id like this:
    #  [ {"session_id": "<session_id>","parenet_id": "<session_id>"}, "conversation_id": "<conversation_id>"} ]
    print(f"session_id: {session_id}, parent_id: {parent_id}, conversation_id: {conversation_id}")


    response = chatbot.ask(prompt=prompt, conversation_id=conversation_id, parent_id=None)

    last_response = list(response)[-1]

    print(last_response)

    if parent_id is None or conversation_id is None:
        conversation_id = last_response["conversation_id"]
        parent_id = last_response["parent_id"]

        chatbot.change_title(conversation_id, session_id)
        new_session = {}
        new_session["session_id"] = session_id
        new_session["parent_id"] = parent_id
        new_session["conversation_id"] = conversation_id
        session_list.append(new_session)
        with open('./session_list.json', 'w') as f:
            json.dump(session_list, f)
    result["response"] = last_response["message"]

    return jsonify(result)


if __name__ == '__main__':

    # read host and port from sys.argv. If not found, use default
    if len(sys.argv) > 1:
        host = sys.argv[1]
        port = sys.argv[2]
    else:
        host = '0.0.0.0'
        port = 5000

    app.run(host=host, port=port)

# curl -X POST -H "Content-Type: application/json" -d '{"session_id": "test_session", "prompt": "请帮我生成一个检查live的flask函数，使用GET方法。"}' http://127.0.0.1:5000/chat