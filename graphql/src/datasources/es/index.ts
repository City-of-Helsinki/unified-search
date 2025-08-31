import { RESTDataSource } from '@apollo/datasource-rest';

import {
  getAdministrativeDivisions,
  getOntologyTree,
  getOntologyWords,
  getQueryResults,
  getSuggestions,
} from './api/index.js';
import type { getQueryResultsProps } from './api/index.js';
import { ELASTIC_SEARCH_URI } from './constants.js';
import type {
  AdministrativeDivisionParams,
  OntologyTreeParams,
  OntologyWordParams,
  SuggestionsParams,
} from './types.js';

export class ElasticSearchAPI extends RESTDataSource {
  constructor() {
    super();
    this.baseURL = ELASTIC_SEARCH_URI;
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
