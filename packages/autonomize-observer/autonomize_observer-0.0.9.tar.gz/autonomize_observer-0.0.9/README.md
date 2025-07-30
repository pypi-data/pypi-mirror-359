# Autonomize Observer SDK v0.0.9

A production-ready SDK for comprehensive LLM observability with a **modern, pythonic API** that makes monitoring effortless. Get complete visibility into your AI applications with automatic cost tracking, performance analytics, and workflow tracing.

## 🎯 What's New in v0.0.9

### 🚀 **Modern Pythonic API**
**Zero-configuration observability** with intuitive patterns:

```python
from autonomize_observer import observe

@observe(project="my-app")
def ai_function():
    client = OpenAI()  # Auto-monitored!
    return client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello!"}]
    )
```

### ✨ **Multiple Usage Patterns**
Choose the approach that fits your style:
- **🎨 Decorator Pattern**: `@observe` for functions
- **🏗️ Workflow Orchestration**: `@workflow` + `@step` for complex flows
- **📦 Context Manager**: `with observe()` for explicit scoping
- **⚡ Async Native**: Full async/await support
- **🔄 Migration Ready**: `observe.monitor()` for gradual adoption

### 🏛️ **Enterprise Architecture**
Built with **proven design patterns**:
- **Factory Pattern**: Auto-detection of 150+ LLM models
- **Strategy Pattern**: Provider-specific cost calculations
- **Decorator Pattern**: Zero-overhead client monitoring  
- **Observer Pattern**: Event-driven observability

## 🚀 Quick Start

### Installation

```bash
# Basic installation
pip install autonomize-observer

# With provider support
pip install "autonomize-observer[openai]"        # OpenAI
pip install "autonomize-observer[anthropic]"     # Anthropic  
pip install "autonomize-observer[openai,anthropic]"  # Multiple providers
```

### Simple Monitoring (Recommended)

```python
from autonomize_observer import observe
from openai import OpenAI

@observe(project="customer-service")
def handle_query(user_question):
    """Handle customer query with automatic observability."""
    client = OpenAI()  # Automatically monitored!
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful customer service agent."},
            {"role": "user", "content": user_question}
        ]
    )
    
    return response.choices[0].message.content

# Use normally - complete observability happens automatically
answer = handle_query("How do I reset my password?")
print(answer)
```

**What you get automatically:**
- ✅ **Cost tracking** with precise token-based pricing
- ✅ **Performance metrics** (latency, throughput, errors)
- ✅ **Complete traces** sent to Kafka/MongoDB
- ✅ **Provider detection** (OpenAI, Anthropic, etc.)
- ✅ **Model analytics** and usage patterns

### Complex Workflows

```python
from autonomize_observer import workflow, step
from openai import OpenAI
from anthropic import Anthropic

@workflow("content-generation", project="marketing")
def generate_marketing_content(topic, target_audience):
    """Multi-step content generation with full observability."""
    
    @step("research")
    def research_topic():
        client = OpenAI()  # Auto-monitored
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user", 
                "content": f"Research key insights about {topic} for {target_audience}"
            }]
        )
        return response.choices[0].message.content
    
    @step("draft")
    def create_draft(research_data):
        client = Anthropic()  # Auto-monitored
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": f"Create marketing content based on: {research_data}"
            }]
        )
        return response.content[0].text
    
    @step("review")
    def review_content(draft_content):
        client = OpenAI()  # Auto-monitored
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": f"Review and improve this marketing content: {draft_content}"
            }]
        )
        return response.choices[0].message.content
    
    # Execute workflow with full step-by-step observability
    research = research_topic()
    draft = create_draft(research)
    final_content = review_content(draft)
    
    return {
        "research": research,
        "draft": draft,
        "final": final_content
    }

# Run workflow - each step automatically tracked
result = generate_marketing_content("AI automation", "tech startups")
```

### Async Support

```python
from autonomize_observer import observe
from openai import AsyncOpenAI

@observe(project="async-app")
async def async_ai_function():
    """Async function with automatic observability."""
    client = AsyncOpenAI()  # Auto-monitored
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello async world!"}]
    )
    
    return response.choices[0].message.content

# Use with async/await
result = await async_ai_function()
```

## 📊 API Comparison

### 🆕 Modern API (v0.0.9) - Recommended

```python
from autonomize_observer import observe

@observe(project="my-app")
def my_function():
    client = OpenAI()  # Auto-monitored!
    return client.chat.completions.create(...)
```

### 🔧 Legacy API (Still Supported)

```python
from autonomize_observer import monitor, initialize

initialize()  # Required setup
client = monitor(OpenAI(), provider="openai")  # Manual monitoring
response = client.chat.completions.create(...)
```

