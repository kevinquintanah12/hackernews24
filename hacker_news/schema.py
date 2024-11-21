import graphene
import graphql_jwt
import links.schema
import users.schema
import education.schema
import workexperience.schema
import languages.schema  # Importamos el esquema de languages
import header.schema     # Importamos el esquema de header
import interest.schema   # Importamos el esquema de interest
import skills.schema     # Importamos el esquema de skills

class Query(
    education.schema.Query, 
    users.schema.Query, 
    links.schema.Query, 
    workexperience.schema.Query,  # Añadimos el Query de workexperience
    languages.schema.Query,       # Añadimos el Query de languages
    header.schema.Query,          # Añadimos el Query de header
    interest.schema.Query,        # Añadimos el Query de interest
    skills.schema.Query,          # Añadimos el Query de skills
    graphene.ObjectType
):
    pass

class Mutation(
    education.schema.Mutation, 
    users.schema.Mutation, 
    links.schema.Mutation, 
    workexperience.schema.Mutation,  # Añadimos el Mutation de workexperience
    languages.schema.Mutation,       # Añadimos el Mutation de languages
    header.schema.Mutation,          # Añadimos el Mutation de header
    interest.schema.Mutation,        # Añadimos el Mutation de interest
    skills.schema.Mutation,          # Añadimos el Mutation de skills
    graphene.ObjectType
):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
