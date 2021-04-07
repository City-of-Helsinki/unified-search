const { GraphQLScalarType } = require('graphql');

exports.querySchema = `

""" Query """

  directive @origin(service: String, type: String, attr: String) repeatable on FIELD_DEFINITION | OBJECT

  enum UnifiedSearchResultCategory {
    POINT_OF_INTEREST
    EVENT
    RESERVABLE
    ENROLLABLE
    ARTWORK
    ARTICLE
    SERVICE
  }

  type SearchResultConnection {
    """ Elasticsearch raw results """
    es_results: [ElasticSearchResult]

    count: Int
    max_score: Float
    pageInfo: SearchResultPageInfo
    edges: [SearchResultEdge!]!
  }

  type SearchResultPageInfo {
    hasNextPage: Boolean!
    hasPreviousPage: Boolean!
    startCursor: String
    endCursor: String
  }

  type SearchResultEdge {
    cursor: String!
    node: SearchResultNode!
  }

  type SearchResultNode {
    _score: Float
    id: ID!
    venue: Venue
    searchCategories: [UnifiedSearchResultCategory!]!
  }

  type Query {
    unifiedSearch(
        """
        Free form query string, corresponding to user search input
        """
        q: String,

        """
        Optional search index.
        """
        index: String,

      ): SearchResultConnection
  }
`;
