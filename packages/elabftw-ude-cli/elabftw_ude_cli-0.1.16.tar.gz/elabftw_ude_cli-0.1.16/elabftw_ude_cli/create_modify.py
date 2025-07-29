# import statements
import json
import requests
from . import config as Config
from . import read
import re


def create_experiment(data):
    """
    Creates and experiment
    :param data: dictionary of he new expereiment must have minimum the title
    :return: the experiment ID of the new experiment.
    """
    endpoint = Config.base_url + "experiments/"
    Config.headers['Content-Type'] = 'application/json'
    exp_id = ""
    response = requests.post(endpoint, headers=Config.headers, data=json.dumps(data))
    if response.status_code == 201:
        # Request was successful
        if Config.verbose >= 1: print("Request was successful.")
        if Config.verbose >= 2: print(response.headers['Location'])
        exp_id = response.headers['Location'].split("/")[-1]
        if Config.verbose >= 1: print(f"experiment ID: {exp_id}")
    elif response.status_code == 401:
        # Unauthorized - Invalid API key
        print("Unauthorized - Invalid API key.")
    else:
        # Request failed for some other reason
        print("Error:", response.status_code, response.text)
    return exp_id


def modify_experiment(exp_id_here, modify_data):
    """
    Adds and modifies the information in the experiment.
    :param exp_id_here: Experiment ID of the experiment.
    :param modify_data: The data to be added or changed.
    :return: Nothing.
    """
    url = Config.base_url + f"experiments/" + str(exp_id_here)
    Config.headers['Content-Type'] = 'application/json'

    # Define the data to be sent in the request body
    data = modify_data
    if Config.verbose >= 2: print(json.dumps(data))
    # Since Tags and Categories need different functions, we will pop them out/check for correctness and work on them first
    if "tags" in data:
        tags=data.pop("tags")
        tag_modifier(exp_id_here,tags)
    if "category" in data:
        if not data["category"].isdigit():
            data["category"]=identify_category_id(exp_id_here,data["category"])

    # Send the PATCH request
    response = requests.patch(url, headers=Config.headers, data=json.dumps(data))
    if Config.verbose >= 2: print(response.json())
    # Check the response status code
    if response.status_code == 200:
        if Config.verbose >= 1: print("Experiment updated successfully.")
    elif response.status_code == 400:
        print("Bad request. Check if the request body is correctly formatted.")
    else:
        print("Failed to update experiment. Status code:", response.status_code)
        print("Response:", response.text)


def add_steps(exp_id_here,steps_here, duplicate=False):
    """
    this function adds the steps to the new experiment
    :param exp_id_here: experiment_ID (can be retrieved from gui or from the create_experiment function
    :param steps_here: the list of steps containing the dictionary of the steps
    :return: nothing
    """
    url = Config.base_url + f"experiments/" + str(exp_id_here) +f"/steps"
    Config.headers['Content-Type'] = 'application/json'
    steps_in_exp=[x["body"] for x in requests.get(url=url, headers=Config.headers).json()]
    for step in steps_here:
        if step["body"] in steps_in_exp and duplicate==False:
            if Config.verbose >= 1: print(f"Step {step} already exists in experiment {exp_id_here}. Skipping. (Add duplicate=true to add anyway)")
            continue
        response = requests.post(url, headers=Config.headers, data=json.dumps(step))
        if response.status_code == 201:
            if Config.verbose >= 1: print(f"Added_Step: {step}")
        else:
            print(f"Failed to add step: {step}, Response: {response.text}")
            exit()

        if str(step['body']).__contains__("with protocol"):
            protocol_match = re.search(r'with protocol (\d+)', step['body'])
            if protocol_match:
                protocol_id = int(protocol_match.group(1))
                if Config.verbose >= 1: print(f"Found protocol ID: {protocol_id} in step: {step['body']}")

                # Link the protocol to the experiment
                link_payload = {"action": "create"}
                link_response = requests.post(
                    Config.base_url + f"experiments/" + str(exp_id_here)+"/items_links/"+str(protocol_id),
                    headers=Config.headers,
                    data=json.dumps(link_payload)
                )

                if link_response.status_code == 201:
                    if Config.verbose >= 1: print(f"Linked protocol ID {protocol_id} to experiment {exp_id_here}")
                else:
                    print(f"Failed to link protocol ID {protocol_id} to experiment {exp_id_here}: {link_response.text}")


def print_json_nicely(data):
    for x in dict(data):
        print(f"{x}:{data[x]}")

