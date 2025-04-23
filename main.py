from datetime import date
import json

from workflowy import workflowy_client as wf

with open('config.json', 'r') as config_file:
    config = json.load(config_file)
    username = config.get['username']
    password = config.get['password']

session_id = wf.WorkFlowyClient.login(username, password)
client = wf.WorkFlowyClient(session_id)

main = client.get_main_list()
node = main.get_list_by_name_nested(['Mikey\'s Work', 'Mikey\'s Problems', 'Env', 'QA'])
node.create_sublist(str(date.today()))

problems = node.get_list_by_name(str(date.today()))