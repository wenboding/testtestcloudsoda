import requests
from config import CLIENT_ID, CLIENT_SECRET, TOKEN_URL

# AuthManager to handle token retrieval
class AuthManager:
    def __init__(self):
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.token_url = TOKEN_URL
        self.access_token = None
    
    def get_access_token(self):
        """Fetch the OAuth token and store it."""
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = requests.post(self.token_url, data=payload)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            print("Token fetched successfully.")
        else:
            raise Exception(f"Failed to get token. Status Code: {response.status_code}, Response: {response.text}")
    
    def get_headers(self):
        """Return the headers with the Bearer token."""
        if not self.access_token:
            self.get_access_token()  # Fetch token if not already available
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

# GraphQL API class
class GraphQLAPI:
    def __init__(self, url, auth_manager):
        self.url = url
        self.auth_manager = auth_manager

    def get_headers(self):
        """Return the headers with the Authorization token."""
        return self.auth_manager.get_headers()

    def send_query(self, query):
        """Send a GraphQL query or mutation."""
        response = requests.post(self.url, json={'query': query}, headers=self.get_headers())
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Query failed with status code {response.status_code}: {response.text}")

# REST API Managers for different entities

class UserManager:
    def __init__(self, auth_manager, user_list_url):
        self.auth_manager = auth_manager
        self.user_list_url = user_list_url

    def list_users(self):
        """List all users using the token from AuthManager."""
        headers = self.auth_manager.get_headers()
        response = requests.get(self.user_list_url, headers=headers)
        
        if response.status_code == 200:
            users = response.json()['data']
            print("Users List:")
            for user in users:
                user_id = user['id']
                user_name = user['attributes'].get('name', 'No name provided')
                user_email = user['attributes'].get('email', 'No email provided')
                print(f"ID: {user_id}, Name: {user_name}, Email: {user_email}")
        else:
            print(f"Failed to retrieve users. Status Code: {response.status_code}, Response: {response.text}")


class RESTStorageManager:
    def __init__(self, auth_manager, storage_list_url):
        self.auth_manager = auth_manager
        self.storage_list_url = storage_list_url

    def list_storages(self):
        """List all storages using the token from AuthManager."""
        headers = self.auth_manager.get_headers()
        response = requests.get(self.storage_list_url, headers=headers)
        
        if response.status_code == 200:
            storages = response.json()['data']
            print("Storages List:")
            for storage in storages:
                storage_id = storage['id']
                storage_name = storage['attributes'].get('name', 'No name provided')
                storage_type = storage['attributes'].get('type', 'No type provided')
                print(f"ID: {storage_id}, Name: {storage_name}, Type: {storage_type}")
        else:
            print(f"Failed to retrieve storages. Status Code: {response.status_code}, Response: {response.text}")

# GraphQL Managers for Storage, Accessor, and Agent creation
class StorageManager(GraphQLAPI):
    def create_storage(self):
        """Create a new storage via GraphQL mutation."""
        mutation = """
        mutation {
          storage {
            create(input: {
              objectS3Like: {
                name: "test storage",
                scopeId: "15f2da29-0625-453e-bdda-f1431037eddf",
                accountId: "7439df24-be3d-457d-a4c6-2e9b229cf9d6",
                metadata: {},
                config: {
                  bucketName: "test_bucket",
                  storageClass: STANDARD  # Remove quotes here
                }
              }
            }) {
              result {
                ... on StorageObjectS3Like {
                  name
                }
              }
              # Removed the UnprocessableFields fragment
            }
          }
        }
        """
        result = self.send_query(mutation)
        return result



class AgentManager(GraphQLAPI):
    def create_agent(self):
        """Create a new agent via GraphQL mutation."""
        mutation = """
        mutation {
          agent {
            create(
              input: {
                accountId: "7439df24-be3d-457d-a4c6-2e9b229cf9d6",
                scopeId: "15f2da29-0625-453e-bdda-f1431037eddf",
                tags: {},
                name: "my test agent"
              }
            ) {
              result {
                ... on Agent {
                  id
                  name
                }
              }
            }
          }
        }
        """
        result = self.send_query(mutation)
        return result



class AccessorManager(GraphQLAPI):
    def create_accessor(self):
        """Create a new accessor via GraphQL mutation."""
        mutation = """
        mutation {
          accessor {
            create(
              input: {
                s3Like: {
                  name: "test s3 like accessor",
                  accountId: "7439df24-be3d-457d-a4c6-2e9b229cf9d6",
                  scopeId: "15f2da29-0625-453e-bdda-f1431037eddf",
                  apiURL: "https://s3likeurl.com",
                  authorization: {
                    credentialProviderChain: {
                      useDefault: false,
                      providers: [
                        {
                          static: {
                            accessKeyId: "testKey",
                            secretAccessKey: "secret"
                          }
                        }
                      ]
                    }
                  }
                }
              }
            ) {
              result {
                ... on AccessorS3Like {
                  id
                  name
                }
              }
            }
          }
        }
        """
        result = self.send_query(mutation)
        return result




# Constants (replace these with actual values from your environment)
USER_LIST_URL = "https://walmart-usw.api.cloudsoda.io/users"
REST_STORAGE_LIST_URL = "https://walmart-usw.api.cloudsoda.io/storages"
GROUP_LIST_URL = "https://walmart-usw.api.cloudsoda.io/groups"
JOB_LIST_URL = "https://walmart-usw.api.cloudsoda.io/jobs"  # Replace with the correct endpoint for jobs
GRAPHQL_URL = "https://walmart-usw.api.cloudsoda.io/graphql"

# Initialize the AuthManager and get access token
auth_manager = AuthManager()
auth_manager.get_access_token()

# REST API usage
user_manager = UserManager(auth_manager, USER_LIST_URL)
rest_storage_manager = RESTStorageManager(auth_manager, REST_STORAGE_LIST_URL)

# List users using REST API
user_manager.list_users()

# List storages using REST API
rest_storage_manager.list_storages()

# GraphQL API usage
graphql_storage_manager = StorageManager(GRAPHQL_URL, auth_manager)
accessor_manager = AccessorManager(GRAPHQL_URL, auth_manager)
agent_manager = AgentManager(GRAPHQL_URL, auth_manager)

result = agent_manager.create_agent()
print("Agent created:", result)
if 'errors' in result:
    print("Full error:", result['errors'])


# Create storage using GraphQL
created_storage = graphql_storage_manager.create_storage()
print("Storage created:", created_storage)

# Create accessor using GraphQL
created_accessor = accessor_manager.create_accessor()
print("Accessor created:", created_accessor)

# Create agent using GraphQL
created_agent = agent_manager.create_agent()
print("Agent created:", created_agent)
