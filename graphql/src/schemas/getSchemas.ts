import { elasticSearchSchema } from './es.js';
import { geoSchema } from './geojson.js';
import { locationSchema } from './location.js';
import { ontologySchema } from './ontology.js';
import { palvelukarttaSchema } from './palvelukartta.js';
import { querySchema } from './query.js';
import { sharedSchema } from './shared.js';

/**
 * Get all GraphQL schemas for the GraphQL server.
 */
export function getSchemas() {
  return [
    querySchema,
    elasticSearchSchema,
    palvelukarttaSchema,
    locationSchema,
    sharedSchema,
    geoSchema,
    ontologySchema,
  ];
}
