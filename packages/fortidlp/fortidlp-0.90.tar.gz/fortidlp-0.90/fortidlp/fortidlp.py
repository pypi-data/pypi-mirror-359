
import re
import os
import json
from typing import BinaryIO, Optional
from fortidlp.auth import AuthenticationHandler
from fortidlp.connector import APIHandler

version = '0.1'

fortidlp_connection = APIHandler()

class Audit:
	'''
	Class Audit
	Description:  Return a list of audit logs.
	'''

	def get_audit_logs(self, filter: list = None, start_time: str = None, end_time: str = None, operation_types: list[str] = None, results_per_page: int = 100, sort_order: str = 'desc') -> dict:
		'''
		Class Audit
		Description:  Return a list of audit logs.
		
		Args:
			start_time (str): Start time for the logs in ISO format.
			end_time (str): End time for the logs in ISO format.
			limit (int): Number of logs to return.

		Returns:
			bool: Status of the request (True or False). 
			None: This function does not return any data.
		'''

		parameters = {}

		if filter:
			parameters["filter"] = filter if isinstance(filter, list) else [filter]
		if start_time or end_time:
			parameters["time_range"] = {}
		if start_time:
			parameters["time_range"]["start_time"] = start_time
		if end_time:
			parameters["time_range"]["to"] = end_time

		if operation_types:
			parameters["types"] = operation_types if isinstance(operation_types, list) else [operation_types]

		url = '/api/v1/audit/search'

		url = f"{url}?results_per_page={results_per_page}&sort_order={sort_order}"

		return fortidlp_connection.send(url, params=parameters)
	
class Cases:

	def list_cases(self, content_event_uri: Optional[str] = None, content_operated_by: Optional[str] = None, created_by: Optional[str] = None) -> dict:
		'''
		Class Cases
		Description:  Return a list of cases.
		
		Args:
			content_event_uri: "string",
			content_operated_by: "string",
			created_by: "string"

		Returns:
			bool: Status of the request (True or False). 
			None: This function does not return any data.
		'''

		url = '/api/v1/cases'
		parameters = {}
		
		if content_event_uri:
			parameters["content_event_uri"] = content_event_uri
		if content_operated_by:
			parameters["content_operated_by"] = content_operated_by
		if created_by:
			parameters["created_by"] = created_by

		return fortidlp_connection.get(url, params=parameters)

	def delete_case(self, case_id: str) -> dict:
		'''
		Class Cases
		Description:  Deletes a case.
		
		Args:
			case_id (str): The ID of the case to delete.

		Returns:
			bool: Status of the request (True or False). 
			None: This function does not return any data.
		'''

		url = f'/api/v1/cases/{case_id}'
		return fortidlp_connection.delete(url)

class Operators:
	''''''

	def list_operators(self) -> dict:
		'''
		Class Operators
		Description:  Return a list of operators.
        
		Args:

		Returns:
			bool: Status of the request (True or False). 
			None: This function does not return any data.
		'''

		url = '/api/v1/operators'
		return fortidlp_connection.get(url)

	def create_operator(self, username:str, name: str, email: str, company: str, password: str, role, link_expiration: int = 1, password_reset_on_login: bool = True ) -> tuple[bool, None]:
		'''
		Class Operators
		Description:  Adds a new operator.
        
		Args:

		Returns:
			bool: Status of the request (True or False). 
			None: This function does not return any data.
		'''

		url = '/api/v1/operators'

		data = {
			"operator": {
				"company": company,
				"display_name": name,
				"email": email,
				"name": username,
				"roles": [
					role
				],
			},
			"passphrase": password,
			"passphrase_reset_link_expiry_duration": link_expiration,
			"passphrase_reset_on_login": password_reset_on_login
		}

		return fortidlp_connection.send(url, params=data)
		
	def delete_operator(self, operator_id: str) -> dict:
		'''
		Class Operators
		Description:  Deletes an operator.
		
		Args:
			operator_id (str): The ID of the operator to delete.

		Returns:
			bool: Status of the request (True or False). 
			None: This function does not return any data.
		'''
		url = f'/api/v1/operators/{operator_id}'
		return fortidlp_connection.delete(url)

