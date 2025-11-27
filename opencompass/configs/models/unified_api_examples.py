"""Example configurations for Unified API Model."""

from opencompass.models import UnifiedAPIModel

# OpenAI API configuration example
openai_api_meta_template = dict(round=[
    dict(role='HUMAN', api_role='HUMAN'),
    dict(role='BOT', api_role='BOT', generate=True),
])

openai_model = dict(
    abbr='unified-openai',
    type=UnifiedAPIModel,
    path='gpt-3.5-turbo',
    config=dict(
        adapter_type='openai',
        api_key='YOUR_OPENAI_API_KEY',  # In production, use environment variables
        endpoint='https://api.openai.com/v1/chat/completions',
        model='gpt-3.5-turbo',
    ),
    meta_template=openai_api_meta_template,
    query_per_second=1,
    max_out_len=2048,
    max_seq_len=4096,
    batch_size=8,
)

# Edge RESTful API configuration example
edge_api_meta_template = dict(round=[
    dict(role='HUMAN', api_role='HUMAN'),
    dict(role='BOT', api_role='BOT', generate=True),
])

edge_model = dict(
    abbr='unified-edge-restful',
    type=UnifiedAPIModel,
    path='custom-edge-model',
    config=dict(
        adapter_type='restful',
        endpoint='http://localhost:8000/api/v1/chat',
        method='POST',
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer YOUR_TOKEN',
        },
        request_mapping={
            'prompt': 'input.prompt',
            'max_tokens': 'params.max_new_tokens',
        },
        response_mapping={
            'result': 'data.result',
        },
    ),
    meta_template=edge_api_meta_template,
    query_per_second=2,
    max_out_len=1024,
    max_seq_len=2048,
    batch_size=4,
)

# Collection of example models
models = [openai_model, edge_model]