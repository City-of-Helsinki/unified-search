# Changelog

## [2.2.0](https://github.com/City-of-Helsinki/unified-search/compare/sources-v2.1.0...sources-v2.2.0) (2025-10-06)


### Features

* **sources:** Update dependencies to latest ([7cbd773](https://github.com/City-of-Helsinki/unified-search/commit/7cbd7735dbf5d559d7d1700e1df7a3f5ca29c674))

## [2.1.0](https://github.com/City-of-Helsinki/unified-search/compare/sources-v2.0.0...sources-v2.1.0) (2025-09-12)


### Features

* **sources:** Add dynamic runtime compatibility for Elasticsearch 8 & 9 ([23bceba](https://github.com/City-of-Helsinki/unified-search/commit/23bceba80fae180b5ac610131556e0d0ba7ce37c))

## [2.0.0](https://github.com/City-of-Helsinki/unified-search/compare/sources-v1.4.0...sources-v2.0.0) (2025-09-08)


### ⚠ BREAKING CHANGES

* **graphql:** remove event importer & clean up/purge GraphQL schema

### Features

* Add pre-commit hooks for eslint, prettier, vitest and md-toc ([6d73a6b](https://github.com/City-of-Helsinki/unified-search/commit/6d73a6b0c62826ad595e852332546b3046746dc5))
* Combine /test/ completely into sources app for maintainability ([aaac514](https://github.com/City-of-Helsinki/unified-search/commit/aaac5142188e8bf8bc1acc7899e95450bdf50f3d))
* **graphql:** Document administrativeDivisions query more ([0287f1b](https://github.com/City-of-Helsinki/unified-search/commit/0287f1bc6d9a296f8f7d99215d5623d47e913bc7))
* **graphql:** Remove event importer & clean up/purge GraphQL schema ([fea7da9](https://github.com/City-of-Helsinki/unified-search/commit/fea7da923144aee2f12e55c1e510ad646904a0bd))
* **sources:** Add commitHash to readiness endpoint's output ([0cbd6b0](https://github.com/City-of-Helsinki/unified-search/commit/0cbd6b06e64ec01e19ab1761881c3d8d324c6b14))
* **sources:** Add CSP & tests for it ([d6274ce](https://github.com/City-of-Helsinki/unified-search/commit/d6274ce50e3b8669ba8af4169feb4ed15915fd5e))
* **sources:** Add openapi.yaml documentation of available endpoints ([dfb8fe7](https://github.com/City-of-Helsinki/unified-search/commit/dfb8fe77d17519bc65dc96af9e8863e3bb9317c5))
* **sources:** Add permissive CORS, b/c only readiness/healthz endpoints ([15429e6](https://github.com/City-of-Helsinki/unified-search/commit/15429e6f5f4180106c9023be36d0c0ccab984766))
* **sources:** Add readiness/healthz endpoints ([1ad6906](https://github.com/City-of-Helsinki/unified-search/commit/1ad690667811a15f39a212c0b9842a0140ee8950))
* **sources:** Docker: ignore more files, copy using chmod 755 ([c28dffd](https://github.com/City-of-Helsinki/unified-search/commit/c28dffd0ec16c33866e04fd5ad61217aab9b2acc))
* **sources:** Make location importer more robust by retrying requests ([7b0a528](https://github.com/City-of-Helsinki/unified-search/commit/7b0a528fc556fa642ae01aeffac04126d4d3b400))
* **sources:** Remove asgi.py as unnecessary ([7e21be0](https://github.com/City-of-Helsinki/unified-search/commit/7e21be0f72c4e40f31c970152563dacc9429d425))
* **sources:** Remove django admin login page as unneeded ([1931b32](https://github.com/City-of-Helsinki/unified-search/commit/1931b321eccc10a8ea38f9d14a6ae6b6c6ed5a56))
* **sources:** Remove support for ingest_data data deletion as unneeded ([5b0073b](https://github.com/City-of-Helsinki/unified-search/commit/5b0073b86d17ba69fc878a8d8f4c5e7aeebab112))
* **sources:** Remove unused Keyword class as unnecessary ([14d88b0](https://github.com/City-of-Helsinki/unified-search/commit/14d88b00c1791cde0e9d4b25013b496c30af2ee6))
* **sources:** Upgrade to Python 3.12 & all dependencies, use ruff ([9cb7f7d](https://github.com/City-of-Helsinki/unified-search/commit/9cb7f7dcecbb3c23fd7789cb720e9baf1ac4700d))
* **sources:** Use more directives in CSP, use upgrade-insecure-requests ([f08de7e](https://github.com/City-of-Helsinki/unified-search/commit/f08de7ed269894cd05da41005af9aa406eb36ef8))
* **sources:** Use ubi9 python 3.9 GDAL image in Dockerfile ([7bbba03](https://github.com/City-of-Helsinki/unified-search/commit/7bbba03dd1d12b5a237a7bc04f438de55fffd81c))
* Switch from OpenSearch → ElasticSearch & Kibana v9.1.3 ([b082271](https://github.com/City-of-Helsinki/unified-search/commit/b082271106ec987b6b80e985d1fd7411e4c73bd7))


### Bug Fixes

* **graphql:** Add LONG_TERM_PATIENTS to TargetGroup ([290dd95](https://github.com/City-of-Helsinki/unified-search/commit/290dd95d45a14ec474aca2d6ba2b8904848f37ff))
* **graphql:** Load env vars from .env file ([27199e8](https://github.com/City-of-Helsinki/unified-search/commit/27199e8fb31e3c30ab2e374ccaa9f21ea362147b))
* **sources:** Load env vars from .env using python-dotenv ([76fa327](https://github.com/City-of-Helsinki/unified-search/commit/76fa327439d5a91cc0b2130416e9981e6077c1c2))
* **sources:** Make request_json function retry request twice ([228ec5d](https://github.com/City-of-Helsinki/unified-search/commit/228ec5d2d866af591f328b2fbcc98bed32c64146))
* **sources:** Remove django-munigeo monkeypatching as unnecessary ([2ab2bf0](https://github.com/City-of-Helsinki/unified-search/commit/2ab2bf0aea49a5715f0454153c35b613382661b7))
* **sources:** Remove incorrect deprecation ([9b766e3](https://github.com/City-of-Helsinki/unified-search/commit/9b766e3bdb4483637abc48c8bf82606561cec1b4))
* **sources:** Remove upgrade-insecure-requests CSP directive as unneeded ([84e7c88](https://github.com/City-of-Helsinki/unified-search/commit/84e7c880c55f50dfe4dbfdac845813af22cd570c))
* Tests, update README & docker compose & .dockerignore ([8864887](https://github.com/City-of-Helsinki/unified-search/commit/886488734b7f5f1b9f7898970688e74d7c4dcab7))


### Documentation

* Add development environments to READMEs ([211108f](https://github.com/City-of-Helsinki/unified-search/commit/211108fe316fa05956bd2b534df2a3ba4204ecec))
* Add endpoint documentation links ([53d5915](https://github.com/City-of-Helsinki/unified-search/commit/53d5915f81d35504671520501408302ee82b63e5))
* Document data importers & their data import flow ([e004a99](https://github.com/City-of-Helsinki/unified-search/commit/e004a99b573c36565499bf2b775e740afa88c097))
* Update README files ([ab09e74](https://github.com/City-of-Helsinki/unified-search/commit/ab09e7475c51aef5bf4de2759a665a052ea9bdc0))

## [1.4.0](https://github.com/City-of-Helsinki/unified-search/compare/sources-v1.3.1...sources-v1.4.0) (2023-12-08)


### Features

* **sources:** Add connections endpoint and use it with reservation info ([4fb1429](https://github.com/City-of-Helsinki/unified-search/commit/4fb1429d85f3b505367702368a3d878c963d3dbd))
* **sources:** Add LocationImporterAPI to clean and reusability ([752e8f2](https://github.com/City-of-Helsinki/unified-search/commit/752e8f210f4af94a508826a3c451386fa1a412a0))
* **sources:** Add reservation data class to location importer ([a327af0](https://github.com/City-of-Helsinki/unified-search/commit/a327af0295c28c636823ca5c2b8380e932c021a0))


### Bug Fixes

* Imports ([a327af0](https://github.com/City-of-Helsinki/unified-search/commit/a327af0295c28c636823ca5c2b8380e932c021a0))
* Linting issues ([66213a5](https://github.com/City-of-Helsinki/unified-search/commit/66213a52c41d981ea69b56c231d53b013121389e))
* Location importer Address import ([b255398](https://github.com/City-of-Helsinki/unified-search/commit/b255398e07c978251e243f6a96ca489e4fbdc5b2))
* **sources:** Linter issues ([5f90778](https://github.com/City-of-Helsinki/unified-search/commit/5f90778ef209334502761cfa92a794d53cb1ebcd))
* **sources:** Ontology object should be created only once ([9275c07](https://github.com/City-of-Helsinki/unified-search/commit/9275c07ebcefe3d192939a6646af1168453f333b))

## [1.3.1](https://github.com/City-of-Helsinki/unified-search/compare/sources-v1.3.0...sources-v1.3.1) (2023-10-25)


### Bug Fixes

* **importers:** Remove duplicated ontology word importer ([1c41741](https://github.com/City-of-Helsinki/unified-search/commit/1c41741445fdc6ca50d6a70c189dfe15f59174b5))

## [1.3.0](https://github.com/City-of-Helsinki/unified-search/compare/sources-v1.2.0...sources-v1.3.0) (2023-10-13)


### Features

* **graphql:** Order by accessibility profile's shortcoming count ([e688fb2](https://github.com/City-of-Helsinki/unified-search/commit/e688fb2d0fe534c40570aad2079dac935631c13f))


### Bug Fixes

* Fix unknown and zero accessibility shortcoming counts ([3ed0a3c](https://github.com/City-of-Helsinki/unified-search/commit/3ed0a3c6bf914083e45784d8a8f15650736ff564))
* **ingest_data:** Fix data importing from kartta.hsy.fi by updating cert ([cc6e1e6](https://github.com/City-of-Helsinki/unified-search/commit/cc6e1e65a8f94ed836a6ddecd61a55955a63084e))

## [1.2.0](https://github.com/City-of-Helsinki/unified-search/compare/sources-v1.1.0...sources-v1.2.0) (2023-08-23)


### Features

* Add --use-fallback-languages support to all importers, default=off ([ed141aa](https://github.com/City-of-Helsinki/unified-search/commit/ed141aace01b43e81db499164095396154fd1d44))
* Add fi&gt;en>sv fallback language support to LanguageStringConverter ([b7cbd29](https://github.com/City-of-Helsinki/unified-search/commit/b7cbd2987c1ffd28d35553f2193297e63b9ae354))
* Add GraphQL filters for serviceOwnerTypes, targetGroups etc ([91fc169](https://github.com/City-of-Helsinki/unified-search/commit/91fc169e3f976efd920e094085c1b00871892d75))
* Import venues' accessibility info and service provider/owner info ([78c8f28](https://github.com/City-of-Helsinki/unified-search/commit/78c8f282e078a963ff2cf297ef07d38ea6200c56))
* Import venues' accessibility sentences ([8f09613](https://github.com/City-of-Helsinki/unified-search/commit/8f09613d16f35c7eda5a6e3f9b9d4feb1338c238))
* Import venues' accessibility shortages per accessibility viewpoint ([92ed0f3](https://github.com/City-of-Helsinki/unified-search/commit/92ed0f3d9d6575c3d560067b187610b66dd78e49))
* Import venues' accessibility shortcomings from new service map API ([074b0dc](https://github.com/City-of-Helsinki/unified-search/commit/074b0dcddfe532cbff7d0f76bbec857ff6cab42c))
* Import venues' Respa API resources, e.g. reservability ([94bc57b](https://github.com/City-of-Helsinki/unified-search/commit/94bc57bf644f4cdc665337a354ef9b0d116c814b))
* Import venues' target groups from service description registry ([5ee8925](https://github.com/City-of-Helsinki/unified-search/commit/5ee8925469770f1f80a5ef59e51a665601be8cdc))
* **ingest_data:** Use fallback languages (Order: fi, en, sv) by default ([9edea3b](https://github.com/City-of-Helsinki/unified-search/commit/9edea3bf74d622b1d839f7b5cdb045ace6359fbd))


### Bug Fixes

* Change fallback language order from fi/en/sv to en/fi/sv ([a730d8c](https://github.com/City-of-Helsinki/unified-search/commit/a730d8c260d17247a2802904dfdefae7ffd6b2d6))
* Fix importing of Respa resources & showing new data in GraphQL ([64c412f](https://github.com/City-of-Helsinki/unified-search/commit/64c412f157c557adda497e18cf9d39314afc0ec2))
* Netcat build failure ([d8f2e92](https://github.com/City-of-Helsinki/unified-search/commit/d8f2e92f08e30ad04c1f8938480bd7d06d160fe0))
* Release-please US-106 ([9e74726](https://github.com/City-of-Helsinki/unified-search/commit/9e74726018e7b6264163aaf17e7fcc8740ade996))
* Update django-munigeo, monkey patch broken location import URL ([40c2857](https://github.com/City-of-Helsinki/unified-search/commit/40c2857aabda204647c4fb2a24fdf225652cbb26))
