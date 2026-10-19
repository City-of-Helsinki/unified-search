from munigeo.importer.helsinki import HelsinkiImporter as MunigeoHelsinkiImporter


class HelsinkiImporter(MunigeoHelsinkiImporter):
    hsy_layer = "taustakartat_ja_aluejaot:seutukartta_pien_2021"
    hsy_municipalities = {"091", "092", "049", "235"}

    def _import_one_division_type(self, muni, div):
        if div.get("wfs_layer") == self.hsy_layer:
            div = {**div, "wfs_url": "https://kartta.hsy.fi/geoserver/wfs"}
        return super()._import_one_division_type(muni, div)

    def _import_division(self, muni, div, type_obj, syncher, parent_dict, feat):
        if (
            div.get("wfs_layer") == self.hsy_layer
            and feat["kunta"].as_string() not in self.hsy_municipalities
        ):
            return
        return super()._import_division(muni, div, type_obj, syncher, parent_dict, feat)
