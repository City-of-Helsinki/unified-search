import { Client } from '@elastic/elasticsearch';

import {
  getAdministrativeDivisions,
  getOntologyTree,
  getOntologyWords,
  getQueryResults,
  getSuggestions,
} from './api/index.js';
import type { getQueryResultsProps } from './api/index.js';
import type {
  AdministrativeDivisionParams,
  OntologyTreeParams,
  OntologyWordParams,
  SuggestionsParams,
} from './types.js';

export class ElasticSearchAPI {
  public readonly esClient: Client | null = null;

  constructor() {
    const nodeURLs = (process.env.ES_URI ?? '')
      .split(',')
      .map((node) => new URL(node.trim()));

    for (const url of nodeURLs) {
      if (url.username || url.password) {
        throw new Error(
          'Elasticsearch URI must not contain credentials; ' +
            'use ES_USERNAME and ES_PASSWORD environment variables instead!'
        );
      }
    }

    // Set Basic Auth, if at least username is provided
    const username = process.env.ES_USERNAME ?? '';
    const password = process.env.ES_PASSWORD ?? '';
    const auth = username ? { username, password } : undefined;

    const nodes = nodeURLs.map((url) => url.toString());

    // Initialize Elasticsearch client
    this.esClient = new Client({ nodes, auth });
  }

  async getQueryResults(props: getQueryResultsProps) {
    return await getQueryResults(this.esClient, props);
  }

  async getSuggestions(props: SuggestionsParams) {
    return await getSuggestions(this.esClient, props);
  }

  async getAdministrativeDivisions(props: AdministrativeDivisionParams) {
    return await getAdministrativeDivisions(this.esClient, props);
  }

  async getOntologyTree(props: OntologyTreeParams) {
    return await getOntologyTree(this.esClient, props);
  }

  async getOntologyWords(props: OntologyWordParams) {
    return await getOntologyWords(this.esClient, props);
  }
}

export type QueryContext = {
  dataSources: {
    elasticSearchAPI: ElasticSearchAPI;
  };
};
