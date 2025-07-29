import json
import requests
import urllib3
import warnings
import logging
import time
from copy import deepcopy
from rocketcontent.content_services_api import ContentServicesApi
from rocketcontent.content_config import ContentConfig
from rocketcontent.util import validate_id

# Disable https warnings if the http certificate is not valid
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

class ContentAdmArchivePolicy:

    def __init__(self, content_config):

        if isinstance(content_config, ContentConfig):
            self.repo_admin_url = content_config.repo_admin_url
            self.logger = content_config.logger
            self.headers = deepcopy(content_config.headers)
        else:
            raise TypeError("ContentConfig class object expected")

    #--------------------------------------------------------------
    # Verify if Archivig Policy definition exists
    # This method checks if a Archivig Policy with the specified id exists.
    # It returns True if the Archivig Policyexists, otherwise returns False.
    # If an error occurs during the request or JSON parsing, it logs the error and returns False.
    def verify_archiving_policy(self, ap_id) -> bool:
        """
        Verifies if a Archivig Policy the specified name exists by querying the admin reports API.
        Args:
            ap_id (str): The ID of the Archivig Policy to verify.
        Returns:
            bool: True if an item with the given ID exists in the response, False otherwise.
        Raises:
            requests.HTTPError: If the HTTP request to the API fails.
            json.JSONDecodeError: If the response cannot be parsed as JSON.
        Logs:
            - Method name, request URL, and headers for debugging purposes.
        """
        try:
            local_headers = deepcopy(self.headers)
            local_headers['Accept'] = 'application/vnd.asg-mobius-admin-topic-groups.v1+json'

            tm = str(int(time.time() * 1000))
            archiving_policy_get_url = self.repo_admin_url + f"/archivingpolicies?limit=5&&groupid={ap_id}&timestamp={tm}"

            self.logger.info("--------------------------------")
            self.logger.info("Method : verify_archiving_policy")
            self.logger.debug(f"URL : {archiving_policy_get_url}")
            self.logger.debug(f"Headers : {json.dumps(local_headers)}")
                         
            # Send the request
            response = requests.get(archiving_policy_get_url, headers=local_headers, verify=False)
            
            # Check if the HTTP request was successful
            response.raise_for_status()
            
            # Parse JSON from response
            data = response.json()
          
            # Get items list, default to empty list if not found
            items = data.get("items", [])
            
            # Check each item for id == "AAA01"
            for item in items:
                if item.get("id") == ap_id:
                    return True
            return False
        
        except requests.HTTPError as e:
            self.logger.error(f"HTTP error occurred: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return False       
        

    #--------------------------------------------------------------
    # Import an archiving policy
    def import_archiving_policy(self, archiving_policy_path, archiving_policy_name):
        """
        Import an archiving policy by reading a JSON file and sending it via POST request.
        
        Args:
            archiving_policy_path (str): Path to the JSON file containing the archiving policy.
            archiving_policy_name (str): Name of the archiving policy.
        
        Returns:
            int: HTTP status code of the response, or None if an error occurs.
        """

            # Check if output directory exists
        if not validate_id(archiving_policy_name):
                raise ValueError(f"Not valid archiving policy name: '{archiving_policy_name}'.")
        
        if self.verify_archiving_policy(archiving_policy_name):
            self.logger.error(f"Archivig Policy with name '{archiving_policy_name}' already exists.")
            return 409

        import_archive_policy_url = self.repo_admin_url + "/archivingpolicies"

        self.headers ['Content-Type'] = 'application/vnd.asg-mobius-admin-archiving-policy.v1+json'

        # Read the archiving policy file
        try:
            with open(archiving_policy_path, 'r', encoding='utf-8') as file:
                body = file.read()

            json_data = json.loads(body)

             # Replace root-level 'name' if it matches old_value
            if isinstance(json_data, dict) and "name" in json_data:
                json_data["name"] = archiving_policy_name


        except FileNotFoundError:
            self.logger.error(f"Archiving policy file not found: {archiving_policy_path}")
            return None
        except UnicodeDecodeError:
            self.logger.error(f"Failed to decode file as UTF-8: {archiving_policy_path}")
            return None
        except Exception as e:
            self.logger.error(f"Error reading archiving policy file: {e}")
            return None

        self.logger.info("--------------------------------")
        self.logger.info("Method: import_archive_policy")
        self.logger.debug(f"URL: {import_archive_policy_url}")
        self.logger.debug(f"Headers: {json.dumps(self.headers, indent=2)}")
        self.logger.debug(f"Body: \n{json.dumps(json_data, indent=2)}")

        try:
            # Send the POST request
            response = requests.post(import_archive_policy_url, headers=self.headers, data=json.dumps(json_data, indent=2), verify=False)

            #self.logger.debug(f"Response: {response.text}")

            return response.status_code
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error importing archiving policy: {e}")
            return None            

# Ejecutar la función
if __name__ == "__main__":

        # Configure logger
    logging.getLogger('urllib3').setLevel(logging.CRITICAL)
    logging.getLogger('requests').setLevel(logging.CRITICAL)

    logger = logging.getLogger('')
    logger.handlers = []
    logger.setLevel(getattr(logging, "DEBUG"))
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

    config_file = 'C:\\git\\content-python-library\\dev\conf\\rocketcontent.yaml'  # Ensure this file exists
    content_obj = ContentServicesApi(config_file)


    content_adm_archive_policy = ContentAdmArchivePolicy(content_obj.config)

    status = content_adm_archive_policy.import_archiving_policy(
        archiving_policy_path='C:\\git\\content-python-library\\ES_logs\\ArchivingPolicies\\ES_JOBLOGS_API.json',
        archiving_policy_name='Test Archive Policy'
    )

    print(f"Import Archiving Policy Status: {status}")

    # Example usage of the ContentAdmArchivePolicy class
    # content_adm_archive_policy = ContentAdmArchivePolicy(content_obj.config)
    # status = content_adm_archive_policy.import_archiving_policy(
    #     archiving_policy_path='path/to/your/archiving_policy.json',
    #     archiving_policy_name='Your Archive Policy Name'
    # )
    # print(f"Import Archiving Policy Status: {status}")