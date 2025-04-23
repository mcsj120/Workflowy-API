from datetime import date
import json

from workflowy import workflowy_client as wf
from workflowy import workflowy_list as wfl


with open('config.json', 'r') as config_file:
    config = json.load(config_file)
    username = config['username']
    password = config['password']

session_id = wf.WorkFlowyClient.login(username, password)
client = wf.WorkFlowyClient(session_id)

main = client.get_main_list()
node = main.get_list_by_name_nested(['Mikey\'s Work', 'Schedule'])


def get_text(node: wfl.WorkFlowyList, depth: int) -> str:
    text = ("\t" * depth)  + node.name + "\n"
    for i in node.sublists:
        text += get_text(i, depth + 1)
    return text

text = ""
for i in node.sublists:
    text += get_text(i, 0) + "\n"

file_name = f"{date.today().strftime('%y-%m-%d')}.txt"
with open(file_name, 'w') as file:
    file.write(text)


x = 5