class SpecialistEngine:
    def __init__(self):
        self.facts = set()
        self.rules = []

    def add_fact(self, fact):
        self.facts.add(fact)

    def add_rule(self, condition, result):
        self.rules.append((condition, result))

    def infer(self):
        new_infer = True
        while new_infer:
            new_infer = False
            for condition, result in self.rules:
                if condition.issubset(self.facts) and result not in self.facts:
                    print(f"Rule Applied: {condition}, Inferred: {result}")
                    self.facts.add(result)
                    new_infer = True    

engine = SpecialistEngine()

engine.add_fact("Animal tem penas")
engine.add_fact("Animal voa")

engine.add_rule({"Animal tem penas", "Animal voa"}, "Animal é uma ave")
engine.add_rule({"Animal é uma ave", "Animal tem bico"}, "Animal é um pinguim")

engine.infer()

print("Fatos finais:", engine.facts)