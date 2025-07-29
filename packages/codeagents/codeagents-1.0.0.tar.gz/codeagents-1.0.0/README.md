# CodeAgents

A powerful library for building code agents.

## Installation

### npm
```bash
npm install codeagents
```

### pip
```bash
pip install codeagents
```

## Usage

### JavaScript
```javascript
const { CodeAgent } = require('codeagents');

const agent = new CodeAgent('MyAgent');
const result = agent.execute('console.log("Hello World")');
const analysis = agent.analyze('const x = 5;\nconst y = 10;');
```

### Python
```python
from codeagents import CodeAgent

agent = CodeAgent('MyAgent')
result = agent.execute('print("Hello World")')
analysis = agent.analyze('x = 5\ny = 10')
```

## License

MIT