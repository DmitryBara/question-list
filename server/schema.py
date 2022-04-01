import graphene
import graphql_jwt

import questionnaire.schema
import users.schema


class Query(
    users.schema.Query,
    questionnaire.schema.Query,
    graphene.ObjectType,
):
  pass


class Mutation(
    users.schema.Mutation,
    questionnaire.schema.Mutation,
    graphene.ObjectType,
):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.Revoke.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
