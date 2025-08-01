# SpectaQL Configuration

This is a directory for SpectaQL configuration files,
which are used to generate documentation for the GraphQL API.

Commands for generating the documentation can be found in
[package.json](../package.json) as:

- generate-local-dev-graphql-docs
- generate-test-graphql-docs
- generate-stage-graphql-docs
- generate-prod-graphql-docs

depending on the environment you want to use as source for the documentation.

Normally `generate-test-graphql-docs` is fine for generating the documentation.

## Contents

- [config.yaml](./config.yaml)
  - The main configuration file for SpectaQL.

- [description-into-generated-docs.md](./description-into-generated-docs.md)
  - A markdown file that contains the main description to be included
    in the generated documentation.
