from datetime import datetime
from graphene_django.utils.testing import GraphQLTestCase
import json
from django.contrib.auth import get_user_model
from header.models import Header
from header.schema import schema

# Mutación para crear un usuario
CREATE_USER_MUTATION = '''
mutation createUserMutation($email: String!, $password: String!, $username: String!) {
    createUser(email: $email, password: $password, username: $username) {
        user {
            username
            password
        }
    }
}
'''

# Mutación de login
LOGIN_USER_MUTATION = '''
mutation TokenAuthMutation($username: String!, $password: String!) {
    tokenAuth(username: $username, password: $password) {
        token
    }
}
'''

# Consultas de headers
QUERY_ALL_HEADERS = '''
query {
    header {
        id
        name
        phone
        email
        location
        photo
    }
}
'''



# Mutación de crear header
CREATE_HEADER_MUTATION = '''
mutation createHeaderMutation($name: String!, $phone: String!, $email: String!, $location: String!, $photo: String!) {
    createHeader(
        name: $name,
        phone: $phone,
        email: $email,
        location: $location,
        photo: $photo
    ) {
        id
        name
        phone
        email
        location
        photo
    }
}
'''

# Mutación de actualización de header
UPDATE_HEADER_MUTATION = '''
mutation updateHeaderMutation($id: Int!, $name: String!, $phone: String!, $email: String!, $location: String!, $photo: String!) {
    updateHeader(
        idHeader: $id,
        name: $name,
        phone: $phone,
        email: $email,
        location: $location,
        photo: $photo
    ) {
        idHeader
        name
        phone
        email
        location
        photo
    }
}
'''

class HeaderTests(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema

    def setUp(self):

        response_user = self.query(
            CREATE_USER_MUTATION,
            variables={"email": "user@example.com", "username": "testuser", "password": "testpassword"}
        )
        print("Create user response status code:", response_user.status_code)
        print("Create user response content:", response_user.content)
        if response_user.status_code != 200:
            raise Exception(f"Error in create user mutation: {response_user.content}")

        try:
            content_user = json.loads(response_user.content)
        except json.JSONDecodeError as e:
            raise Exception(f"JSON decode error in create user mutation: {response_user.content}") from e

        if "errors" in content_user:
            raise Exception(f"GraphQL error in create user mutation: {content_user['errors']}")

        response_token = self.query(
            LOGIN_USER_MUTATION,
            variables={"username": "testuser", "password": "testpassword"}
        )
        print("Login response status code:", response_token.status_code)
        print("Login response content:", response_token.content)

        if response_token.status_code != 200:
            raise Exception(f"Error in login mutation: {response_token.content}")

        try:
            content_token = json.loads(response_token.content)
        except json.JSONDecodeError as e:
            raise Exception(f"JSON decode error in login mutation: {response_token.content}") from e

        if "errors" in content_token:
            raise Exception(f"GraphQL error in login mutation: {content_token['errors']}")

        self.token = content_token["data"]["tokenAuth"]["token"]
        self.headers = {"AUTHORIZATION": f"JWT {self.token}"}

        # Ensure the user doesn't already have a header before creating one
        if not Header.objects.filter(user=get_user_model().objects.get(username="testuser")).exists():
            self.header = Header.objects.create(
                name="John Doe",
                phone="1234567890",
                email="john.doe@example.com",
                location="New York",
                photo="https://example.com/photo.jpg",  # Asegúrate de que sea una URL válida si el campo es obligatorio
                user=get_user_model().objects.get(username="testuser")
            )

    def test_query_all_headers(self):

        header = Header.objects.order_by('?').first()

        response = self.query(QUERY_ALL_HEADERS, headers=self.headers)
        print("Query all headers response status code:", response.status_code)
        print("Query all headers response content:", response.content)

        try:
            content = json.loads(response.content)
        except json.JSONDecodeError as e:
            raise Exception(f"JSON decode error in query all headers: {response.content}") from e

        if response.status_code != 200 or "errors" in content:
            raise Exception(f"Error querying all headers: {content}")

        
    
    def test_mutation_create_header(self):
        # Ensure no header exists before creating one
        if not Header.objects.filter(user=get_user_model().objects.get(username="testuser")).exists():
            response = self.query(
                CREATE_HEADER_MUTATION,
                variables={
                    "name": "Jane Doe",
                    "phone": "0987654321",
                    "email": "jane.doe@example.com",
                    "location": "California",
                    "photo": "https://example.com/photo2.jpg"
                },
                headers=self.headers
            )
            print("Create header response status code:", response.status_code)
            print("Create header response content:", response.content)

            try:
                content = json.loads(response.content)
            except json.JSONDecodeError as e:
                raise Exception(f"JSON decode error in create header mutation: {response.content}") from e

            if response.status_code != 200 or "errors" in content:
                raise Exception(f"Error in create header mutation: {content}")

            self.assertResponseNoErrors(response)
            self.assertEqual(content["data"]["createHeader"]["name"], "Jane Doe")

    def test_mutation_update_header(self):
        response = self.query(
            UPDATE_HEADER_MUTATION,
            variables={
                "id": self.header.id,
                "name": "John Updated",
                "phone": "9876543210",
                "email": "john.updated@example.com",
                "location": "Los Angeles",
                "photo": "https://example.com/photo_updated.jpg"
            },
            headers=self.headers
        )
        print("Update header response status code:", response.status_code)
        print("Update header response content:", response.content)

        try:
            content = json.loads(response.content)
        except json.JSONDecodeError as e:
            raise Exception(f"JSON decode error in update header mutation: {response.content}") from e

        if response.status_code != 200 or "errors" in content:
            raise Exception(f"Error in update header mutation: {content}")

        self.assertResponseNoErrors(response)
        self.assertEqual(content["data"]["updateHeader"]["name"], "John Updated")
        self.assertEqual(content["data"]["updateHeader"]["phone"], "9876543210")