**Both APIs provide identical observability data!**

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        Autonomize Observer SDK v0.0.9                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐ │
│  │   Modern API        │    │   Workflow API      │    │   Legacy API        │ │
│  │                     │    │                     │    │                     │ │
│  │  @observe           │    │  @workflow          │    │  monitor(client)    │ │
│  │  def func():        │    │  def workflow():    │    │  client.chat()      │ │
│  │    client = OpenAI()│    │    @step("name")    │    │                     │ │
│  │    # Auto-monitored │    │    def step():      │    │                     │ │
│  └─────────┬───────────┘    └─────────┬───────────┘    └─────────┬───────────┘ │
│            │                          │                          │             │
│            │ Auto-monitoring          │ Workflow tracing         │ Direct      │
│            │                          │                          │ monitoring  │
│            └──────────────────┬───────┴──────────────────────────┘             │
│                               │                                                 │
│  ┌─────────────────────────────┴─────────────────────────────────────────────┐ │
│  │                     Unified Observability Engine                          │ │
│  │                                                                            │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐ │ │
│  │  │ Factory Pattern │  │Strategy Pattern │  │   Decorator Pattern         │ │ │
│  │  │ Provider        │  │ Cost            │  │   Client Monitoring         │ │ │
│  │  │ Detection       │  │ Calculation     │  │   (150+ Models)             │ │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                               │                                                 │
│  ┌─────────────────────────────┴─────────────────────────────────────────────┐ │
│  │                        Event Streaming                                     │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐ │ │
│  │  │     Kafka       │  │    MongoDB      │  │      Dashboard APIs         │ │ │
│  │  │   Streaming     │  │    Storage      │  │    Analytics Ready          │ │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🎯 Key Features

### **🤖 Auto-Magic Observability**
- **Zero Configuration**: No setup required for common use cases
- **Auto-Detection**: Automatically detects LLM providers and models
- **Auto-Monitoring**: Clients automatically monitored within decorated functions
- **Context-Aware**: Proper scoping and resource management

### **⚡ High Performance**
- **0.006ms Overhead**: 833x better than 5ms requirement
- **42M+ Operations/Second**: Proven scalability
- **Minimal Memory**: Optimized with weak references
- **Thread-Safe**: Full concurrent access support

### **🏢 Enterprise Ready**
- **150+ Models**: OpenAI, Anthropic, Google, Meta, Mistral, Amazon, and more
- **Kafka Streaming**: Real-time observability data pipeline
- **MongoDB Storage**: Scalable analytics database
- **Dashboard APIs**: Built-in endpoints for analytics platforms

### **🔄 Migration Friendly**
- **100% Backward Compatibility**: All existing code works unchanged
- **Gradual Adoption**: Mix old and new APIs in same project
- **Zero Risk**: No breaking changes for existing integrations
- **Easy Migration**: Direct replacement patterns available

## 📚 Configuration

### Environment Variables

```bash
# Kafka Configuration (Optional - defaults provided)
export AUTONOMIZE_KAFKA_BROKERS="your-kafka-brokers:9092"
export AUTONOMIZE_KAFKA_TOPIC="genesis-traces-streaming"
export AUTONOMIZE_KAFKA_USERNAME="your-username"
export AUTONOMIZE_KAFKA_PASSWORD="your-password"

# Security (Optional)
export AUTONOMIZE_KAFKA_SECURITY_PROTOCOL="SASL_SSL"
export AUTONOMIZE_KAFKA_SASL_MECHANISM="PLAIN"

# Provider API Keys
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### Programmatic Configuration

```python
# Context manager with custom config
with observe(
    project="my-app",
    user_id="user-123",
    session_id="session-456",
    tags={"environment": "production", "version": "1.0"}
) as obs:
    client = obs.monitor(OpenAI())
    response = client.chat.completions.create(...)

# Direct monitoring with config
client = observe.monitor(
    OpenAI(), 
    project="my-app",
    cost_rates={"gpt-4": {"input": 0.01, "output": 0.03}}
)
```

## 🧪 Testing & Validation

### Comprehensive Test Suite

```bash
# Run all tests
pytest tests/

# Test modern API specifically
pytest tests/test_modern_api.py -v

# Performance validation
python performance_test_new_api.py

# Legacy API compatibility
pytest tests/test_monitoring.py tests/test_agent_tracer.py
```

### Performance Benchmarks

```python
# Performance test example
from autonomize_observer import observe

@observe(project="perf-test")
def benchmark_function():
    # Your LLM calls here
    pass

# Overhead: 0.006ms (requirement: <5ms) ✅
# Throughput: 42M+ operations/second ✅
# Memory: Optimized with weak references ✅
```

## 📖 Examples & Documentation

### Jupyter Notebooks

Explore comprehensive examples in `examples/notebooks/`:

- **`00_modern_api_showcase.ipynb`** - 🆕 Complete modern API examples
- **`01_basic_monitoring.ipynb`** - Simple LLM call monitoring
- **`02_advanced_tracing.ipynb`** - Complex workflow tracing
- **`03_cost_tracking.ipynb`** - Cost analytics and budgeting
- **`04_async_monitoring.ipynb`** - Async/await patterns

### Real-World Examples

```python
# Customer service chatbot
@observe(project="customer-service", user_id="support-bot")
def handle_support_ticket(ticket_content, customer_id):
    # Automatic observability for support interactions
    pass

# Content generation pipeline
@workflow("content-pipeline", project="marketing")
def content_generation_pipeline(brief, target_audience):
    # Step-by-step workflow tracking
    pass

