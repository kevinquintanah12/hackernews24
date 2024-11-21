from django.test import TestCase
from graphene_django.utils.testing import GraphQLTestCase
from mixer.backend.django import mixer
import graphene
import json
from django.contrib.auth import get_user_model

from links.schema import schema
from links.models import Link, Vote

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

# Define las consultas y mutaciones GraphQL
LINKS_QUERY = '''
 {
   links {
     id
     url
     description
   }
 }
'''

CREATE_LINK_MUTATION = '''
 mutation createLinkMutation($url: String!, $description: String!) {
     createLink(url: $url, description: $description) {
         id
         url
         description
     }
 }
'''

CREATE_VOTE_MUTATION = '''
 mutation createVoteMutation($linkId: Int!) {
     createVote(linkId: $linkId) {
         user {
             username
         }
         link {
             id
             url
         }
     }
 }
'''

# Clase de prueba para GraphQL
class LinkTestCase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema
    
    def setUp(self):
        # Crea un usuario y un enlace para las pruebas
        self.link1 = mixer.blend(Link)
        self.link2 = mixer.blend(Link)
   
        response_user = self.query(
            CREATE_USER_MUTATION,
            variables={'email': 'adsoft@live.com.mx', 'username': 'adsoft', 'password': 'adsoft'}
        )
        content_user = json.loads(response_user.content)

        response_token = self.query(
            LOGIN_USER_MUTATION,
            variables={'username': 'adsoft', 'password': 'adsoft'}
        )
        content_token = json.loads(response_token.content)
        token = content_token['data']['tokenAuth']['token']
        self.headers = {"AUTHORIZATION": f"JWT {token}"}

    def test_createLink_mutation(self):
        # Prueba para crear un enlace
        response = self.query(
            CREATE_LINK_MUTATION,
            variables={'url': 'https://google.com', 'description': 'google'},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertIsNotNone(content['data']['createLink']['id'])  # Verificar que el ID se devuelve
        self.assertEqual(content['data']['createLink']['description'], 'google')

    def test_createVote_mutation(self):
        # Crear un enlace para votar
        response_create_link = self.query(
            CREATE_LINK_MUTATION,
            variables={'url': 'https://example.com', 'description': 'Example description'},
            headers=self.headers
        )
        content_create_link = json.loads(response_create_link.content)
        
        # Asegurarse de que el ID sea un entero
        link_id = int(content_create_link['data']['createLink']['id'])
        
        # Realizar la mutación para votar por el enlace creado
        response_create_vote = self.query(
            CREATE_VOTE_MUTATION,
            variables={'linkId': link_id},
            headers=self.headers
        )
        content_create_vote = json.loads(response_create_vote.content)
        
        # Verificar que el voto fue creado correctamente
        self.assertResponseNoErrors(response_create_vote)
        
        # Comparar los IDs como enteros para evitar la discrepancia de tipos
        self.assertEqual(int(content_create_vote['data']['createVote']['link']['id']), link_id)
        self.assertEqual(content_create_vote['data']['createVote']['link']['url'], 'https://example.com')
        self.assertEqual(content_create_vote['data']['createVote']['user']['username'], 'adsoft')
