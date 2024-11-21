from datetime import datetime
from graphene_django.utils.testing import GraphQLTestCase
import json
from django.contrib.auth import get_user_model
from interest.models import Interest
from interest.schema import schema

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

LOGIN_USER_MUTATION = '''
mutation TokenAuthMutation($username: String!, $password: String!) {
    tokenAuth(username: $username, password: $password) {
        token
    }
}
'''

QUERY_ALL_INTERESTS = '''
query {
    interests {
        id
        name
        description
    }
}
'''

QUERY_INTEREST_BY_ID = '''
query($idInterest: Int!) {
    interestById(idInterest: $idInterest) {
        id
        name
        description
    }
}
'''

CREATE_INTEREST_MUTATION = '''
mutation createInterestMutation($name: String!, $description: String!) {
    createInterest(
        name: $name,
        description: $description
    ) {
        idInterest
        name
        description
    }
}
'''

DELETE_INTEREST_MUTATION = '''
mutation deleteInterestMutation($idInterest: Int!) {
    deleteInterest(idInterest: $idInterest) {
        idInterest
    }
}
'''

class InterestTests(GraphQLTestCase):
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

        self.interest = Interest.objects.create(
            name="Data Science",
            description="A field that deals with data processing and analysis.",
            posted_by=get_user_model().objects.get(username="testuser")
        )

    def test_query_all_interests(self):
        response = self.query(QUERY_ALL_INTERESTS, headers=self.headers)
        print("Query all interests response status code:", response.status_code)
        print("Query all interests response content:", response.content)

        try:
            content = json.loads(response.content)
        except json.JSONDecodeError as e:
            raise Exception(f"JSON decode error in query all interests: {response.content}") from e

        if response.status_code != 200 or "errors" in content:
            raise Exception(f"Error querying all interests: {content}")

        self.assertResponseNoErrors(response)
        self.assertEqual(len(content["data"]["interests"]), 1)

    def test_query_interest_by_id(self):
        response = self.query(
            QUERY_INTEREST_BY_ID,
            variables={"idInterest": self.interest.id},
            headers=self.headers
        )
        print("Query interest by ID response status code:", response.status_code)
        print("Query interest by ID response content:", response.content)

        try:
            content = json.loads(response.content)
        except json.JSONDecodeError as e:
            raise Exception(f"JSON decode error in query interest by ID: {response.content}") from e

        if response.status_code != 200 or "errors" in content:
            raise Exception(f"Error querying interest by ID: {content}")

        self.assertResponseNoErrors(response)
        self.assertEqual(content["data"]["interestById"]["name"], "Data Science")

    def test_mutation_create_interest(self):
        response = self.query(
            CREATE_INTEREST_MUTATION,
            variables={
                "name": "AI Research",
                "description": "Researching new methods in artificial intelligence."
            },
            headers=self.headers
        )
        print("Create interest response status code:", response.status_code)
        print("Create interest response content:", response.content)

        try:
            content = json.loads(response.content)
        except json.JSONDecodeError as e:
            raise Exception(f"JSON decode error in create interest mutation: {response.content}") from e

        if response.status_code != 200 or "errors" in content:
            raise Exception(f"Error in create interest mutation: {content}")

        self.assertResponseNoErrors(response)
        self.assertEqual(content["data"]["createInterest"]["name"], "AI Research")

    def test_mutation_delete_interest(self):
        response = self.query(
            DELETE_INTEREST_MUTATION,
            variables={"idInterest": self.interest.id},
            headers=self.headers
        )
        print("Delete interest response status code:", response.status_code)
        print("Delete interest response content:", response.content)

        try:
            content = json.loads(response.content)
        except json.JSONDecodeError as e:
            raise Exception(f"JSON decode error in delete interest mutation: {response.content}") from e

        if response.status_code != 200 or "errors" in content:
            raise Exception(f"Error in delete interest mutation: {content}")

        self.assertResponseNoErrors(response)
        self.assertEqual(str(content["data"]["deleteInterest"]["idInterest"]), str(self.interest.id))
        self.assertFalse(Interest.objects.filter(id=self.interest.id).exists())