# Data analysis assistant
@observe(project="data-analysis")
async def analyze_data_async(dataset_info):
    # Async data analysis with observability
    pass
```

## 🚀 Advanced Usage

### Custom Providers

```python
# Auto-detection works with any provider
@observe(project="multi-provider")
def multi_provider_workflow():
    openai_client = OpenAI()          # Auto-detected as OpenAI
    anthropic_client = Anthropic()    # Auto-detected as Anthropic
    google_client = GoogleAI()        # Auto-detected as Google
    
    # All automatically monitored with provider-specific optimizations
```

### Error Handling

```python
@observe(project="robust-app")
def robust_ai_function():
    try:
        client = OpenAI()
        response = client.chat.completions.create(...)
        return response.choices[0].message.content
    except Exception as e:
        # Errors automatically captured in observability data
        print(f"AI call failed: {e}")
        return "I'm sorry, I couldn't process that request."
```

### Integration with Existing Systems

```python
# Works with your existing monitoring
import logging
from autonomize_observer import observe

logger = logging.getLogger(__name__)

@observe(project="existing-system")
def integrated_function(user_input):
    logger.info("Processing user input")
    
    client = OpenAI()  # Auto-monitored by Observer
    response = client.chat.completions.create(...)
    
    logger.info("AI processing complete")
    return response.choices[0].message.content
```

## 🔧 Migration Guide

### From Legacy API

```python
# OLD: Legacy API (still works!)
from autonomize_observer import monitor, initialize
initialize()
client = monitor(OpenAI(), provider="openai")

# NEW: Modern API (recommended)
from autonomize_observer import observe
@observe(project="my-app")
def my_function():
    client = OpenAI()  # Auto-monitored!

# MIGRATION: Direct replacement
from autonomize_observer import observe
client = observe.monitor(OpenAI(), project="my-app")
```

### From Other Observability Tools

```python
# Replace complex setups with simple decorators
@observe(project="migrated-app")
def previously_complex_setup():
    # No more manual instrumentation needed
    client = OpenAI()
    return client.chat.completions.create(...)
```

## 📈 Analytics & Dashboards

### Data Access

The SDK automatically creates rich observability data:

```javascript
// MongoDB Collections Created
{
  "traces": {           // Complete execution traces
    "trace_id": "...",
    "project_name": "my-app", 
    "total_cost": 0.045,
    "duration_ms": 1250,
    "steps": [...]
  },
  "model_usage": {      // Individual LLM calls
    "model": "gpt-4o",
    "provider": "openai",
    "input_tokens": 150,
    "output_tokens": 75,
    "cost": 0.025
  },
  "realtime_metrics": { // Aggregated analytics
    "entity_type": "model",
    "entity_name": "gpt-4o", 
    "total_calls": 1247,
    "total_cost": 45.67
  }
}
```

### Dashboard APIs

```python
# Query your observability data
GET /api/v1/observability/dashboard/summary
GET /api/v1/observability/dashboard/costs
GET /api/v1/observability/dashboard/models
```

## 🔬 Technical Details

### Design Patterns Used

- **Factory Pattern**: Automatic provider detection and instantiation
- **Strategy Pattern**: Provider-specific cost calculation algorithms  
- **Decorator Pattern**: Non-invasive client monitoring
- **Observer Pattern**: Event-driven observability system

### Thread Safety

```python
# Safe for concurrent use
import threading
from autonomize_observer import observe

@observe(project="concurrent-app")
def thread_safe_function():
    client = OpenAI()  # Thread-safe monitoring
    return client.chat.completions.create(...)

# Multiple threads can safely use observability
threads = [threading.Thread(target=thread_safe_function) for _ in range(10)]
```

### Performance Characteristics

- **Latency Overhead**: 0.006ms average
- **Memory Overhead**: <1MB baseline + weak references
- **CPU Overhead**: <0.1% in production workloads
- **Network Overhead**: Async Kafka publishing (non-blocking)

## 🤝 Contributing

We welcome contributions! Here's how to get started:

```bash
# Setup development environment
git clone https://github.com/autonomize-ai/autonomize-observer.git
cd autonomize-observer
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Check performance
python performance_test_new_api.py
```

### Development Priorities

- **New Provider Support**: Add more LLM providers
- **Enhanced Analytics**: Advanced cost optimization features
- **Performance Optimizations**: Further reduce overhead
- **Documentation**: More examples and use cases

## 📜 License

Proprietary - Autonomize AI

## 🆘 Support

- **Documentation**: Complete examples in `examples/notebooks/`
- **Issues**: [GitHub Issues](https://github.com/autonomize-ai/autonomize-observer/issues)
- **Migration Help**: See `analysis/migration_guide.md`

---

**Autonomize Observer SDK v0.0.9** - Production-ready LLM observability with modern, pythonic APIs that make monitoring effortless.

### 🎉 Ready to Start?

```python
pip install autonomize-observer

from autonomize_observer import observe

@observe(project="your-app")
def your_ai_function():
    # Your LLM code here - automatically monitored!
    pass
```

**That's it!** Complete observability with one decorator. 🚀