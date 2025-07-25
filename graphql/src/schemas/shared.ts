import { gql } from 'graphql-tag';
export const sharedSchema = gql`
  scalar DateTime
  type NodeMeta @cacheControl(inheritMaxAge: true) {
    id: ID!
    createdAt: DateTime
    updatedAt: DateTime
  }

  type LanguageString @cacheControl(inheritMaxAge: true) {
    fi: String
    sv: String
    en: String
  }

  enum CacheControlScope {
    PUBLIC
    PRIVATE
  }

  directive @cacheControl(
    maxAge: Int
    scope: CacheControlScope
    inheritMaxAge: Boolean
  ) on FIELD_DEFINITION | OBJECT | INTERFACE | UNION
`;
