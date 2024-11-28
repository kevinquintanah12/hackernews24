from django.test import TestCase
from graphene_django.utils.testing import GraphQLTestCase
from mixer.backend.django import mixer
import graphene
import json
from django.contrib.auth import get_user_model

from header.schema import schema
from header.models import Header

# Create your tests here.

HEADER_QUERY = '''
query GetHeaders($search: String) {
  headers(search: $search) {
    id
    name
  }
}
'''

HEADER_BY_ID_QUERY = '''
            query GetHeaderById($id_header: Int!) {
                headerById(idHeader: $id_header) {
                    id
                    name
                }
            }
'''

USERS_QUERY = '''
 {
   users {
     id
     username
     password
   }
 }
'''


CREATE_HEADER_MUTATION = '''
 mutation createHeaderMutation($id_header: Int!, $name: String!,
    $description: String!,
    $image_url: String,
    $email: String!,
    $phone_number: String,
    $location: String!,
    $github: String!) {
     createHeader(idHeader: $id_header, name: $name,
        description: $description,
        imageUrl: $image_url,
        email: $email,
        phoneNumber: $phone_number,
        location: $location,
        github: $github) {
         idHeader
         name
     }
 }
'''

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

DELETE_HEADER_MUTATION = '''
mutation DeleteHeader($id_header: Int!) {
    deleteHeader(idHeader: $id_header) {
        idHeader
    }
}
'''

