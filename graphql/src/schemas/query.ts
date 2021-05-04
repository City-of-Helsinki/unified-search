export const querySchema = `

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

  enum UnifiedSearchLanguage {
    FINNISH
    SWEDISH
    ENGLISH
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

  type Suggestion {
    label: String!
  }

  type SearchSuggestionConnection {
    suggestions: [Suggestion]!
  }

  type Query {
    unifiedSearch(
        """
        Free form query string, corresponding to user search input
        """
        q: String,

        """
        Optional, filter to match only these ontology words
        """
        ontology: String,

        """
        Optional search index.
        """
        index: String,

        """
        Optional pagination variable, match results after this cursor.
        """
        after: String

        """
        Optional pagination variable, limit the amount of results to N.
        """
        first: Int

        """
        NOTE: Unsupported

        Optional pagination variable, match results before this cursor.
        """
        before: String

        """
        NOTE: Unsupported

        Optional pagination variable, match the N last results.
        """
        last: Int

        """
        Targets the search to fields of specified language
        """
        languages: [UnifiedSearchLanguage!]! = [FINNISH, SWEDISH, ENGLISH]

      ): SearchResultConnection

    unifiedSearchCompletionSuggestions(
      """
      Free form query string, corresponding to what the user has typed so far
      """
      prefix: String

      """
      Limits the result set into the specified languages
      """
      languages: [UnifiedSearchLanguage!]! = [FINNISH, SWEDISH, ENGLISH]

      """
      Optional search index.
      """
      index: String

      """
      Optional result size.
      """
      size: Int = 5
      ): SearchSuggestionConnection
  }
`;
