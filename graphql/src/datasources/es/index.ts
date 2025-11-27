import { AugmentedRequest, RESTDataSource } from '@apollo/datasource-rest';

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

export class ElasticSearchAPI extends RESTDataSource {
  public readonly authHeader: string | null = null;

  constructor() {
    super();

    // Set base URL
    const url = new URL(process.env.ES_URI);
    if (url.username || url.password) {
      throw new Error(
        'Elasticsearch URI must not contain credentials; ' +
          'use ES_USERNAME and ES_PASSWORD environment variables instead!'
      );
    }
    this.baseURL = url.toString();

    // Set Basic Auth, if at least username is provided
    const username = process.env.ES_USERNAME ?? '';
    const password = process.env.ES_PASSWORD ?? '';

    if (username) {
      const credentials = `${username}:${password}`;
      this.authHeader = `Basic ${Buffer.from(credentials).toString('base64')}`;
    }
  }

  /**
   * Attach authorization header, if present, to all requests
   * @see https://www.apollographql.com/docs/apollo-server/data/fetching-rest
   */
  override willSendRequest(_path: string, request: AugmentedRequest): void {
    if (this.authHeader) {
      request.headers['authorization'] = this.authHeader;
    }
  }

  async getQueryResults(props: getQueryResultsProps) {
    const request = this.post.bind(this);
    return await getQueryResults(request, props);
  }

  async getSuggestions(props: SuggestionsParams) {
    const request = this.post.bind(this);
    return await getSuggestions(request, props);
  }

  async getAdministrativeDivisions(props: AdministrativeDivisionParams) {
    const request = this.get.bind(this);
    return await getAdministrativeDivisions(request, props);
  }

  async getOntologyTree(props: OntologyTreeParams) {
    const request = this.post.bind(this);
    return await getOntologyTree(request, props);
  }

  async getOntologyWords(props: OntologyWordParams) {
    const request = this.post.bind(this);
    return await getOntologyWords(request, props);
  }
}

export type QueryContext = {
  dataSources: {
    elasticSearchAPI: ElasticSearchAPI;
  };
};
