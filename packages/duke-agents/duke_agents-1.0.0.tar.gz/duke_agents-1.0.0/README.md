# DUKE Agents

[![PyPI version](https://badge.fury.io/py/duke-agents.svg)](https://badge.fury.io/py/duke-agents)
[![Python Support](https://img.shields.io/pypi/pyversions/duke-agents.svg)](https://pypi.org/project/duke-agents/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://readthedocs.org/projects/duke-agents/badge/?version=latest)](https://duke-agents.readthedocs.io/en/latest/?badge=latest)

DUKE Agents is an advanced AI agent framework implementing the IPO (Input-Process-Output) architecture with enriched memory and feedback loops. It provides autonomous agents powered by Mistral LLMs for complex task execution.

## 🚀 Features

- **IPO Architecture**: Structured Input-Process-Output workflow with memory persistence
- **Multiple Agent Types**: AtomicAgent for simple tasks, CodeActAgent for code generation and execution
- **Mistral Integration**: Native support for Mistral and Codestral models
- **Memory Management**: Rich workflow memory with feedback loops
- **Auto-correction**: Built-in retry logic with satisfaction scoring
- **Flexible Orchestration**: Linear and LLM-driven workflow execution
- **Type Safety**: Full Pydantic models for type validation

## 📦 Installation

```bash
pip install duke-agents
```

### Prerequisites

- Python 3.8 or higher
- Mistral API key (get one at [console.mistral.ai](https://console.mistral.ai))

## 🔧 Quick Start

### Basic Usage

```python
from duke_agents import AtomicAgent, ContextManager, Orchestrator
from duke_agents.models import AtomicInput

# Set your Mistral API key
import os
os.environ["MISTRAL_API_KEY"] = "your-api-key"

# Initialize context manager
context = ContextManager("Process customer data")

# Create orchestrator
orchestrator = Orchestrator(context)

# Create and register an agent
agent = AtomicAgent("data_processor")
orchestrator.register_agent(agent)

# Define workflow
workflow = [{
    'agent': 'data_processor',
    'input_type': 'atomic',
    'input_data': {
        'task_id': 'task_001',
        'parameters': {'data': 'customer info'}
    }
}]

# Execute workflow
results = orchestrator.execute_linear_workflow(workflow)
```

### Code Generation Example

```python
from duke_agents import CodeActAgent, ContextManager, Orchestrator

# Initialize
context = ContextManager("Generate data analysis code")
orchestrator = Orchestrator(context)

# Create code generation agent
code_agent = CodeActAgent("analyst")
orchestrator.register_agent(code_agent)

# Execute
workflow = [{
    'agent': 'analyst',
    'input_type': 'codeact',
    'input_data': {
        'prompt': 'Create a function to analyze sales data and return top 5 products'
    }
}]

results = orchestrator.execute_linear_workflow(workflow)

# Generated code is in results[0].generated_code
if results[0].success:
    print(f"Generated code:\n{results[0].generated_code}")
    print(f"Execution result: {results[0].execution_result}")
```

## 📚 Documentation

Full documentation is available at [duke-agents.readthedocs.io](https://duke-agents.readthedocs.io).

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) first.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Mistral AI](https://mistral.ai) models
- Implements IPO architecture for robust agent workflows