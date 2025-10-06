# Changelog

## [3.1.0](https://github.com/City-of-Helsinki/unified-search/compare/graphql-v3.0.1...graphql-v3.1.0) (2025-10-06)


### Features

* **graphql:** Update all dependencies to latest, except @types/node→22 ([1541b77](https://github.com/City-of-Helsinki/unified-search/commit/1541b774cbf32508fa195e4f41c8d82e06d10b33))

## [3.0.1](https://github.com/City-of-Helsinki/unified-search/compare/graphql-v3.0.0...graphql-v3.0.1) (2025-09-15)


### Bug Fixes

* **graphql:** Make GraphQL release, add info to README ([5006df6](https://github.com/City-of-Helsinki/unified-search/commit/5006df68f0728f25d8360b43cb7014aab559fb11))

## [3.0.0](https://github.com/City-of-Helsinki/unified-search/compare/graphql-v2.2.0...graphql-v3.0.0) (2025-09-08)


### ⚠ BREAKING CHANGES

* **graphql:** remove needless recursion from LocationDescription type
* **graphql:** remove event importer & clean up/purge GraphQL schema

### Features

* Add pre-commit hooks for eslint, prettier, vitest and md-toc ([6d73a6b](https://github.com/City-of-Helsinki/unified-search/commit/6d73a6b0c62826ad595e852332546b3046746dc5))
* **graphql:** Add Apollo Sandbox landing page support ([5a62358](https://github.com/City-of-Helsinki/unified-search/commit/5a6235846a680b893025c56dca49cde29cb5fbb4))
* **graphql:** Add more comprehensive readiness & healthz endpoints ([9e88616](https://github.com/City-of-Helsinki/unified-search/commit/9e88616f85ddccf3256e144aaaeec0f779836f33))
* **graphql:** Add restrictive CSP using helmet ([db4b62e](https://github.com/City-of-Helsinki/unified-search/commit/db4b62eaceb2bdc4bdc882d1ccdc5b09eb96be41))
* **graphql:** Allow apollo sandbox in production ([ade9058](https://github.com/City-of-Helsinki/unified-search/commit/ade9058416741a32d2d2c04b08899d6d11df7c93))
* **graphql:** Configure permissive CORS for the open public GraphQL API ([31e3a0f](https://github.com/City-of-Helsinki/unified-search/commit/31e3a0fa4cda18ab008078e15e5ac6ad49ec6e90))
* **graphql:** Disable apollo server landing page as unnecessary ([76048ab](https://github.com/City-of-Helsinki/unified-search/commit/76048abafc17adf0e9e6fb5898ae0a7e1a3dc89b))
* **graphql:** Document administrativeDivisions query more ([0287f1b](https://github.com/City-of-Helsinki/unified-search/commit/0287f1bc6d9a296f8f7d99215d5623d47e913bc7))
* **graphql:** Make CSP config explicit & use more CSP directives ([04433a3](https://github.com/City-of-Helsinki/unified-search/commit/04433a363428b8fb03714697bfb83913df750f7e))
* **graphql:** Purge/upgrade packages, use ESM/es2022/nodenext/tsx ([609667f](https://github.com/City-of-Helsinki/unified-search/commit/609667fc255531f3be50873de408056300228795))
* **graphql:** Remove event importer & clean up/purge GraphQL schema ([fea7da9](https://github.com/City-of-Helsinki/unified-search/commit/fea7da923144aee2f12e55c1e510ad646904a0bd))
* **graphql:** Switch from jest to vitest ([26cb20a](https://github.com/City-of-Helsinki/unified-search/commit/26cb20a0bafb5a09dfc242686574d03f3697ca22))
* **graphql:** Upgrade all packages to latest minor version ([c858699](https://github.com/City-of-Helsinki/unified-search/commit/c8586994a6d3f3c73575922950b264c7954f5820))
* **graphql:** Upgrade luxon to latest major ([494bb8e](https://github.com/City-of-Helsinki/unified-search/commit/494bb8e5b26dd02ec858911ecd6d6d44c9c1368c))
* **graphql:** Upgrade sentry v6 → v9 ([e0183c4](https://github.com/City-of-Helsinki/unified-search/commit/e0183c4b771ae86d777ef1ef15bdf6127500ba26))
* **graphql:** Upgrade to eslint v9 + add minimal types to src/index.ts ([10faef6](https://github.com/City-of-Helsinki/unified-search/commit/10faef642c33d7766be69fda5754e3c725c77c12))
* **graphql:** Use better workaround for readiness build time ([9858f57](https://github.com/City-of-Helsinki/unified-search/commit/9858f57f72bd8a08e4d12bab3a0890f275c1549f))
* **graphql:** Use ubi10 node.js v22 image in Dockerfile ([96c9f97](https://github.com/City-of-Helsinki/unified-search/commit/96c9f97fad4e493e937b485fdbbaeee9b315ad03))
* **sources:** Remove unused Keyword class as unnecessary ([14d88b0](https://github.com/City-of-Helsinki/unified-search/commit/14d88b00c1791cde0e9d4b25013b496c30af2ee6))
* Switch from OpenSearch → ElasticSearch & Kibana v9.1.3 ([b082271](https://github.com/City-of-Helsinki/unified-search/commit/b082271106ec987b6b80e985d1fd7411e4c73bd7))


### Bug Fixes

* **build:** Change vocabulary & scripts from using transpile → build ([930c923](https://github.com/City-of-Helsinki/unified-search/commit/930c923fb58d6721386bec5c808dc2c38906fd26))
* **graphql:** Add LONG_TERM_PATIENTS to TargetGroup ([290dd95](https://github.com/City-of-Helsinki/unified-search/commit/290dd95d45a14ec474aca2d6ba2b8904848f37ff))
* **graphql:** EXPOSE port 4000 in Dockerfile ([63e6f58](https://github.com/City-of-Helsinki/unified-search/commit/63e6f58200c547e6358067f639db33346ad43c30))
* **graphql:** Fix cyclic import related to QueryContext type ([15aecd5](https://github.com/City-of-Helsinki/unified-search/commit/15aecd53cb8e0c86743ecc37927654fee58ccf32))
* **graphql:** Load env vars from .env file ([27199e8](https://github.com/City-of-Helsinki/unified-search/commit/27199e8fb31e3c30ab2e374ccaa9f21ea362147b))
* **graphql:** Remove needless recursion from LocationDescription type ([1afe01a](https://github.com/City-of-Helsinki/unified-search/commit/1afe01a4a3de476c0b284431f838c4008a858cf6))
* Tests, update README & docker compose & .dockerignore ([8864887](https://github.com/City-of-Helsinki/unified-search/commit/886488734b7f5f1b9f7898970688e74d7c4dcab7))

## [2.2.0](https://github.com/City-of-Helsinki/unified-search/compare/graphql-v2.1.0...graphql-v2.2.0) (2024-01-04)

### Features

- **graphql:** Add Sentry environment argument to configuration ([8266034](https://github.com/City-of-Helsinki/unified-search/commit/8266034ed5cbe0868b71101417e2ea20c94d02ba))

## [2.1.0](https://github.com/City-of-Helsinki/unified-search/compare/graphql-v2.0.0...graphql-v2.1.0) (2023-12-08)

### Features

- **graphql:** Add reservation field and filter ([2a8f662](https://github.com/City-of-Helsinki/unified-search/commit/2a8f6620f4231adda0db293a9b44bbdc9925ab9d))
- **graphql:** Exact matches should be higher in relevance ([d963f70](https://github.com/City-of-Helsinki/unified-search/commit/d963f70a0d351dade34b4e5c4cdebb72567b642c))
- **graphql:** Include ontologies in default search query ([6d7a482](https://github.com/City-of-Helsinki/unified-search/commit/6d7a4824d812e9978df50779352bdd36286cf28e))
- **search:** Use "query string" query with "bool_prefix"-type and escaping ([46c43f6](https://github.com/City-of-Helsinki/unified-search/commit/46c43f6334d1b5f54853dd6141ac912a94b21932))

### Bug Fixes

- **graphql:** Bind ElasticSearchAPI to request utility props ([672b2cb](https://github.com/City-of-Helsinki/unified-search/commit/672b2cbbf48eb701f33b8ba8d18ac865ccacd17d))
- **graphql:** Handle the special char for all results ([9943925](https://github.com/City-of-Helsinki/unified-search/commit/9943925fd1a83db1048cd4d800d5b65423c0ba8f))
- **graphql:** Linter issues ([f6ebef8](https://github.com/City-of-Helsinki/unified-search/commit/f6ebef8292438244ffff1a72150bae30586cb889))
- Transpiling did not include index.js in the dist-root ([983c60e](https://github.com/City-of-Helsinki/unified-search/commit/983c60e9ff945aad8ffc4f0a59183698244620b4))
- Typescript error ([bb0ae90](https://github.com/City-of-Helsinki/unified-search/commit/bb0ae9008f065c3e60607e63c0a50239394537b0))

## [2.0.0](https://github.com/City-of-Helsinki/unified-search/compare/graphql-v1.3.0...graphql-v2.0.0) (2023-10-25)

### ⚠ BREAKING CHANGES

- **graphql:** rename orderedByAccessibilityShortcoming field
- **graphql:** remove unsupported before & last arguments
- **graphql:** rename graphql query argument "q" to "text"
- **graphql:** remove deprecated administrativeDivisionId argument
- **graphql:** unify ontologyWordId query args to ontologyWordIdOrSets
- **graphql:** unify ontologyTreeId query args to ontologyTreeIdOrSets
- **graphql:** remove deprecated ontologyTreeId argument

### Features

- **graphql:** Rename graphql query argument "q" to "text" ([9f01fe0](https://github.com/City-of-Helsinki/unified-search/commit/9f01fe0676a5e08f692102a65dfc073a139df774))
- **graphql:** Rename orderedByAccessibilityShortcoming field ([1180717](https://github.com/City-of-Helsinki/unified-search/commit/1180717e1e57689da8b0d4be430cba3b2939bbe3))
- **graphql:** Type graphql search index with an enumeration for clarity ([273180a](https://github.com/City-of-Helsinki/unified-search/commit/273180a514c749ca348461155864f16a513b8820))
- **graphql:** Unify ontologyTreeId query args to ontologyTreeIdOrSets ([db4cf0a](https://github.com/City-of-Helsinki/unified-search/commit/db4cf0ad3610a6ebcdaf8f7d25f1bb9f551b0945))
- **graphql:** Unify ontologyWordId query args to ontologyWordIdOrSets ([dce5a10](https://github.com/City-of-Helsinki/unified-search/commit/dce5a10a414976106b2f63540c5747100196dba4))

### Bug Fixes

- **dockerfile:** Use double quotes around $YARN_VERSION ([0fe05ff](https://github.com/City-of-Helsinki/unified-search/commit/0fe05ffee3dc250993ac0c3006d019a3dc724169))
- **graphql:** Remove deprecated administrativeDivisionId argument ([91af86a](https://github.com/City-of-Helsinki/unified-search/commit/91af86a0a786d0e93c690cb47cc00f64d9751176))
- **graphql:** Remove deprecated ontologyTreeId argument ([cd30f29](https://github.com/City-of-Helsinki/unified-search/commit/cd30f2956bf647e37f17065bbcc038221dd87a5e))
- **graphql:** Remove unsupported before & last arguments ([9300a48](https://github.com/City-of-Helsinki/unified-search/commit/9300a48d5f2fbfd2f657b7ed765c8d4210067c89))

## [1.3.0](https://github.com/City-of-Helsinki/unified-search/compare/graphql-v1.2.0...graphql-v1.3.0) (2023-10-13)

### Features

- **graphql:** Add ontologyTreeIdsOrSet2 query parameter ([b17fefe](https://github.com/City-of-Helsinki/unified-search/commit/b17fefe77771215b87c03aa1954258f1f518cea2))
- **graphql:** Order by accessibility profile's shortcoming count ([e688fb2](https://github.com/City-of-Helsinki/unified-search/commit/e688fb2d0fe534c40570aad2079dac935631c13f))

### Bug Fixes

- Fix unknown and zero accessibility shortcoming counts ([3ed0a3c](https://github.com/City-of-Helsinki/unified-search/commit/3ed0a3c6bf914083e45784d8a8f15650736ff564))

## [1.2.0](https://github.com/City-of-Helsinki/unified-search/compare/graphql-v1.1.0...graphql-v1.2.0) (2023-08-23)

### Features

- Add GraphQL filters for serviceOwnerTypes, targetGroups etc ([91fc169](https://github.com/City-of-Helsinki/unified-search/commit/91fc169e3f976efd920e094085c1b00871892d75))
- Import venues' accessibility info and service provider/owner info ([78c8f28](https://github.com/City-of-Helsinki/unified-search/commit/78c8f282e078a963ff2cf297ef07d38ea6200c56))
- Import venues' accessibility sentences ([8f09613](https://github.com/City-of-Helsinki/unified-search/commit/8f09613d16f35c7eda5a6e3f9b9d4feb1338c238))
- Import venues' accessibility shortages per accessibility viewpoint ([92ed0f3](https://github.com/City-of-Helsinki/unified-search/commit/92ed0f3d9d6575c3d560067b187610b66dd78e49))
- Import venues' accessibility shortcomings from new service map API ([074b0dc](https://github.com/City-of-Helsinki/unified-search/commit/074b0dcddfe532cbff7d0f76bbec857ff6cab42c))
- Import venues' Respa API resources, e.g. reservability ([94bc57b](https://github.com/City-of-Helsinki/unified-search/commit/94bc57bf644f4cdc665337a354ef9b0d116c814b))
- Import venues' target groups from service description registry ([5ee8925](https://github.com/City-of-Helsinki/unified-search/commit/5ee8925469770f1f80a5ef59e51a665601be8cdc))

### Bug Fixes

- Fix importing of Respa resources & showing new data in GraphQL ([64c412f](https://github.com/City-of-Helsinki/unified-search/commit/64c412f157c557adda497e18cf9d39314afc0ec2))
- **graphql:** Fix resolving of UnifiedSearchVenue type after rename ([37160d4](https://github.com/City-of-Helsinki/unified-search/commit/37160d4d26f053bae8144ecdeaa0877c6695810b))
- **graphql:** Rename Venue to UnifiedSearchVenue & sync schema comments ([0a7b49d](https://github.com/City-of-Helsinki/unified-search/commit/0a7b49d5a271f6c4b0b276f6aa4d851c77dd2bcb))
- Release-please US-106 ([9e74726](https://github.com/City-of-Helsinki/unified-search/commit/9e74726018e7b6264163aaf17e7fcc8740ade996))
