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
    return await getQueryResults(this.post, props);
  }

  async getSuggestions(props: getSuggestionProps) {
    return await getSuggestions(this.post, props);
  }

  async getAdministrativeDivisions(props: AdministrativeDivisionParams) {
    return await getAdministrativeDivisions(this.get, props);
  }

  async getOntologyTree(props: OntologyTreeParams) {
    return await getOntologyTree(this.post, props);
  }

  async getOntologyWords(props: OntologyWordParams) {
    return await getOntologyWords(this.post, props);
  }
}

export { ElasticSearchAPI, ES_DEFAULT_PAGE_SIZE };