class Users:
	'''
	Class Users
	Description:  Return a list of users.
	'''

	def get_users(self) -> tuple[bool, None]:
		'''
		Class Users
		Description:  Return a list of users.
		
		Args:

		Returns:
			bool: Status of the request (True or False). 
			None: This function does not return any data.
		'''

		url = '/api/v1/users'
		return fortidlp_connection.get(url)
	
	# Function to create a users, that might contain the following data as input:
	# {
	# "address_home": "123 Street Name, New York 12401, United States",
	# "address_office": "123 Street Name, New York 12401, United States",
	# "department": "Accounting",
	# "description": "string",
	# "directory_labels": [
	# 	{
	# 	"category": "DIRECTORY",
	# 	"name": "Department | Accounting"
	# 	}
	# ],
	# "email": "john.smith@example.com",
	# "image_content": "string",
	# "juid": "5b07da47-86a8-4fc2-a7d8-3241b74270ca",
	# "manager": "Liz Brown",
	# "manager_unique_id": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
	# "name": "John Smith",
	# "phone_number_mobile": "+1 234 555 6789",
	# "phone_number_office": "+1 234 555 6789",
	# "sync_info": {
	# 	"sync_invocation_id": "5b07da47-86a8-4fc2-a7d8-3241b74270ca",
	# 	"sync_source": "ldap://5b07da47-86a8-4fc2-a7d8-3241b74270ca"
	# },
	# "title": "Finance Assistant",
	# "unique_data": "S-1-5-21-3623811015-3361044348-30300820-1013",
	# "unique_id": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
	# "user_uri": [
	# 	"mail://john.smith@example.com",
	# 	"sid://S-1-5-21-3623811015-3361044348-30300820-1013@domain"
	# ]
	# }

	def create_user(self, address_home: str = None, address_office: str = None, department: str = None, description: str = None, directory_labels: str = None, category: str = None,  label_name: str = None, name: str = None, email: str = None, image_content: str = None, juid: str = None, manager: str = None, manager_unique_id: str = None, phone_number_mobile: str = None, phone_number_office: str = None, sync_info: str = None, sync_invocation_id: str = None, sync_source: str = None, title: str = None, unique_data: str = None, unique_id: str = None, user_uri: str = None) -> tuple[bool, None]:
		
		user = {
			"address_home": address_home,
			"address_office": address_office,
			"department": department,
			"description": description,
			"directory_labels": directory_labels,
			"email": email,
			"image_content": image_content,
			"juid": juid,
			"manager": manager,
			"manager_unique_id": manager_unique_id,
			"name": name,
			"phone_number_mobile": phone_number_mobile,
			"phone_number_office": phone_number_office,
			"sync_info": {
				"sync_invocation_id": sync_invocation_id,
				"sync_source": sync_source
			},
			"title": title,
			"unique_data": unique_data,
			"unique_id": unique_id,
		}

		url = '/api/v1/admin/users'

		return fortidlp_connection.send(url, params=user)

class Policies:
	'''
	Class Policies
	Description:  Return a list of policies.
	'''

	def create_policies_groups(self, description: str, exclude_labels: list[str], include_labels: list[str], match: str, name: str) -> tuple[bool, None]:
		'''
		Class Policies
		Description:  Create a new policies group.

		Args:
			description (str): The description of the policies group.
			exclude_labels (list[str]): The labels to exclude.
			include_labels (list[str]): The labels to include.
			match (str): The match criteria.
			name (str): The name of the policies group.

		Returns:
			bool: Status of the request (True or False). 
			None: This function does not return any data.
		'''

		url = '/api/v1/policies/groups'
		return fortidlp_connection.send(url)

	def list_policies_groups(self) -> tuple[bool, None]:
		'''
		Class Policies
		Description:  Return a list of policies.
		
		Args:

		Returns:
			bool: Status of the request (True or False). 
			None: This function does not return any data.
		'''

		url = '/api/v1/policies/groups'
		return fortidlp_connection.get(url)

	def delete_policy_group(self, group_id: str) -> dict:
		'''
		Class Policies
		Description:  Delete a policies group.
		
		Args:
			group_id (str): The ID of the policies group to delete.

		Returns:
			bool: Status of the request (True or False). 
			None: This function does not return any data.
		'''

		url = f'/api/v1/policies/groups/{group_id}'
		return fortidlp_connection.delete(url)

	def export_policy_groups(self, group_ids: list[str], include_data_objects: bool = True, include_labels: bool = True) -> tuple[bool, None]:
		'''
		Class Policies
		Description:  Export policy groups.
		
		Args:
			group_ids (list[str]): List of policy group IDs to export.

		Returns:
			bool: Status of the request (True or False). 
			None: This function does not return any data.
		'''

		url = '/api/v1/policies/export'
		data = {
			"group_ids": group_ids,
			"include_data_objects": include_data_objects,
			"include_labels": include_labels
		}
		return fortidlp_connection.download(url, params=data)

	def list_policies_data(self) -> tuple[bool, None]:
		'''
		Class Policies
		Description:  Return a list of policies data.
		
		Args:

		Returns:
			bool: Status of the request (True or False). 
			None: This function does not return any data.
		'''

		url = '/api/v1/policies/data'
		return fortidlp_connection.get(url)

	def delete_policy_asset(self, asset_id: str) -> dict:
		'''
		Class Policies
		Description:  Delete a specific policy asset.
		
		Args:
			asset_id (str): The ID of the policy asset to delete.

		Returns:
			bool: Status of the request (True or False). 
			None: This function does not return any data.
		'''

		url = f'/api/v1/policies/data/{asset_id}'
		return fortidlp_connection.delete(url)

