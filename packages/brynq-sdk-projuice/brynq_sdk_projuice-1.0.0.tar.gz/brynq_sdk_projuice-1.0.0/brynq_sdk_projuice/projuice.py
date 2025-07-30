import os
import requests
from brynq_sdk_brynq import BrynQ
from requests.auth import HTTPBasicAuth
from typing import Union, List, Optional,Literal


class Projuice(BrynQ):
    """
    ProJuice SDK integrated with BrynQ for secure file uploads.
    """

    def __init__(self, system_type: Optional[Literal['source', 'target']] = None, debug=False):
        """
        Initializes the ProJuice SDK by retrieving system credentials and setting up authentication.

        :param label: The credential label(s) for ProJuice.
        :param debug: Enables debug logging if set to True.
        """
        super().__init__()
        credentials = self.interfaces.credentials.get(system="projuice", system_type=system_type)
        credentials = credentials.get('data')
        self.username = f"{credentials['identifier']}"
        self.password = f"{credentials['api_key']}"
        self.base_url =  f"https://{credentials['base_url']}/webservice_v2.php"
        self.debug = debug

    def upload_file(self, file_path: str) -> Optional[requests.Response]:
        """
        Uploads a file to the ProJuice web service.

        :param file_path: Path to the file to be uploaded.
        :return: Response object from the server if any response was received, otherwise None.
        """
        try:
            with open(file_path, "rb") as file:
                files = {"file": (os.path.basename(file_path), file, "text/csv")}

                # 20 seconds to connect, 30 minutes to wait for response
                response = requests.post(self.base_url, files=files, auth=HTTPBasicAuth(self.username, self.password), timeout=(20, 1800))

                # Do not raise_for_status — caller should decide how to handle HTTP errors
                if self.debug:
                    print(f"[DEBUG] Upload complete - status code: {response.status_code}")
                return response

        except requests.exceptions.RequestException as err:
            # Handle all network-related issues (connection, timeout, etc.)
            if self.debug:
                print(f"[DEBUG] Request exception occurred: {err}")

            # If the exception contains a response, return it
            if hasattr(err, "response") and err.response is not None:
                if self.debug:
                    print(f"[DEBUG] Returning error response - status code: {err.response.status_code}")
                return err.response

        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Unexpected error: {type(e).__name__} - {e}")

        # Returns None when no response is ever received
        return None