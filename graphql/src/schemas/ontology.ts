import { gql } from 'graphql-tag';
export const ontologySchema = gql`
  type OntologyTree {
    id: ID
    parentId: ID
    name: LanguageString
    childIds: [ID]
    ancestorIds: [ID]
    level: Int
  }
`;
