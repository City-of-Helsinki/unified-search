# Data importers

The data importers used for importing data into the unified search's
OpenSearch/Elasticsearch index are located under this directory.

## Architecture

Azure DevOps [cron jobs](https://dev.azure.com/City-of-Helsinki/kuva-unified-search/_git/kuva-unified-search-pipelines?path=%2Fpipeline-templates%2Fdeploy-pipeline-unified-search-sources.yml)
call [ingest_data](./management/commands/ingest_data.py) Django management command with parameters:

| ingest_data parameter     | Used importer                                                       |
|---------------------------|---------------------------------------------------------------------|
| `administrative_division` | [AdministrativeDivisionImporter](#administrative-division-importer) |
| `location`                | [LocationImporter](#location-importer)                              |
| `ontology_tree`           | [OntologyTreeImporter](#ontology-tree-importer)                     |
| `ontology_word`           | [OntologyWordImporter](#ontology-word-importer)                     |

### Administrative division importer

[AdministrativeDivisionImporter](./importers/administrative_division.py) imports Helsinki/Finland
administrative divisions using [django-munigeo](https://github.com/City-of-Helsinki/django-munigeo) commands:
- `geo_import finland --municipalities` → [geo_import](https://github.com/City-of-Helsinki/django-munigeo/blob/release-0.3.12/munigeo/management/commands/geo_import.py) → [finland](https://github.com/City-of-Helsinki/django-munigeo/blob/release-0.3.12/munigeo/importer/finland.py) importer 
- `geo_import helsinki --divisions` → [geo_import](https://github.com/City-of-Helsinki/django-munigeo/blob/release-0.3.12/munigeo/management/commands/geo_import.py) → [helsinki](https://github.com/City-of-Helsinki/django-munigeo/blob/release-0.3.12/munigeo/importer/helsinki.py) importer 

#### Imported administrative divisions

- Municipalities (=kunnat)
  - Neighborhoods (=kaupunginosat)
  - Sub-districts (=osa-alueet)
  - Districts (=peruspiirit)

#### Data sources

Based on django-munigeo [v0.3.12](https://github.com/City-of-Helsinki/django-munigeo/releases/tag/release-0.3.12) (2025-02-27):

The django-munigeo's `finland` importer uses the following source:
1. National Land Survey of Finland's division of Finland into administrative areas (vector), 1:1M scale, year 2016
   - Cached at and [used](https://github.com/City-of-Helsinki/django-munigeo/blob/release-0.3.12/munigeo/importer/finland.py#L35) from [makasiini.hel.ninja](https://makasiini.hel.ninja/TietoaKuntajaosta_2016_1000k.zip)
   - Cached file [taken](https://github.com/City-of-Helsinki/django-munigeo/blob/release-0.3.8/munigeo/importer/finland.py#L29) from [kartat.kapsi.fi](http://kartat.kapsi.fi/files/kuntajako/kuntajako_1000k/etrs89/gml/TietoaKuntajaosta_2016_1000k.zip)
     - Versions for each year between 2016–2025 [are available](https://kartat.kapsi.fi/files/kuntajako/kuntajako_1000k/etrs89/gml/) 
   - Originally from National Land Survey of Finland (Maanmittauslaitos), see docs:
     - [Division into administrative areas (vector)](https://www.maanmittauslaitos.fi/en/maps-and-spatial-data/datasets-and-interfaces/product-descriptions/division-administrative-areas-vector)
     - [Specification for the used year 2016 version (In Finnish)](https://xml.nls.fi/Kuntajako/Asiakasdokumentaatio/Tietotuoteselosteet/tietotuoteseloste_kuntajako_2016_1000k.pdf) 

The django-munigeo's `helsinki` importer uses the following sources:
1. [City of Helsinki's Open Data WFS-service](https://kartta.hel.fi/avoindata/dokumentit/HKI_wfs-avoin-data-kuvaus.pdf) at [kartta.hel.fi/ws/geoserver/avoindata/wfs](https://kartta.hel.fi/ws/geoserver/avoindata/wfs?request=GetCapabilities)
   - "Helsingin kaupunkimittauspalveluiden ylläpitämä WFS-rajapintapalvelu" in Finnish 
   - [Used WFS layers](https://github.com/City-of-Helsinki/django-munigeo/blob/release-0.3.12/munigeo/data/fi/helsinki/config.yml):
     - Major districts / `avoindata:Piirijako_suurpiiri` (=Suurpiirit)
     - Districts / `avoindata:Piirijako_peruspiiri` (=Peruspiirit)
     - Sub-districts / `avoindata:Piirijako_osaalue` (=Osa-alueet)
     - Small districts / `avoindata:Piirijako_pienalue` (=Pienalueet)
     - Neighborhoods /  `avoindata:Kaupunginosajako` (=Kaupunginosat)
     - Voting districts / `avoindata:Halke_aanestysalue` (=Äänestysalueet)
     - Postcodes / `avoindata:Postinumeroalue` (=Postinumeroalueet)
2. [Helsinki Region Environmental Services Authority (HSY)](https://www.hsy.fi/en/)'s WFS-service at [kartta.hsy.fi/geoserver/wfs](https://kartta.hsy.fi/geoserver/wfs?request=GetCapabilities)
   - [Used WFS layers](https://github.com/City-of-Helsinki/django-munigeo/blob/release-0.3.12/munigeo/data/fi/helsinki/config.yml):
     - Statistical districts / `taustakartat_ja_aluejaot:seutukartta_pien_2021` only for municipalities:
       - Helsinki / [091](https://stat.fi/fi/luokitukset/kunta/kunta_1_20250101/code/091)
       - Vantaa / [092](https://stat.fi/fi/luokitukset/kunta/kunta_1_20250101/code/092)
       - Espoo / [049](https://stat.fi/fi/luokitukset/kunta/kunta_1_20250101/code/049)
       - Kauniainen / [235](https://stat.fi/fi/luokitukset/kunta/kunta_1_20250101/code/235)

### Location importer

Terms `unit`, `location` and `venue` are used interchangeably, and they mean the same thing.

[LocationImporter](./importers/location/importers.py) imports data from the following sources:
1. [REST API for City of Helsinki Service Map](https://www.hel.fi/palvelukarttaws/restpages/ver4_en.html) (Closed source application by CGI) 
   - [All accessibility sentences](https://www.hel.fi/palvelukarttaws/restpages/ver4_en.html#_find_all_accessibility_sentences) from [accessibility_sentence](https://www.hel.fi/palvelukarttaws/rest/v4/accessibility_sentence/) endpoint
   - [All accessibility shortages](https://www.hel.fi/palvelukarttaws/restpages/ver4_en.html#_find_all_accessibility_shortages) from [accessibilitity_shortage](https://www.hel.fi/palvelukarttaws/rest/v4/accessibility_shortage/) endpoint
   - [All accessibility viewpoints](https://www.hel.fi/palvelukarttaws/restpages/ver4_en.html#_find_all_accessibility_viewpoints) from [accessibility_viewpoint](https://www.hel.fi/palvelukarttaws/rest/v4/accessibility_viewpoint/) endpoint
   - [All connections](https://www.hel.fi/palvelukarttaws/restpages/ver4_en.html#_find_all_connections) from [connection](https://www.hel.fi/palvelukarttaws/rest/v4/connection/) endpoint
   - [All units](https://www.hel.fi/palvelukarttaws/restpages/ver4_en.html#_filter_units) from [unit](https://www.hel.fi/palvelukarttaws/rest/v4/unit/?newfeatures=yes) endpoint
2. [TPR Service Description Register REST API](https://www.hel.fi/palvelukarttaws/restpages/palvelurekisteri_en.html) (Closed source application by CGI)
   - All Helsinki's public service descriptions from [description](https://www.hel.fi/palvelukarttaws/rest/vpalvelurekisteri/description/?alldata=yes) endpoint
3. [Service Map Backend](https://github.com/City-of-Helsinki/smbackend) (Open source)
   - All accessibility shortcoming counts from [unit](https://api.hel.fi/servicemap/v2/unit/?format=json&only=accessibility_shortcoming_count&page_size=1000) endpoint (with pagination)
4. Same data sources as [administrative division importer](#administrative-division-importer)
   - These are used to add administrative division information to the location data
5. [Helsinki Opening hours API / Hauki](https://github.com/City-of-Helsinki/hauki) (Open source)
   - Opening hours for venues from [opening_hours](https://hauki.api.hel.fi/v1/opening_hours/) endpoint

### Ontology tree importer

[OntologyTreeImporter](./importers/ontology_tree.py) imports data from the following source:
- [REST API for City of Helsinki Service Map](https://www.hel.fi/palvelukarttaws/restpages/ver4_en.html) (Closed source application by CGI):
  - All ontology trees from the [ontologytree](https://www.hel.fi/palvelukarttaws/restpages/ver4.html#_find_all_ontology_trees) endpoint

### Ontology word importer

[OntologyWordImporter](./importers/ontology_word.py) imports data from the following source:
- [REST API for City of Helsinki Service Map](https://www.hel.fi/palvelukarttaws/restpages/ver4_en.html) (Closed source application by CGI):
  - All ontology words from the [ontologyword](https://www.hel.fi/palvelukarttaws/restpages/ver4.html#_find_all_ontology_words) endpoint

### Data import flow diagram

The `ingest_data` command reads data from external data sources (REST API endpoints, WFS services, zip files etc)
and writes it to the Elasticsearch indexes.

When reading this diagram, please note that:
- The data flow is initiated by Azure DevOps cron jobs daily, which call the `ingest_data` command
- Data flow has been simplified to go in only one direction, abstracting away any loopbacks used for data processing
  - The `mapped to` arrows indicate that data processing is done in the importer code

```mermaid
---
title: Data Import Flow
---
flowchart LR
  subgraph DevOps["Azure DevOps Cron Jobs"]
    AdminDivCronJob["Admin Div"]
    LocationCronJob["Location"]
    OntologyTreeAndWordCronJob["Ontology Tree & Word"]
  end
  subgraph Sources["Backend management command"]
    IngestDataAdminDiv["ingest_data \n administrative_division"]
    IngestDataLocation["ingest_data \n location"]
    IngestDataOntologyWord["ingest_data \n ontology_word"]
    IngestDataOntologyTree["ingest_data \n ontology_tree"]
  end
  subgraph Makasiini["makasiini.hel.ninja (zip)"]
    TietoaKuntajaostaZip["Administrative Divisions 2016"]
  end
  subgraph HelsinkiWFS["kartta.hel.fi (WFS)"]
    AdminDivWFSLayers["Administrative Divisions"]
  end
  subgraph HsyWFS["kartta.hsy.fi (WFS)"]
    StatDistrictsWFSLayers["Statistical Districts"]
  end
  subgraph PalvelukarttaWS["www.hel.fi/palvelukarttaws"]
    OntologyWordEndpoint["All ontology words"]
    OntologyTreeEndpoint["All ontology trees"]
    AccessibilitySentenceEndpoint["All accessibility sentences"]
    AccessibilityShortageEndpoint["All accessibility shortages"]
    AccessibilityViewpointEndpoint["All accessibility viewpoints"]
    ConnectionEndpoint["All connections"]
    UnitEndpoint["All units"]
    DescriptionEndpoint["All Helsinki's public \n service descriptions"]
  end
  subgraph ServiceMap["api.hel.fi/servicemap"]
    AccessibilityShortcomingCountEndpoint["All accessibility \n shortcoming counts"]
  end
  subgraph Hauki["hauki.api.hel.fi"]
    OpeningHoursEndpoint["Venue opening hours"]
  end
  subgraph Elasticsearch["Elasticsearch Indexes"]
    AdminDivIndex["administrative_division"]
    LocationIndex["location"]
    OntologyTreeIndex["ontology_tree"]
    OntologyWordIndex["ontology_word"]
  end
  
  %% Group parts together in order to control layout
  %% Workaround for hard-to-control layout i.e. https://github.com/mermaid-js/mermaid/issues/815
  subgraph DataSourcesGroup["Data Sources"]
    Makasiini
    HelsinkiWFS
    HsyWFS
    ServiceMap
    PalvelukarttaWS
    Hauki
  end
  
  MunigeoResults(" ")
  OntologyTreeResults(" ")
  OntologyWordResults(" ")
  
  AdminDivCronJob -- calls --> IngestDataAdminDiv
  LocationCronJob -- calls -->IngestDataLocation
  OntologyTreeAndWordCronJob -- calls --> IngestDataOntologyTree
  OntologyTreeAndWordCronJob -- calls --> IngestDataOntologyWord
        
  IngestDataAdminDiv -- reads --> TietoaKuntajaostaZip
  IngestDataAdminDiv -- reads --> AdminDivWFSLayers
  IngestDataAdminDiv -- reads --> StatDistrictsWFSLayers
        
  IngestDataLocation -- reads --> TietoaKuntajaostaZip
  IngestDataLocation -- reads --> AdminDivWFSLayers
  IngestDataLocation -- reads --> StatDistrictsWFSLayers
  IngestDataLocation -- reads --> OntologyTreeEndpoint
  IngestDataLocation -- reads --> OntologyWordEndpoint
        
  AdminDivWFSLayers -- mapped to --> MunigeoResults
  
  StatDistrictsWFSLayers -- mapped to --> MunigeoResults
  
  IngestDataOntologyWord -- reads --> OntologyWordEndpoint
  IngestDataOntologyTree -- reads --> OntologyTreeEndpoint  
  IngestDataLocation -- reads --> AccessibilitySentenceEndpoint
  IngestDataLocation -- reads --> AccessibilityShortageEndpoint
  IngestDataLocation -- reads --> AccessibilityViewpointEndpoint
  IngestDataLocation -- reads --> ConnectionEndpoint
  IngestDataLocation -- reads --> UnitEndpoint
  IngestDataLocation -- reads --> DescriptionEndpoint
  IngestDataLocation -- reads --> AccessibilityShortcomingCountEndpoint
  IngestDataLocation -- reads --> OpeningHoursEndpoint
  
  OntologyTreeEndpoint -- mapped to --> OntologyTreeResults
  OntologyWordEndpoint -- mapped to --> OntologyWordResults
  OntologyWordResults -.-> LocationIndex
  OntologyTreeResults -.-> LocationIndex  
  OntologyTreeResults ==> OntologyTreeIndex
  OntologyWordResults ==> OntologyWordIndex
  AccessibilitySentenceEndpoint -- mapped to --> LocationIndex
  AccessibilityShortageEndpoint -- mapped to --> LocationIndex
  AccessibilityViewpointEndpoint -- mapped to --> LocationIndex
  ConnectionEndpoint -- mapped to --> LocationIndex
  UnitEndpoint -- mapped to --> LocationIndex
  DescriptionEndpoint -- mapped to --> LocationIndex
  OpeningHoursEndpoint -- mapped to --> LocationIndex
  AccessibilityShortcomingCountEndpoint -- mapped to --> LocationIndex
  TietoaKuntajaostaZip -- mapped to --> MunigeoResults
  
  MunigeoResults ==> AdminDivIndex
  MunigeoResults -.-> LocationIndex
        
  %% Make parts of the diagram that are only used for layout handling invisible
  %% Workaround for hard-to-control layout i.e. https://github.com/mermaid-js/mermaid/issues/815
  style DataSourcesGroup fill:transparent, stroke-width:3
```