class PoliciesData:
	'''
	Class PoliciesData
	Description:  Return a list of policies data.
	'''

	def list_policies_data(self, filter: list = None, results_per_page: int = 100) -> tuple[bool, None]:
		'''
		Class PoliciesData
		Description:  Return a list of policies data.
		
		Args:
			filter (list): List of filters to apply to the policies data.
			results_per_page (int): Number of results per page.

		Returns:
			bool: Status of the request (True or False). 
			None: This function does not return any data.
		'''

		url = '/api/v1/policies/data'
		return fortidlp_connection.get(url)

	def get_policy_data(self, policy_id: str) -> tuple[bool, None]:
		'''
		Class PoliciesData
		Description:  Return a specific policy data.
		
		Args:
			policy_id (str): The ID of the policy data to retrieve.

		Returns:
			bool: Status of the request (True or False). 
			None: This function does not return any data.
		'''

		url = f'/api/v1/policies/data/{policy_id}'
		return fortidlp_connection.get(url)
	
	def delete_policy_data(self, policy_id: str) -> tuple[bool, None]:
		'''
		Class PoliciesData
		Description:  Delete a specific policy data.
		
		Args:
			policy_id (str): The ID of the policy data to delete.

		Returns:
			bool: Status of the request (True or False). 
			None: This function does not return any data.
		'''

		url = f'/api/v1/policies/data/{policy_id}'
		return fortidlp_connection.delete(url)

class Incidents:
	'''
	Class Incidents
	Description:  Return a list of incidents.
	'''

	def search_incidents(self, filter: list = [], include_agents: str = True, include_cluster_data: str = True, include_labels: str = True, include_users: str = True, results_per_page: int = 100) -> dict:
		'''
		Class Incidents
		Description:  Return a list of incidents.
		
		Args:
			filter (list): List of filters to apply to the incidents.
			include_agents (bool): Whether to include agents in the response.
			include_cluster_data (bool): Whether to include cluster data in the response.
			include_labels (bool): Whether to include labels in the response.
			include_users (bool): Whether to include users in the response.

		Returns:
			bool: Status of the request (True or False). 
			None: This function does not return any data.
		'''

		parameters = {
			"filter": filter if isinstance(filter, list) else [filter]
		}
		if include_agents:
			parameters["include_agents"] = include_agents
		if include_cluster_data:
			parameters["include_cluster_data"] = include_cluster_data
		if include_labels:
			parameters["include_labels"] = include_labels
		if include_users:
			parameters["include_users"] = include_users

		url = '/api/v2/incidents/search'
		if results_per_page:
			url = f"{url}?results_per_page={results_per_page}"
		
		return fortidlp_connection.send(url, params=parameters)

	# Function to update incident status:
	# This function receives: {
	# "all": true,
	# "filter": [ ],
	# "reason": "string",
	# "status": "RESOLVE"
	# }

	def update_status(self, status: str, all: Optional[bool] = None, filter: Optional[list] = None, reason = None) -> dict:
		'''
		Class Incidents
		Description:  Update the status of incidents.
		
		Args:
			all (bool): Whether to update all incidents.
			filter (list): List of filters to apply to the incidents.
			reason (str): Reason for the status update.
			status (str): New status for the incidents.

		Returns:
			bool: Status of the request (True or False). 
			None: This function does not return any data.
		'''

		parameters = {
			"status": status
		}
		if filter and not all:
			parameters["filter"] = filter if isinstance(filter, list) else [filter]
		if all and not filter:
			parameters["all"] = all
		if reason:
			parameters["reason"] = reason
		
		url = '/api/v2/incidents/status'
		return fortidlp_connection.send(url, params=parameters)

