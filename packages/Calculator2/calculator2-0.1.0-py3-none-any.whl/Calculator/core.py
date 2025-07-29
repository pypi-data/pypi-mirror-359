import re

class Calculator:
    def __init__(self):
        self.pattern = re.compile(r'^[\d+\-*/().\s]+$')
        
    def calc(self, expression):
        if not self.pattern.match(expression):
            raise ValueError("Espressione non valida")
        try:
            return eval(expression)
        except Exception as e:
            raise ValueError(f"Errore nel calcolo: {e}")
