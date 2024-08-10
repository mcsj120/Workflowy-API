from datetime import date

from workflowy import workflowy_client as wf

#TODO: add code to read from .env file
username = ""
password = ""

session_id = wf.WorkFlowyClient.login()
client = wf.WorkFlowyClient(session_id)

main = client.get_main_list()
node = main.get_list_by_name_nested(['Mikey\'s Work', 'Mikey\'s Problems', 'Env', 'QA'])
node.create_sublist(str(date.today()))

problems = node.get_list_by_name(str(date.today()))