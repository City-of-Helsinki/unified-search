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
    edges: [SearchResultEdge!]! @cacheControl(inheritMaxAge: true)
  }

  type SearchResultPageInfo {
    hasNextPage: Boolean!
    hasPreviousPage: Boolean!
    startCursor: String
    endCursor: String
  }

  type SearchResultEdge {
    cursor: String!
    node: SearchResultNode! @cacheControl(inheritMaxAge: true)
  }

  type SearchResultNode {
    _score: Float
    id: ID!
    venue: Venue @cacheControl(inheritMaxAge: true)
    event: Event
    searchCategories: [UnifiedSearchResultCategory!]!
  }

  type Suggestion {
    label: String!
  }

  type SearchSuggestionConnection {
    suggestions: [Suggestion]!
  }

  enum SortOrder {
    ASCENDING
    DESCENDING
  }

  input OrderByDistance {
    latitude: Float
    longitude: Float
    order: SortOrder = ASCENDING
  }

  input OrderByName {
    order: SortOrder = ASCENDING
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
        Optional, filter to match only this administrative division. DEPRECATED! use administrativeDivisionIds instead.
        """
        administrativeDivisionId: ID

        """
        Optional, filter to match only these administrative divisions
        """
        administrativeDivisionIds: [ID],

        """
        Optional, filter to match only this ontology tree id. DEPRECATED! use ontologyTreeIds instead.
        """
        ontologyTreeId: ID

        """
        Optional, filter to match only these ontology tree ids
        """
        ontologyTreeIds: [ID],

        """
        Optional, filter to match only these ontology word ids
        """
        ontologyWordIds: [ID],

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

        """
        Return only venues that are open at the given moment. In addition to ISO 8601 datetimes, accepts values
        conforming to Elastic Search date math (https://www.elastic.co/guide/en/elasticsearch/reference/7.x/common-options.html#date-math)
        like "now+3h". When there is a datetime provided without a timezone offset, "Europe/Helsinki" will be assumed
        as the time zone.
        """
        openAt: String

        """
        Order results by distance to given coordinates. Cannot be used with "orderByName".
        """
        orderByDistance: OrderByDistance

        """
        Order results by venue name in language given as the first value in "languages" argument. Cannot be used with "orderByDistance".
        """
        orderByName: OrderByName

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

    administrativeDivisions(
        """
        Return only Helsinki administrative divisions that make a sensible set to be used as an option list in an UI for example.
        """
        helsinkiCommonOnly: Boolean): [AdministrativeDivision]

    ontologyTree(
      rootId: ID
      leavesOnly: Boolean
     ): [OntologyTree]

    ontologyWords(
      ids: [ID!]
    ): [OntologyWord]
  }
`;
