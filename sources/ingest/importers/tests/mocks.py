import json
import os

mocks_dir = os.path.dirname(__file__)
unit_swimhall = json.load(
    open(os.path.join(mocks_dir, "mock_responses/unit-41102.json"))
)
unit_indoor_arena = json.load(
    open(os.path.join(mocks_dir, "mock_responses/unit-42284.json"))
)
ontology_tree = json.load(
    open(os.path.join(mocks_dir, "mock_responses/ontology_tree.json"))
)
ontology_words = json.load(
    open(os.path.join(mocks_dir, "mock_responses/ontology_words.json"))
)


MOCKED_SERVICE_MAP_UNITS_RESPONSE = [
    {k: v for k, v in unit.items() if k not in {"connections"}}
    for unit in [unit_swimhall, unit_indoor_arena]
]

MOCKED_SERVICE_MAP_CONNECTIONS_RESPONSE = [
    {**connection, "unit_id": unit["id"]}
    for unit in [unit_swimhall, unit_indoor_arena]
    for connection in unit["connections"]
]

MOCKED_SERVICE_MAP_ACCESSIBILITY_SENTENCE_VIEWPOINT_RESPONSE = [
    {
        "unit_id": 6365,
        "sentence_group_name": "Kulkureitti pääsisäänkäynnille",
        "sentence_group_fi": "Reitti pääsisäänkäynnille",
        "sentence_group_sv": "Rutten till huvudingången",
        "sentence_group_en": "The route to the main entrance",
        "sentence_fi": "Kulkureitti sisäänkäynnille on tasainen ja riittävän leveä sekä valaistu.",
        "sentence_sv": "Rutten till ingången är jämn och tillräckligt bred samt belyst.",
        "sentence_en": "The route to the entrance is smooth and sufficiently wide and illuminated.",
    },
    {
        "unit_id": 6365,
        "sentence_group_name": "Pääsisäänkäynti",
        "sentence_group_fi": "Pääsisäänkäynti",
        "sentence_group_sv": "Huvudingången",
        "sentence_group_en": "The main entrance",
        "sentence_fi": "Sisäänkäynti sijaitsee syvennyksessä ja on valaistu.",
        "sentence_sv": "Ingången är belägen i en nisch och belyst.",
        "sentence_en": "The entrance is located in a recess and is illuminated.",
    },
    {
        "unit_id": 1414,
        "sentence_group_name": "Sisätilat",
        "sentence_group_fi": "Sisätilat",
        "sentence_group_sv": "I lokalen",
        "sentence_fi": "Toimipisteessä on esteetön wc.",
        "sentence_sv": "I verksamhetslokalen finns en tillgänglig toalett.",
    },
]

MOCKED_SERVICE_MAP_ACCESSIBILITY_SHORTAGE_VIEWPOINT_RESPONSE = [
    {
        "unit_id": 2,
        "viewpoint_id": "32",
        "shortage_fi": "Esteettömiä autopaikkoja ei ole.",
        "shortage_sv": "Inga p-platser för personer med rörelsehinder.",
        "shortage_en": "No parking places for persons with a disability.",
    },
    {
        "unit_id": 2,
        "viewpoint_id": "32",
        "shortage_fi": "Sisäänkäynnissä on ahdas tuulikaappi.",
        "shortage_sv": "Det finns ett trångt vindfång vid ingången.",
        "shortage_en": "The entrance has a cramped foyer.",
    },
    {
        "unit_id": 2,
        "viewpoint_id": "21",
        "shortage_fi": "Ei puutteita.",
        "shortage_sv": "Inga brister.",
        "shortage_en": "No shortcomings.",
    },
    {
        "unit_id": 16,
        "viewpoint_id": "33",
        "shortage_fi": "Toimipisteessä ei ole esteetöntä wc:tä.",
        "shortage_sv": "Det finns ingen tillgänglig toalett i verksamhetsstället.",
        "shortage_en": "The facility does not have an accessible toilet.",
    },
]

