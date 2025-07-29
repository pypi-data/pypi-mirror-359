from typing import TypedDict


class Signature(TypedDict):
    date: str
    file: str
    hash: str
    full_hash: str


class Metadata(TypedDict):
    model_name: str
    model_short_name: str
    service_provider: str
    creator: str
    tokenizer: str
    date: str
    request_country: str
    signature_hash: str
    system_fingerprint: str


class Message(TypedDict):
    role: str
    content: str


class Configuration(TypedDict):
    target_position: int
    tokens_in: int
    tokens_out: int
    samples_per_position: int
    samples_for_distribution: int
    min_probability_threshold: float
    seed: int
    original_prompt: str
    complete_messages: list[Message]


class Token(TypedDict):
    token_string: str
    token_id: int
    count: int
    probability: float


class DistributionResults(TypedDict):
    total_tokens_collected: int
    unique_tokens_collected: int
    tokens: dict[str, Token]
    filtered_out_tokens: dict[str, Token]


class APIParameters(TypedDict):
    model: str
    temperature: float
    top_p: float
    max_tokens: int
    frequency_penalty: int
    presence_penalty: int
    logprobs: bool
    top_logprobs: int
    store: bool
    stream: bool
    response_format: dict[str, str]
    seed: int
    messages: list[Message]


class PathAnalysis(TypedDict):
    path_tokens: list[str]


class SignatureContent(TypedDict):
    metadata: Metadata
    configuration: Configuration
    signature_parameters: dict[str, str]
    distribution_results: DistributionResults
    api_parameters: APIParameters
    path_analysis: PathAnalysis
