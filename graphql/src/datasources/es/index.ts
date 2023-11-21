import {
  getAdministrativeDivisions,
  getOntologyTree,
  getOntologyWords,
  getQueryResults,
  getSuggestions,
} from './api';
import type { getQueryResultsProps, getSuggestionProps } from './api';
import { ELASTIC_SEARCH_URI, ES_DEFAULT_PAGE_SIZE } from './constants';
import type {
  AdministrativeDivisionParams,
  OntologyTreeParams,
  OntologyWordParams,
} from './types';

import { RESTDataSource } from 'apollo-datasource-rest';

class ElasticSearchAPI extends RESTDataSource {
  constructor() {
    super();
    this.baseURL = ELASTIC_SEARCH_URI;
  }

  async getQueryResults(props: getQueryResultsProps) {
    const request = this.post.bind(this);
    return await getQueryResults(request, props);
  }

  async getSuggestions(props: getSuggestionProps) {
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