MOCKED_SERVICE_MAP_UNIT_VIEWPOINT_RESPONSE = {
    "count": 3,
    "next": None,
    "previous": None,
    "results": [
        {
            "id": 72023,
            "accessibility_shortcoming_count": {
                "rollator": 2,
                "wheelchair": 2,
                "hearing_aid": 1,
                "reduced_mobility": 1,
                "visually_impaired": 2,
                "stroller": 5,
            },
        },
        {
            "id": 71689,
            "accessibility_shortcoming_count": {
                "rollator": 4,
                "wheelchair": 4,
                "reduced_mobility": 3,
                "visually_impaired": 6,
            },
        },
        {"id": 71688, "accessibility_shortcoming_count": {}},
    ],
}


MOCKED_SERVICE_MAP_ACCESSIBILITY_VIEWPOINT_RESPONSE = [
    {
        "id": "00",
        "name_fi": "Valitse esteettömyysnäkökulma (Testi)",
        "name_sv": "Välj tillgänglighetsperspektiv (Test)",
        "name_en": "Choose accessibility perspective (Test)",
        "values": ["unknown"],
    },
    {
        "id": "11",
        "name_fi": "Olen pyörätuolin käyttäjä",
        "name_sv": "Jag är en rullstolsanvändare",
        "name_en": "I am a wheelchair user",
        "values": ["unknown", "green", "red"],
    },
    {
        "id": "12",
        "name_fi": "Olen pyörätuolin käyttäjä - saavun omalla autolla",
        "name_sv": "Jag är en rullstolsanvändare - kommer med min egen bil",
        "name_en": "I am a wheelchair user - arrive by my car",
        "values": ["unknown", "green", "red"],
    },
    {
        "id": "13",
        "name_fi": "Olen pyörätuolin käyttäjä - saavun saattoliikenteellä",
        "name_sv": "Jag är en rullstolsanvändare - kommer med angöringstrafik",
        "name_en": "I am a wheelchair user - arrive with pick-up and drop-off traffic",
        "values": ["unknown", "green", "red"],
    },
    {
        "id": "21",
        "name_fi": "Olen liikkumisesteinen, mutta kävelen",
        "name_sv": "Jag är rörelsehindrad, men jag går",
        "name_en": "I have reduced mobility, but I walk",
        "values": ["unknown", "green", "red"],
    },
    {
        "id": "22",
        "name_fi": "Olen liikkumisesteinen, mutta kävelen - saavun omalla autolla",
        "name_sv": "Jag är rörelsehindrad, men jag går - kommer med min egen bil",
        "name_en": "I have reduced mobility, but I walk - arrive by my car",
        "values": ["unknown", "green", "red"],
    },
    {
        "id": "23",
        "name_fi": "Olen liikkumisesteinen, mutta kävelen - saavun saattoliikenteellä",
        "name_sv": "Jag är rörelsehindrad, men jag går - kommer med angöringstrafik",
        "name_en": "I have reduced mobility, but I walk - arrive with pick-up and drop-off traffic",
        "values": ["unknown", "green", "red"],
    },
    {
        "id": "31",
        "name_fi": "Olen rollaattorin käyttäjä",
        "name_sv": "Jag är en rollatoranvändare",
        "name_en": "I am a rollator user",
        "values": ["unknown", "green", "red"],
    },
    {
        "id": "32",
        "name_fi": "Olen rollaattorin käyttäjä - saavun omalla autolla",
        "name_sv": "Jag är en rollatoranvändare - kommer med min egen bil",
        "name_en": "I am a rollator user - arrive by my car",
        "values": ["unknown", "green", "red"],
    },
    {
        "id": "33",
        "name_fi": "Olen rollaattorin käyttäjä - saavun saattoliikenteellä",
        "name_sv": "Jag är en rollatoranvändare - kommer med angöringstrafik",
        "name_en": "I am a rollator user - arrive with pick-up and drop-off traffic",
        "values": ["unknown", "green", "red"],
    },
    {
        "id": "41",
        "name_fi": "Minulla on lastenvaunut",
        "name_sv": "Jag är en barnvagnsdragare",
        "name_en": "I am a stroller pusher",
        "values": ["unknown", "green", "red"],
    },
    {
        "id": "51",
        "name_fi": "Olen näkövammainen",
        "name_sv": "Jag är synskadad",
        "name_en": "I am visually impaired",
        "values": ["unknown", "green", "red"],
    },
    {
        "id": "52",
        "name_fi": "Olen näkövammainen - saavun saattoliikenteellä",
        "name_sv": "Jag är synskadad - kommer med angöringstrafik",
        "name_en": "I am visually impaired - arrive with pick-up and drop-off traffic",
        "values": ["unknown", "green", "red"],
    },
    {
        "id": "61",
        "name_fi": "Käytän kuulolaitetta",
        "name_sv": "Jag använder en hörapparat",
        "name_en": "I use a hearing aid",
        "values": ["unknown", "green", "red"],
    },
]