class SaaS:
	'''
	Class SaaS
	Description:  Return a list of SaaS applications.
	'''

	def change_state(self, state: str, reason: str, all: Optional[bool] = None, filter: Optional[list] = None) -> dict:
		'''
		Class SaaS
		Description:  Change the state of a SaaS application.
		
		Args:
			state (str): The new state for the SaaS application.
			all (bool): Whether to apply the state change to all applications.
			filter (list): List of filters to apply to the SaaS applications.
			reason (str): Reason for the state change.

		Returns:
			bool: Status of the request (True or False). 
			None: This function does not return any data.
		'''

		url = f'/api/v2/saas-applications/state'
		data = {
			"state": state,
			"reason": reason,
		}
		if all and not filter:
			data["all"] = all
		if not all and filter:
			data["filter"] = filter if isinstance(filter, list) else [filter]

		return fortidlp_connection.send(url, params=data)

class Agents:
	'''
	Class Agents
	Description:  Return a list of agents.
	'''

	def get_agents(self, filter: list = [], results_per_page: int = 100, sort_order: str = "asc", cursor: Optional[str] = None) -> dict:
		'''
		Class Agents
		Description:  Return a list of agents.
		
		Args:
			filter: (list): List of filters to apply to the agents.
			include_actions: (bool): Whether to include actions in the response.
			include_health: (bool): Whether to include health data in the response.
			include_labels: (bool): Whether to include labels in the response.
			include_users: (bool): Whether to include users in the response.

		Returns:
			bool: Status of the request (True or False). 
			None: This function does not return any data.
		'''

		url = f'/api/v2/agents/search'

		parameters = {}
		if filter:
			parameters["filter"] = filter if isinstance(filter, list) else [filter]
		if cursor:
			parameters["cursor"] = cursor

		if results_per_page:
			url = f"{url}?results_per_page={results_per_page}&sort_order={sort_order}"
		
		return fortidlp_connection.send(url, params=parameters)

	def update_status(self, filter: Optional[list], new_state: Optional[str], reason: Optional[str]) -> dict:
		'''
		Class Agents
		Description:  Update the status of agents.
		
		Args:
			filter (list): List of filters to apply to the agents.
			new_state (str): New state for the agents.
			reason (str): Reason for the status update.

		Returns:
			bool: Status of the request (True or False). 
			None: This function does not return any data.
		'''

		url = f'/api/v2/agents/state'
		data = {
			"new_state": new_state,
			"reason": reason
		}
		if filter:
			data["filter"] = filter if isinstance(filter, list) else [filter]

		return fortidlp_connection.send(url, params=data)

	# Function Delete archived agents
	#{
	# "agent_ids": [
	# 	"string"
	# ],
	# "archived_days": "string",
	# "inactive_days": 0,
	# "never_reported": true,
	# "revoked_days": "string"
	# }

	def delete_archived_agents(self, agent_ids: list, archived_days: Optional[str] = None, inactive_days: Optional[int] = None, never_reported: Optional[bool] = None, revoked_days: Optional[str] = None) -> dict:

		data = {
			"agent_ids": agent_ids if isinstance(agent_ids, list) else [agent_ids]
		}
		
		if archived_days:
			data["archived_days"] = archived_days
		if inactive_days:
			data["inactive_days"] = inactive_days
		if never_reported is not None:
			data["never_reported"] = never_reported
		if revoked_days:	
			data["revoked_days"] = revoked_days

		print(json.dumps(data, indent=4))

		url = '/api/v1/admin/agents/archived/delete'
		return fortidlp_connection.insert(url, params=data)

	def assign_labels(self, agent_ids: list[str], label_ids: list[str]) -> dict:
		'''
		Class Labels
		Description:  Assign labels to agents.
		
		Args:
			agent_ids (list[str], optional): List of agent IDs to assign labels to.
			label_ids (list[str], optional): List of label IDs to assign.

		Returns:
			bool: Status of the request (True or False).
			None: This function does not return any data.
		'''
	
		url = '/api/v1/admin/agents/labels/add'
		param = {
			"agent_ids": agent_ids if isinstance(agent_ids, list) else [agent_ids],
			"label_ids": label_ids if isinstance(label_ids, list) else [label_ids]
		}
		
		return fortidlp_connection.insert(url, params=param)

	def unassign_labels(self, agent_ids: list[str], label_ids: list[str]) -> dict:
		'''
		Class Labels
		Description:  Unassign labels from agents.
		Args:
			agent_ids (list[str], optional): List of agent IDs to unassign labels from.
			label_ids (list[str], optional): List of label IDs to unassign.
		Returns:
			bool: Status of the request (True or False).
			None: This function does not return any data.
		'''

		url = '/api/v1/admin/agents/labels/remove'
		param = {
			"agent_ids": agent_ids if isinstance(agent_ids, list) else [agent_ids],
			"label_ids": label_ids if isinstance(label_ids, list) else [label_ids]
		}
		return fortidlp_connection.insert(url, params=param)

