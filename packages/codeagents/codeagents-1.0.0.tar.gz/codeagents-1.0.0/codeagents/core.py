class CodeAgent:
    def __init__(self, name):
        self.name = name
    
    def execute(self, code):
        print(f"{self.name} is executing: {code}")
        return f"Executed: {code}"
    
    def analyze(self, code):
        return {
            "lines": len(code.split('\n')),
            "characters": len(code),
            "agent": self.name
        }