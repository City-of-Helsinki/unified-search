# Changelog

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
