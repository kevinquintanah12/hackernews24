from datetime import datetime
from graphene_django.utils.testing import GraphQLTestCase
import json
from django.contrib.auth import get_user_model
from workexperience.models import WorkExperience
from workexperience.schema import schema

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

QUERY_ALL_WORK_EXPERIENCES = '''
query {
    workExperience {
        id
        jobTitle
        company
        startDate
        endDate
        description
        accomplishments
    }
}
'''

QUERY_WORK_EXPERIENCE_BY_ID = '''
query($idWorkExperience: Int!) {
    workExperienceById(idWorkExperience: $idWorkExperience) {
        id
        jobTitle
        company
        startDate
        endDate
        description
        accomplishments
    }
}
'''

CREATE_WORK_EXPERIENCE_MUTATION = '''
mutation createWorkExperienceMutation($jobTitle: String!, $company: String!, $startDate: Date!, $endDate: Date!, $description: String!, $accomplishments: [String!]) {
    createWorkExperience(
        jobTitle: $jobTitle,
        company: $company,
        startDate: $startDate,
        endDate: $endDate,
        description: $description,
        accomplishments: $accomplishments
    ) {
        idWorkExperience
        jobTitle
        company
    }
}
'''

DELETE_WORK_EXPERIENCE_MUTATION = '''
mutation deleteWorkExperienceMutation($idWorkExperience: Int!) {
    deleteWorkExperience(idWorkExperience: $idWorkExperience) {
        idWorkExperience
    }
}
'''

class WorkExperienceTests(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema

    def setUp(self):
        # Crear un usuario
        response_user = self.query(
            CREATE_USER_MUTATION,
            variables={"email": "user@example.com", "username": "testuser", "password": "testpassword"}
        )

        if response_user.status_code != 200:
            raise Exception(f"Error en la mutación de creación de usuario: {response_user.content}")

        content_user = json.loads(response_user.content)
        if "errors" in content_user:
            raise Exception(f"Error GraphQL en la mutación de creación de usuario: {content_user['errors']}")

        # Login del usuario
        response_token = self.query(
            LOGIN_USER_MUTATION,
            variables={"username": "testuser", "password": "testpassword"}
        )

        if response_token.status_code != 200:
            raise Exception(f"Error en la mutación de login: {response_token.content}")

        content_token = json.loads(response_token.content)
        if "errors" in content_token:
            raise Exception(f"Error GraphQL en la mutación de login: {content_token['errors']}")

        # Obtener el token de autenticación
        self.token = content_token["data"]["tokenAuth"]["token"]
        self.headers = {"AUTHORIZATION": f"JWT {self.token}"}

        # Crear una instancia de WorkExperience
        self.work_experience = WorkExperience.objects.create(
            job_title="Software Engineer",
            company="Test Company",
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2022, 1, 1),
            description="Worked on backend systems",
            accomplishments= ["Improved system performance", "Reduced downtime"],
            


            user=get_user_model().objects.get(username="testuser")
        )

    def test_query_all_work_experiences(self):
        response = self.query(QUERY_ALL_WORK_EXPERIENCES, headers=self.headers)
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(content["data"]["workExperience"]), 1)

    def test_query_work_experience_by_id(self):
        response = self.query(
            QUERY_WORK_EXPERIENCE_BY_ID,
            variables={"idWorkExperience": self.work_experience.id},
            headers=self.headers
        )
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertEqual(content["data"]["workExperienceById"]["jobTitle"], "Software Engineer")

    def test_mutation_create_work_experience(self):
        response = self.query(
            CREATE_WORK_EXPERIENCE_MUTATION,
            variables={
                "jobTitle": "Data Analyst",
                "company": "Another Company",
                "startDate": "2022-01-01",
                "endDate": "2024-01-01",
                "description": "Analyzed company data",
                "accomplishments": ["Improved system performance", "Reduced downtime"],


            },
            headers=self.headers
        )
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertEqual(content["data"]["createWorkExperience"]["jobTitle"], "Data Analyst")

    def test_mutation_delete_work_experience(self):
        response = self.query(
            DELETE_WORK_EXPERIENCE_MUTATION,
            variables={"idWorkExperience": self.work_experience.id},
            headers=self.headers
        )
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertEqual(str(content["data"]["deleteWorkExperience"]["idWorkExperience"]), str(self.work_experience.id))
        self.assertFalse(WorkExperience.objects.filter(id=self.work_experience.id).exists())
