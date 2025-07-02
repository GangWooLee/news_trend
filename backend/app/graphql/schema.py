from ariadne import QueryType, make_executable_schema, gql
from backend.app.graphql.resolvers import resolvers_map
from backend.app.graphql.context import graphql_context

# GraphQL SDL
type_defs = gql("""
  type Query {
    searchNews(query: String!, display: Int, start: Int, sort: String): [NewsItem!]!
    getNews(skip: Int, limit: Int): [News!]!
    predict(newsId: Int, text: String): PredictResponse!
  }

  type NewsItem {
    title: String
    link: String
    originallink: String
    description: String
    pubDate: String
  }

  type News {
    id: Int!
    title: String!
    link: String!
    originallink: String
    description: String
    pubDate: String!
    createdAt: String!
  }

  type Entity {
    entity: String!
    label: String!
  }

  type Prediction {
    asset: String!
    direction: String!
    confidence: Float!
    reasoning: String!
  }

  type PredictResponse {
    entities: [Entity!]!
    predictions: [Prediction!]!
  }
"""
)

# QueryType 객체 생성
query = QueryType()

# Resolver 등록
for field_name, resolver_func in resolvers_map.items():
    query.set_field(field_name, resolver_func)

# Executable Schema
graphql_schema = make_executable_schema(type_defs, query)