def identify_category_id(exp_id,category, create=True):
    target_team=read.read_experiment(exp_id)["team"]
    possible_categories=requests.get(f"{Config.base_url}teams/{target_team}/experiments_categories",headers=Config.headers).json()
    possible_category_titles=[str(x["title"]).lower() for x in possible_categories]
    possible_category_ids=[x["id"] for x in possible_categories]
    if category.lower() in possible_category_titles:
        return possible_category_ids[possible_category_titles.index(category.lower())]
    else:
        if not create:
            print(f"Warning: Category {category} not found in team {target_team}.\n"
                  f"(hint use create=true to create it if you are an admin for your team, else contact the team admin. )")
            return 0
        else:
            print(f"Warning: Category {category} not found in team {target_team}. Creating it.")
            new_category={"name":category, "default":0}
            response=requests.post(f"{Config.base_url}teams/{target_team}/experiments_categories",headers=Config.headers,json=new_category)
            if response.status_code==201:
                return response.json()["id"]
            else:
                print(f"Error: Failed to create category {category} in team {target_team}.\n"
                      f"If you are not an admin this is understandable, contact the team admin to create a category.")
                return 0

def complete_steps(exp_id_here, step_pattern_to_finish="step_1", done_by=None, change=None):
    """
    Complete one or more experiment steps that match a pattern.

    :param exp_id_here: ID of the experiment.
    :param step_pattern_to_finish: Pattern to match in the step body.
    :param done_by: Optional string to append to step body when marking done.
    :param change: None (default) = match exactly one;
                   'first' = complete first unfinished match;
                   'all' = complete all unfinished matches.
    """
    base_url = Config.base_url + f"experiments/{exp_id_here}/steps"
    Config.headers['Content-Type'] = 'application/json'

    # Get all steps
    all_steps = requests.get(base_url, headers=Config.headers).json()

    # Find matching steps
    matching_steps = [step for step in all_steps if step_pattern_to_finish in str(step['body'])]

    # Show all step statuses
    for step in all_steps:
        status = "finished" if step["finished"] == 1 else "not finished"
        if Config.verbose >= 1: print(f"{step['id']}: step is {status}")

    # Default: must have exactly one match
    if change is None:
        if len(matching_steps) != 1:
            print(f"Error: Found {len(matching_steps)} steps matching pattern '{step_pattern_to_finish}'. Aborting. Provide change=\"first\" or change=\"all\" to Solve this")
            return
        matching_steps = [matching_steps[0]]  # keep as list to reuse logic below

    elif change == "first":
        # Keep only the first unfinished matching step
        unfinished = [step for step in matching_steps if step["finished"] == 0]
        if not unfinished:
            print("No unfinished steps matching pattern.")
            return
        matching_steps = [unfinished[0]]

    elif change == "all":
        # Keep all unfinished matching steps
        matching_steps = [step for step in matching_steps if step["finished"] == 0]
        if not matching_steps:
            print("No unfinished steps matching pattern.")
            return

    else:
        raise ValueError("Invalid value for `change`. Use None, 'first', or 'all'.")

    # Process each step
    for step in matching_steps:
        if Config.verbose >= 1: print(f"\nProcessing step {step['id']}...")

        if step["finished"] == 0:
            if Config.verbose >= 1: print("Finishing step...")
            finish_response = requests.patch(
                f"{base_url}/{step['id']}",
                headers=Config.headers,
                data=json.dumps({"action": "finish"})
            )
            if Config.verbose >= 2: print(finish_response.json())
        else:
            if Config.verbose >= 1: print("Step already finished.")

        if done_by and "_done_by" not in step['body']:
            if Config.verbose >= 1: print(f"Updating step body with _done_by_{done_by}...")
            updated_body = step['body'] + f"_done_by_{done_by}"
            update_response = requests.patch(
                f"{base_url}/{step['id']}",
                headers=Config.headers,
                data=json.dumps({"body": updated_body})
            )
            if Config.verbose >= 2: print(update_response.json())


def tag_modifier(exp_id, tags):
    endpoint = f"{Config.base_url}experiments/{exp_id}/tags"
    tags = [str(x).lower() for x in tags]

    # Fetch current tags
    current_tags_response = requests.get(endpoint, headers=Config.headers)
    current_tags_json = current_tags_response.json()
    current_tags = [str(x["tag"]).lower() for x in current_tags_json]
    current_tag_ids = [x["tag_id"] for x in current_tags_json]

    # Add new tags
    for tag in tags:
        if tag not in current_tags:
            if Config.verbose >= 1:
                print(f"Adding tag {tag} to experiment {exp_id}")
            response = requests.post(endpoint, headers=Config.headers, json={"tag": tag})
            if Config.verbose >= 2:
                print(response.status_code, response.text)
        else:
            if Config.verbose >= 1:
                print(f"Tag {tag} already exists for experiment {exp_id}")

    # Remove tags that are no longer in the list
    for tag in current_tags:
        if tag not in tags:
            tag_id = current_tag_ids[current_tags.index(tag)]
            if Config.verbose >= 1:
                print(f"Removing tag {tag} from experiment {exp_id}")
            response = requests.patch(f"{endpoint}/{tag_id}", headers=Config.headers, json={"action": "unreference"})
            if Config.verbose >= 2:
                print(response.status_code, response.text)