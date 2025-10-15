import json
class BaseDados:

    def base_conhecimento (self):
        return json.load(open("dados.json"))

"""    def base_conhecimento (self):
        return {
            "colica": {"choro intenso", "dor abdominal", "noite", "chora"},
            "resfriado": {"coriza", "dificuldade respirar", "febre baixa"},
            "febre": {"febre alta", "mal estar"},
            "gastrite": {"vomito","pos alimentacao", "irritacao"},
            "alergia_alimentar": {"erupcao na pele", "dificuldade respirar",}
        }
"""