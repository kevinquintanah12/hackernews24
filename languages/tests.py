from datetime import datetime
from graphene_django.utils.testing import GraphQLTestCase
import json
from django.contrib.auth import get_user_model
from languages.models import Language
from languages.schema import schema

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

QUERY_ALL_LANGUAGES = '''
query {
    languages {
        id
        name
        proficiency
        startDate
        endDate
    }
}
'''

QUERY_LANGUAGE_BY_ID = '''
query($idLanguage: Int!) {
    languageById(idLanguage: $idLanguage) {
        id
        name
        proficiency
        startDate
        endDate
    }
}
'''

CREATE_LANGUAGE_MUTATION = '''
mutation createLanguageMutation($name: String!, $proficiency: String!, $startDate: Date!, $endDate: Date!) {
    createLanguage(
        name: $name,
        proficiency: $proficiency,
        startDate: $startDate,
        endDate: $endDate
    ) {
        idLanguage
        name
        proficiency
    }
}
'''

DELETE_LANGUAGE_MUTATION = '''
mutation deleteLanguageMutation($idLanguage: Int!) {
    deleteLanguage(idLanguage: $idLanguage) {
        idLanguage
    }
}
'''

class LanguageTests(GraphQLTestCase):
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

        self.language = Language.objects.create(
            name="Spanish",
            proficiency="Advanced",
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2024, 1, 1),
            posted_by=get_user_model().objects.get(username="testuser")
        )

    def test_query_all_languages(self):
        response = self.query(QUERY_ALL_LANGUAGES, headers=self.headers)
        print("Query all languages response status code:", response.status_code)
        print("Query all languages response content:", response.content)

        try:
            content = json.loads(response.content)
        except json.JSONDecodeError as e:
            raise Exception(f"JSON decode error in query all languages: {response.content}") from e

        if response.status_code != 200 or "errors" in content:
            raise Exception(f"Error querying all languages: {content}")

        self.assertResponseNoErrors(response)
        self.assertEqual(len(content["data"]["languages"]), 1)

    def test_query_language_by_id(self):
        response = self.query(
            QUERY_LANGUAGE_BY_ID,
            variables={"idLanguage": self.language.id},
            headers=self.headers
        )
        print("Query language by ID response status code:", response.status_code)
        print("Query language by ID response content:", response.content)

        try:
            content = json.loads(response.content)
        except json.JSONDecodeError as e:
            raise Exception(f"JSON decode error in query language by ID: {response.content}") from e

        if response.status_code != 200 or "errors" in content:
            raise Exception(f"Error querying language by ID: {content}")

        self.assertResponseNoErrors(response)
        self.assertEqual(content["data"]["languageById"]["name"], "Spanish")

    def test_mutation_create_language(self):
        response = self.query(
            CREATE_LANGUAGE_MUTATION,
            variables={
                "name": "English",
                "proficiency": "Intermediate",
                "startDate": "2022-01-01",
                "endDate": "2025-01-01"
            },
            headers=self.headers
        )
        print("Create language response status code:", response.status_code)
        print("Create language response content:", response.content)

        try:
            content = json.loads(response.content)
        except json.JSONDecodeError as e:
            raise Exception(f"JSON decode error in create language mutation: {response.content}") from e

        if response.status_code != 200 or "errors" in content:
            raise Exception(f"Error in create language mutation: {content}")

        self.assertResponseNoErrors(response)
        self.assertEqual(content["data"]["createLanguage"]["name"], "English")

    def test_mutation_delete_language(self):
        response = self.query(
            DELETE_LANGUAGE_MUTATION,
            variables={"idLanguage": self.language.id},
            headers=self.headers
        )
        print("Delete language response status code:", response.status_code)
        print("Delete language response content:", response.content)

        try:
            content = json.loads(response.content)
        except json.JSONDecodeError as e:
            raise Exception(f"JSON decode error in delete language mutation: {response.content}") from e

        if response.status_code != 200 or "errors" in content:
            raise Exception(f"Error in delete language mutation: {content}")

        self.assertResponseNoErrors(response)
        self.assertEqual(str(content["data"]["deleteLanguage"]["idLanguage"]), str(self.language.id))
        self.assertFalse(Language.objects.filter(id=self.language.id).exists())
