import { RESTDataSource } from '@apollo/datasource-rest';

import {
  getAdministrativeDivisions,
  getOntologyTree,
  getOntologyWords,
  getQueryResults,
  getSuggestions,
} from './api/index.js';
import type { getQueryResultsProps, GetSuggestionProps } from './api/index.js';
import { ELASTIC_SEARCH_URI, ES_DEFAULT_PAGE_SIZE } from './constants.js';
import type {
  AdministrativeDivisionParams,
  OntologyTreeParams,
  OntologyWordParams,
} from './types.js';

class ElasticSearchAPI extends RESTDataSource {
  constructor() {
    super();
    this.baseURL = ELASTIC_SEARCH_URI;
  }

  async getQueryResults(props: getQueryResultsProps) {
    const request = this.post.bind(this);
    return await getQueryResults(request, props);
  }

  async getSuggestions(props: GetSuggestionProps) {
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

export { ElasticSearchAPI, ES_DEFAULT_PAGE_SIZE };