MOCKED_SERVICE_REGISTRY_DESCRIPTION_VIEWPOINT_RESPONSE = [
    {
        "id": 11,
        "target_groups": ["CHILDREN_AND_FAMILIES", "INDIVIDUALS", "YOUTH"],
        "unit_ids": [1, 2, 3, 4, 5],
    },
    {"id": 12, "target_groups": ["IMMIGRANTS"], "unit_ids": [1, 3, 13, 36]},
    {"id": 634, "target_groups": [], "unit_ids": [1234]},
    {
        "id": 634,
        "target_groups": [
            "ASSOCIATIONS",
            "CHILDREN_AND_FAMILIES",
            "DISABLED",
            "ELDERLY_PEOPLE",
            "IMMIGRANTS",
            "INDIVIDUALS",
            "YOUTH",
        ],
        "unit_ids": [2, 5],
    },
]


MOCK_OPENING_HOURS_RESPONSE = {
    "count": 5,
    "next": None,
    "previous": None,
    "results": [
        {
            "resource": {
                "id": 11,
                "name": {
                    "fi": "Leikkipuisto Kannelmäki",
                    "sv": "Lekparken Kannelmäki",
                    "en": "Playground Kannelmäki",
                },
                "timezone": "Europe/Helsinki",
                "origins": [
                    {
                        "data_source": {
                            "id": "tprek",
                            "name": {"fi": None, "sv": None, "en": None},
                        },
                        "origin_id": "1",
                    }
                ],
            },
            "opening_hours": [
                {
                    "date": "2021-09-03",
                    "times": [
                        {
                            "name": "",
                            "description": "",
                            "start_time": "11:00:00",
                            "end_time": "18:00:00",
                            "end_time_on_next_day": False,
                            "resource_state": "open",
                            "full_day": False,
                            "periods": [1267],
                        }
                    ],
                }
            ],
        },
        {
            "resource": {
                "id": 22,
                "name": {
                    "fi": "Leikkipuisto Kaunokki",
                    "sv": "Lekparken Kaunokki",
                    "en": "Playground Kaunokki",
                },
                "timezone": "Europe/Helsinki",
                "origins": [
                    {
                        "data_source": {
                            "id": "tprek",
                            "name": {"fi": None, "sv": None, "en": None},
                        },
                        "origin_id": "4",
                    }
                ],
            },
            "opening_hours": [
                {
                    "date": "2021-09-03",
                    "times": [
                        {
                            "name": "",
                            "description": "",
                            "start_time": "09:00:00",
                            "end_time": "16:00:00",
                            "end_time_on_next_day": False,
                            "resource_state": "open",
                            "full_day": False,
                            "periods": [1306],
                        }
                    ],
                },
                {
                    "date": "2021-09-03",
                    "times": [
                        {
                            "name": "",
                            "description": "",
                            "start_time": "10:00:00",
                            "end_time": "11:00:00",
                            "end_time_on_next_day": False,
                            "resource_state": "closed",
                            "full_day": False,
                            "periods": [1306],
                        }
                    ],
                },
                {
                    "date": "2021-09-04",
                    "times": [
                        {
                            "name": "",
                            "description": "",
                            "start_time": None,
                            "end_time": None,
                            "end_time_on_next_day": False,
                            "resource_state": "open",
                            "full_day": True,
                            "periods": [1306],
                        }
                    ],
                },
                {
                    "date": "2021-09-05",
                    "times": [
                        {
                            "name": "",
                            "description": "",
                            "start_time": None,
                            "end_time": None,
                            "end_time_on_next_day": False,
                            "resource_state": "closed",
                            "full_day": True,
                            "periods": [1306],
                        }
                    ],
                },
                {
                    "date": "2021-09-06",
                    "times": [
                        {
                            "name": "",
                            "description": "",
                            "start_time": "09:00:00",
                            "end_time": "05:00:00",
                            "end_time_on_next_day": True,
                            "resource_state": "open",
                            "full_day": False,
                            "periods": [1306],
                        }
                    ],
                },
            ],
        },
    ],
}
