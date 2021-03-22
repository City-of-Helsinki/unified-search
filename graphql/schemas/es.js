
const { GraphQLScalarType } = require('graphql');


exports.elasticSearchSchema = `

""" Elasticsearch results """

union Data = PalvelukarttaUnit | LinkedeventsPlace


type ElasticSearchResult {
    took: Int,
    timed_out: Boolean,
    _shards: Shards
    hits: Hits
  }

type Shards {
total: Int, 
successful: Int,
skipped: Int, 
failed: Int
}

type Hits {
max_score: Float,
total: HitTotal,
hits: [SingleHit],
}

type HitTotal {
value: Int,
relation: String
}

type SingleHit {
_index: String,
_type: String,
_score: Float
_id: String,
_source: Data
}

`;