class HeaderTestCase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema
    
    def setUp(self):
        self.header1 = mixer.blend(Header)
        self.header2 = mixer.blend(Header)
   
        response_user = self.query(
            CREATE_USER_MUTATION,
            variables={'email': 'adsoft@live.com.mx', 'username': 'adsoft', 'password': 'adsoft'}
        )
        print('user mutation ')
        content_user = json.loads(response_user.content)
        print(content_user['data'])

        response_token = self.query(
            LOGIN_USER_MUTATION,
            variables={'username': 'adsoft', 'password': 'adsoft'}
        )

        content_token = json.loads(response_token.content)
        token = content_token['data']['tokenAuth']['token']
        print(token)
        self.headers = {"AUTHORIZATION": f"JWT {token}"}


    def test_headers_query(self):
        self.query(
            CREATE_HEADER_MUTATION,
            variables={
                'id_header': 0,
                "name": "John Doe",
                "description": "A passionate software engineer with a focus on backend development.",
                "image_url": "https://example.com/profile.jpg",
                "email": "johndoe@example.com",
                "phone_number": "+123456789",
                "location": "New York, USA",
                "github": "https://github.com/johndoe"},
            headers=self.headers
        )
         
        response = self.query(
            HEADER_QUERY,
             variables={
                'search': '*'},
            headers=self.headers
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        # This validates the status code and if you get errors
        self.assertResponseNoErrors(response)
        print ("query headers results ")
        print (response)
        assert len(content['data']['headers']) == 1


    def test_users_query(self):
        response = self.query(
            USERS_QUERY,
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        # This validates the status code and if you get errors
        self.assertResponseNoErrors(response)
        print ("query users results ")
        print (response)
        assert len(content['data']['users']) == 3


    def test_createHeader_mutation(self):
        response = self.query(
            CREATE_HEADER_MUTATION,
            variables={
                'id_header': 0,
                "name": "John Doe",
                "description": "A passionate software engineer with a focus on backend development.",
                "image_url": "https://example.com/profile.jpg",
                "email": "johndoe@example.com",
                "phone_number": "+123456789",
                "location": "New York, USA",
                "github": "https://github.com/johndoe"},
            headers=self.headers
        )
        content = json.loads(response.content)
        created_headers_id = content['data']['createHeader']['idHeader']
        print("Response content:", content)
        print(content['data'])
        self.assertResponseNoErrors(response)
        self.assertDictEqual({"createHeader": {"idHeader": created_headers_id, "name": "John Doe"}}, content['data']) 
        
    def test_query_invalid_id(self):
        response = self.query(
            HEADER_BY_ID_QUERY,
            variables={'id_header': 999},
            headers=self.headers
        )
        content = json.loads(response.content)
        
        self.assertResponseNoErrors(response)
        self.assertIsNone(content['data']['headerById'])
        
    def test_update_existing_headers(self):
        response_create = self.query(
            CREATE_HEADER_MUTATION,
            variables={
                'id_header': 0,
                "name": "John Doe",
                "description": "A passionate software engineer with a focus on backend development.",
                "image_url": "https://example.com/profile.jpg",
                "email": "johndoe@example.com",
                "phone_number": "+123456789",
                "location": "New York, USA",
                "github": "https://github.com/johndoe"},
            headers=self.headers
        )
        
        content_create = json.loads(response_create.content)
        created_headers_id = content_create['data']['createHeader']['idHeader']

        
        self.query(
            CREATE_HEADER_MUTATION,
            variables={
                'id_header': created_headers_id,
                "name": "Homero",
                "description": "A passionate software engineer with a focus on backend development.",
                "image_url": "https://example.com/profile.jpg",
                "email": "johndoe@example.com",
                "phone_number": "+123456789",
                "location": "New York, USA",
                "github": "https://github.com/johndoe"},
            headers=self.headers
        )

        response_query = self.query(
        HEADER_BY_ID_QUERY,
        variables={'id_header': created_headers_id},
        headers=self.headers
        )
        
        content_query = json.loads(response_query.content)
                
        
        response_query_all = self.query(
            HEADER_QUERY,
             variables={
                'search': '*'},
            headers=self.headers
        )
        
        content = json.loads(response_query_all.content)

        assert len(content['data']['headers']) == 1
        self.assertEqual(content_query['data']['headerById']['name'], "Homero")
        
    def test_not_logged_in(self):
        response = self.query(
            HEADER_BY_ID_QUERY,
            variables={"id_header": 1}
        )

        content = json.loads(response.content)

        self.assertIn('errors', content)
        self.assertIn("Not logged in", content['errors'][0]['message'])

        response = self.query(
            HEADER_QUERY,
            variables={"search": "*"}
        )

        content = json.loads(response.content)

        self.assertIn('errors', content)
        self.assertIn("Not logged in!", content['errors'][0]['message'])

    def test_filter_search(self):
        self.query(
            CREATE_HEADER_MUTATION,
            variables={
                'id_header': 1,
                'name': 'Header A',
                'description': 'This is header A.',
                'image_url': 'https://example.com/image1.jpg',
                'email': 'headera@example.com',
                'phone_number': '+123456789',
                'location': 'New York, USA',
                'github': 'https://github.com/headera'
            },
            headers=self.headers
        )

        response = self.query(
            HEADER_QUERY,
            variables={"search": "Header A"},
            headers=self.headers
        )

        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(content['data']['headers']), 1)
        self.assertEqual(content['data']['headers'][0]['name'], "Header A")

        response = self.query(
            HEADER_QUERY,
            variables={"search": "*"},
            headers=self.headers
        )

        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(content['data']['headers']), 1)

    def test_create_header_not_logged_in(self):
        response = self.query(
            CREATE_HEADER_MUTATION,
            variables={
                'id_header': 0,
                'name': 'Header C',
                'description': 'This is header C.',
                'image_url': 'https://example.com/image3.jpg',
                'email': 'headerc@example.com',
                'phone_number': '+123123123',
                'location': 'Chicago, USA',
                'github': 'https://github.com/headerc'
            }
        )
        
        content = json.loads(response.content)
        
        self.assertIn('errors', content)
        self.assertIn("Not logged in !", content['errors'][0]['message'])

    def test_delete_not_logged_in(self):
        self.query(
            CREATE_HEADER_MUTATION,
            variables={
                'id_header': 1,
                'name': 'Header D',
                'description': 'This is header D.',
                'image_url': 'https://example.com/image4.jpg',
                'email': 'headerd@example.com',
                'phone_number': '+111111111',
                'location': 'Boston, USA',
                'github': 'https://github.com/headerd'
            },
            headers=self.headers
        )

        response = self.query(
            DELETE_HEADER_MUTATION,
            variables={"id_header": 1}
        )

        content = json.loads(response.content)

        self.assertIn('errors', content)
        self.assertIn("Not logged in!", content['errors'][0]['message'])

    def test_delete_invalid_id(self):
        response = self.query(
            DELETE_HEADER_MUTATION,
            variables={"id_header": 9999},
            headers=self.headers
        )

        content = json.loads(response.content)

        self.assertIn('errors', content)
        self.assertIn("Invalid Header id!", content['errors'][0]['message'])

    def test_delete_header_successfully(self):
        response_create = self.query(
            CREATE_HEADER_MUTATION,
            variables={
                'id_header': 0,
                'name': 'Header E',
                'description': 'This is header E.',
                'image_url': 'https://example.com/image5.jpg',
                'email': 'headere@example.com',
                'phone_number': '+222222222',
                'location': 'Seattle, USA',
                'github': 'https://github.com/headere'
            },
            headers=self.headers
        )

        content_create = json.loads(response_create.content)
        created_header_id = content_create['data']['createHeader']['idHeader']

        response = self.query(
            DELETE_HEADER_MUTATION,
            variables={"id_header": created_header_id},
            headers=self.headers
        )

        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['deleteHeader']['idHeader'], created_header_id)

        header_exists = Header.objects.filter(id=created_header_id).exists()
        self.assertFalse(header_exists)

    def test_update_existing_header(self):
        response_create = self.query(
            CREATE_HEADER_MUTATION,
            variables={
                'id_header': 0,
                'name': 'Header A',
                'description': 'Updated Description',
                'image_url': 'https://example.com/updated_image.jpg',
                'email': 'updated_header@example.com',
                'phone_number': '+987654321',
                'location': 'San Francisco, USA',
                'github': 'https://github.com/updatedheader'
            },
            headers=self.headers
        )
        
        content_create = json.loads(response_create.content)
        created_header_id = content_create['data']['createHeader']['idHeader']


        response = self.query(
            CREATE_HEADER_MUTATION,
            variables={
                'id_header': created_header_id,
                'name': 'Updated Header',
                'description': 'Updated Description',
                'image_url': 'https://example.com/updated_image.jpg',
                'email': 'updated_header@example.com',
                'phone_number': '+987654321',
                'location': 'San Francisco, USA',
                'github': 'https://github.com/updatedheader'
            },
            headers=self.headers
        )
        
        content_create = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertEqual(content_create['data']['createHeader']['name'], "Updated Header")

        updated_header = Header.objects.get(id=created_header_id)
        self.assertEqual(updated_header.name, "Updated Header")

    def test_create_new_header(self):
        Header.objects.all().delete()

        response = self.query(
        CREATE_HEADER_MUTATION,
        variables={
            'id_header': 0,  
            'name': 'New Header',
            'description': 'This is a newly created header.',
            'image_url': 'https://example.com/new_image.jpg',
            'email': 'new_header@example.com',
            'phone_number': '+123456789',
            'location': 'San Francisco, USA',
            'github': 'https://github.com/newheader'
        },
        headers=self.headers
    )
       
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['createHeader']['name'], 'New Header')

        created_header = Header.objects.get(email='new_header@example.com')
        self.assertIsNotNone(created_header)
        self.assertEqual(created_header.name, "New Header")