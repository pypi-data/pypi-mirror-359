import requests

def hello():
    print("Hello from Tapestry!")


def fetch_library_data(token, folder_details):
    folder_name = folder_details.get("name")
    tapestry_id = folder_details.get("tapestry_id")

    url =  "https://inthepicture.org/admin/library"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    data = {
        "limit": 10,
        "page": 1,
        "active": "grid",
        "group_id": [],
        "tapestry_id": tapestry_id,
        "parent": folder_name,
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Request failed with status code {response.status_code}", "details": response.text}

def image_to_text(token, user_prompt, document, name ,system_prompt=""):

    url =  "https://inthepicture.org/admin/image_to_text"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    data = {
        "user_prompt": user_prompt,
        "document": document,
        "sytem_prompt": system_prompt,
        "name": name
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Request failed with status code {response.status_code}", "details": response.text}

def fetch_group_data(token, group_ids,tapestry_id,name):

    url =  "https://inthepicture.org/admin/fetch_group_data"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    data = {
        "group_ids": group_ids,
        "tapestry_id": tapestry_id
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Request failed with status code {response.status_code}", "details": response.text}

def selected_document_data(token, document_ids,tapestry_id,name):

    url =  "https://inthepicture.org/admin/selected_document_data"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    data = {
        "document_ids": document_ids,
        "tapestry_id": tapestry_id,
        "name": name
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Request failed with status code {response.status_code}", "details": response.text}