class AgentConfigs:

	def get_agent_configs(self) -> dict:
		'''
		Class AgentConfigs
		Description:  Get all agent configurations.

		Returns:
			dict: The response from the API.
		'''
		url = '/api/v1/agent-configs'
		return fortidlp_connection.get(url)
	

	def delete_agent_config(self, config_id: str) -> dict:
		'''
		Class AgentConfigs
		Description:  Delete an agent configuration.
		
		Args:
			config_id (str): The ID of the agent configuration to delete.

		Returns:
			bool: Status of the request (True or False). 
			None: This function does not return any data.
		'''

		url = f'/api/v1/agent-configs/{config_id}'
		return fortidlp_connection.delete(url)

class Labels:
	'''Class Labels
	Description:  Return a list of labels.
	'''

	def create(self, name: str, description: Optional[str] = None, category: Optional[str] = None, anonymise: Optional[bool] = False, flagged: Optional[bool] = False) -> dict:
		'''
		Class Labels
		Description:  Create a new label.
		
		Args:
			name (str): The name of the label - Mandatory.
			description (str, optional): The description of the label.
			category (str, optional): The category of the label.
			anonymise (bool, optional): Whether to anonymise the label. Defaults to False.
			flagged (bool, optional): Whether the label is flagged. Defaults to False.

		Returns:
			bool: Status of the request (True or False). 
			None: This function does not return any data.
		'''

		url = '/api/v1/labels'
		data = {
			"name": name,
		}
		if description:
			data["description"] = description
		if category:
			data["category"] = category
		if anonymise is not None:
			data["anonymise"] = anonymise
		if flagged is not None:
			data["flagged"] = flagged

		return fortidlp_connection.send(url, params=data)

	def delete(self, id: str, force: Optional[bool] = False) -> dict:
		'''
		Class Labels
		Description:  Delete a label by its ID.
		
		Args:
			id (str): The ID of the label to delete.
			force (bool, optional): Whether to force delete the label. Defaults to False.

		Returns:
			bool: Status of the request (True or False).
			None: This function does not return any data.
		'''

		url = f'/api/v1/labels/{id}'
		return fortidlp_connection.delete(url)

	def get_labels(self, filter: list = [], results_per_page: int = 100, sort_order: str = "asc", cursor: Optional[str] = None) -> dict:
		'''	
		Class Labels
		Description:  Return a list of labels.
		Args:
			filter (list): List of filters to apply to the labels.
			results_per_page (int): Number of results per page.
			sort_order (str): Sort order for the results, either "asc" or "desc".
			cursor (str, optional): Cursor for pagination.
		Returns:	

			bool: Status of the request (True or False).
			None: This function does not return any data.
		'''
		url = '/api/v1/labels/search'
		parameters = {}
		if filter:
			parameters["filter"] = filter if isinstance(filter, list) else [filter]
		
		if results_per_page:
			url = f"{url}?results_per_page={results_per_page}"
		if sort_order:
			url = f"{url}&sort_order={sort_order}"
		if cursor:
			url = f"{url}&cursor={cursor}"

		return fortidlp_connection.send(url, params=parameters)

debug = None
ssl_verification = True
    
def ignore_certificate():
	global ssl_verification
	ssl_verification = False
	print("[!] - We strongly advise you to enable SSL validations. Use this at your own risk!")

def enable_debug():
	global debug
	debug = True

def auth( host: str, access_token: str):
	global debug
	global fortidlp_connection
	login = AuthenticationHandler()

	# ManagementHost = re.search(r'(https?://)?(([a-zA-Z0-9]+)(\.[a-zA-Z0-9.-]+))', host)
	# host = ManagementHost.group(2)

	headers, host = login.get_headers(
		fdlp_host=host,
		access_token=access_token,
	)

	if headers is None:
		status = False
		data = host
	else:
		status = True
		data = 'AUTHENTICATION_SUCCEEDED'

		fortidlp_connection = APIHandler()
		authentication = fortidlp_connection.conn(headers, host, debug, ssl_verification)

		cur_dir = os.path.dirname(__file__)

	return {
		'status': status,
		'data': data
	}
