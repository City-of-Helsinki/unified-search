# Changelog

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
