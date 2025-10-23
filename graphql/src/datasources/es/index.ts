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
    const { baseURL, authHeader } = this.parseElasticSearchURI(
      process.env.ES_URI
    );
    this.baseURL = baseURL;
    this.authHeader = authHeader;
  }

  public get acceptedElasticsearchProtocols() {
    return ['http:', 'https:'];
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

  public parseElasticSearchURI(uri: string): {
    baseURL: string;
    authHeader: string | null;
  } {
    if (!URL.canParse(uri)) {
      throw new Error('Failed to parse Elasticsearch URI');
    }
    const url = new URL(uri);
    const { username, password, protocol } = url;

    if (!this.acceptedElasticsearchProtocols.includes(protocol)) {
      throw new Error(`Unacceptable protocol ${protocol} in Elasticsearch URI`);
    }

    // Remove credentials from URL
    url.username = '';
    url.password = '';
    const baseURL = url.toString();

    if (!username) {
      return { baseURL, authHeader: null };
    }

    // Create Basic Auth header
    const credentials = `${decodeURIComponent(username)}:${decodeURIComponent(password)}`;
    const authHeader = `Basic ${Buffer.from(credentials).toString('base64')}`;

    return { baseURL, authHeader };
  }
}

export type QueryContext = {
  dataSources: {
    elasticSearchAPI: ElasticSearchAPI;
  };
};
