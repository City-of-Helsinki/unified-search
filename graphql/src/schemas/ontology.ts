export const ontologySchema = `
  type OntologyTree {
    id: ID
    parentId: ID
    name: LanguageString
    childIds: [ID]
    ancestorIds: [ID]
    level: Int
  }
`;
