from datetime import datetime
from graphene_django.utils.testing import GraphQLTestCase
import json
from django.contrib.auth import get_user_model
from education.models import Education
from education.schema import schema

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

QUERY_ALL_DEGREES = '''
query {
    degrees {
        id
        degree
        university
        startDate
        endDate
    }
}
'''

QUERY_DEGREE_BY_ID = '''
query($id: Int!) {
    degreeById(id: $id) {
        id
        degree
        university
        startDate
        endDate
    }
}
'''

CREATE_EDUCATION_MUTATION = '''
mutation createEducationMutation($degree: String!, $university: String!, $startDate: Date!, $endDate: Date!) {
    createEducation(
        degree: $degree,
        university: $university,
        startDate: $startDate,
        endDate: $endDate
    ) {
        id
        degree
        university
    }
}
'''

DELETE_EDUCATION_MUTATION = '''
mutation deleteEducationMutation($id: Int!) {
    deleteEducation(id: $id) {
        id
    }
}
'''

class EducationTests(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema

    def setUp(self):
        # Crear usuario para las pruebas
        response_user = self.query(
            CREATE_USER_MUTATION,
            variables={"email": "user@example.com", "username": "testuser", "password": "testpassword"}
        )
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

        # Crear una instancia de Educación para las pruebas
        self.education = Education.objects.create(
            degree="Computer Science",
            university="Test University",
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2024, 1, 1),
            posted_by=get_user_model().objects.get(username="testuser")
        )

    def test_query_all_degrees(self):
        response = self.query(QUERY_ALL_DEGREES, headers=self.headers)
        self.assertResponseNoErrors(response)
        content = json.loads(response.content)
        self.assertEqual(len(content["data"]["degrees"]), 1)

    def test_query_degree_by_id(self):
        response = self.query(
            QUERY_DEGREE_BY_ID,
            variables={"id": self.education.id},
            headers=self.headers
        )
        self.assertResponseNoErrors(response)
        content = json.loads(response.content)
        self.assertEqual(content["data"]["degreeById"]["degree"], "Computer Science")

    def test_mutation_create_education(self):
        response = self.query(
            CREATE_EDUCATION_MUTATION,
            variables={
                "degree": "Data Science",
                "university": "Another University",
                "startDate": "2022-01-01",
                "endDate": "2025-01-01"
            },
            headers=self.headers
        )
        self.assertResponseNoErrors(response)
        content = json.loads(response.content)
        self.assertEqual(content["data"]["createEducation"]["degree"], "Data Science")

    def test_mutation_delete_education(self):
        response = self.query(
            DELETE_EDUCATION_MUTATION,
            variables={"id": self.education.id},
            headers=self.headers
        )
        self.assertResponseNoErrors(response)
        content = json.loads(response.content)
        self.assertEqual(str(content["data"]["deleteEducation"]["id"]), str(self.education.id))
        self.assertFalse(Education.objects.filter(id=self.education.id).exists())

    # Nueva prueba para manejar error en creación de educación sin datos obligatorios
    def test_mutation_create_education_missing_data(self):
        response = self.query(
            CREATE_EDUCATION_MUTATION,
            variables={
                "degree": "",
                "university": "",
                "startDate": "",
                "endDate": ""
            },
            headers=self.headers
        )
        self.assertResponseHasErrors(response)
        content = json.loads(response.content)
        self.assertIn("errors", content)

    # Nueva prueba para manejar token incorrecto
    def test_invalid_token(self):
        invalid_headers = {"AUTHORIZATION": "JWT invalid_token"}
        response = self.query(QUERY_ALL_DEGREES, headers=invalid_headers)
        self.assertResponseHasErrors(response)

    # Nueva prueba para verificar si la respuesta maneja datos vacíos correctamente
    def test_query_empty_degrees(self):
        Education.objects.all().delete()
        response = self.query(QUERY_ALL_DEGREES, headers=self.headers)
        self.assertResponseNoErrors(response)
        content = json.loads(response.content)
        self.assertEqual(content["data"]["degrees"], [])

