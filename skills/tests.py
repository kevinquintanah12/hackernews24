from datetime import datetime
from graphene_django.utils.testing import GraphQLTestCase
import json
from django.contrib.auth import get_user_model
from skills.models import Skill
from skills.schema import schema

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

QUERY_ALL_SKILLS = '''
query {
    skills {
        id
        name
        level
        description
    }
}
'''

QUERY_SKILL_BY_ID = '''
query($idSkill: Int!) {
    skillById(idSkill: $idSkill) {
        id
        name
        level
        description
    }
}
'''

CREATE_SKILL_MUTATION = '''
mutation createSkillMutation($name: String!, $level: String!, $description: String!) {
    createSkill(name: $name, level: $level, description: $description) {
        idSkill
        name
        level
        description
    }
}
'''

DELETE_SKILL_MUTATION = '''
mutation deleteSkillMutation($idSkill: Int!) {
    deleteSkill(idSkill: $idSkill) {
        idSkill
    }
}
'''

class SkillTests(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema

    def setUp(self):
        response_user = self.query(
            CREATE_USER_MUTATION,
            variables={"email": "user@example.com", "username": "testuser", "password": "testpassword"}
        )
        if response_user.status_code != 200:
            raise Exception(f"Error in create user mutation: {response_user.content}")

        content_user = json.loads(response_user.content)
        if "errors" in content_user:
            raise Exception(f"GraphQL error in create user mutation: {content_user['errors']}")

        response_token = self.query(
            LOGIN_USER_MUTATION,
            variables={"username": "testuser", "password": "testpassword"}
        )
        if response_token.status_code != 200:
            raise Exception(f"Error in login mutation: {response_token.content}")

        content_token = json.loads(response_token.content)
        if "errors" in content_token:
            raise Exception(f"GraphQL error in login mutation: {content_token['errors']}")

        self.token = content_token["data"]["tokenAuth"]["token"]
        self.headers = {"AUTHORIZATION": f"JWT {self.token}"}

        self.skill = Skill.objects.create(
            name="Python",
            level="Advanced",
            description="Proficient in Python programming.",
            user=get_user_model().objects.get(username="testuser")
        )

    def test_query_all_skills(self):
        response = self.query(QUERY_ALL_SKILLS, headers=self.headers)
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual(len(content["data"]["skills"]), 1)

    def test_query_skill_by_id(self):
        response = self.query(
            QUERY_SKILL_BY_ID,
            variables={"idSkill": self.skill.id},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual(content["data"]["skillById"]["name"], "Python")

    def test_mutation_create_skill(self):
        response = self.query(
            CREATE_SKILL_MUTATION,
            variables={
                "name": "Django",
                "level": "Intermediate",
                "description": "Experience with Django web framework."
            },
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual(content["data"]["createSkill"]["name"], "Django")

    def test_mutation_delete_skill(self):
        response = self.query(
            DELETE_SKILL_MUTATION,
            variables={"idSkill": self.skill.id},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual(str(content["data"]["deleteSkill"]["idSkill"]), str(self.skill.id))
        self.assertFalse(Skill.objects.filter(id=self.skill.id).exists())
