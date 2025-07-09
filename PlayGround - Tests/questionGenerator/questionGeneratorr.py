import os

class QuestionGenerator:
    def __init__(self, base_path="LLM_testing\questionGenerator"):
        self.questions = []
        self._load_questions(base_path)

    def _load_questions(self, base_path):
        filenames = ["set1.txt"]
        for name in filenames:
            filepath = os.path.join(base_path, name)
            print(f"[DEBUG] Leyendo: {filepath}")
            try:
                with open(filepath, "r", encoding="utf-8") as file:
                    for line in file:
                        parts = line.strip().split("#")
                        if len(parts) >= 3:
                            question = parts[2]
                            self.questions.append(question)
                        else:
                            print(f"[WARNING] Línea malformada ignorada: {line.strip()}")
            except FileNotFoundError:
                print(f"[ERROR] Archivo no encontrado: {filepath}")

    def get_question(self):
        if self.questions:
            return self.questions.pop(0)
        else:
            return None
