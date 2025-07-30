from transformers import AutoTokenizer

from levanter.data.packing import PromptCompletion
from levanter.eval_harness import LmEvalHarnessConfig, TaskConfig, _iterate_tokenized_requests
from test_utils import skip_if_module_missing


@skip_if_module_missing("lm_eval")
def test_iterate_tokenized_requests_with_chat_template():
    """Test the chat template functionality in _iterate_tokenized_requests"""
    from lm_eval.api.instance import Instance

    # Load a tokenizer with chat template - Llama 3 has one
    hf_tokenizer = AutoTokenizer.from_pretrained("stanford-crfm/marin-tokenizer")
    if hf_tokenizer.pad_token is None:
        hf_tokenizer.pad_token = hf_tokenizer.eos_token

    # Create chat-like requests
    requests = [
        Instance(
            request_type="loglikelihood",
            doc={},
            arguments=("What's the best way to learn Python?", " Practice by building small projects."),
            idx=0,
            metadata=("test_task", 0, None),
        ),
        Instance(
            request_type="loglikelihood",
            doc={},
            arguments=("Explain quantum computing.", " Quantum computing uses quantum bits or qubits."),
            idx=1,
            metadata=("test_task", 1, None),
        ),
    ]

    # Parameters
    max_len = 100  # Larger max_len to accommodate chat template additions
    batch_size = 2

    # Run with chat template
    results = list(_iterate_tokenized_requests(requests, hf_tokenizer, max_len, batch_size, apply_chat_template=True))

    # Verify the results
    assert len(results) == len(requests)

    # Check each result
    for i, result in enumerate(results):
        # Should be a PromptCompletion object
        assert isinstance(result, PromptCompletion)
        assert result.segment_id == i

        # The context should have been transformed by the chat template
        context, completion = requests[i].args

        # Check completion is preserved
        completion_text = completion.strip()
        decoded = hf_tokenizer.decode(result.ids)
        assert completion_text in decoded, f"Completion not found for example {i}"

        # Verify prompt_length is correctly set
        assert result.prompt_length < len(
            result.ids
        ), f"Example {i} has invalid prompt_length ({result.prompt_length} >= {len(result.ids)})"

        # Verify that prompt_length approximately matches the expected chat context length
        # It might not match exactly due to truncation or other processing
        prompt_tokens = result.ids[: result.prompt_length]
        prompt_decoded = hf_tokenizer.decode(prompt_tokens)

        # The prompt should contain key parts of the chat context
        # For a chat template, this typically includes formatting like "<s>[INST]"
        if "<|start_header_id|>" in expected_chat_context:
            assert (
                "<|start_header_id|>" in prompt_decoded
            ), f"Chat template formatting not found in prompt for example {i}"

        # Alternative check: the prompt should be longer than the original context
        # due to the chat template adding formatting
        original_context_tokens = hf_tokenizer(context, truncation=False, padding=False)["input_ids"]
        assert result.prompt_length > len(
            original_context_tokens
        ), f"Prompt length not increased by chat template for example {i}"


@skip_if_module_missing("lm_eval")
def test_iterate_tokenized_requests():
    from lm_eval.api.instance import Instance

    hf_tokenizer = AutoTokenizer.from_pretrained("stanford-crfm/marin-tokenizer")
    if hf_tokenizer.pad_token is None:
        hf_tokenizer.pad_token = hf_tokenizer.eos_token

    requests = [
        Instance(
            request_type="loglikelihood",
            doc={},  # Empty dict as it's not used in the function
            arguments=("What is the capital of France?", " Paris"),
            idx=0,
            metadata=("test_task", 0, None),
        ),
        Instance(
            request_type="loglikelihood",
            doc={},
            arguments=("The quick brown fox", " jumps over the lazy dog"),
            idx=1,
            metadata=("test_task", 1, None),
        ),
        Instance(
            request_type="loglikelihood",
            doc={},
            arguments=("To be or not to be,", " that is the question"),
            idx=2,
            metadata=("test_task", 2, None),
        ),
    ]

    # Parameters
    max_len = 50
    batch_size = 2

    # Run the function
    results = list(_iterate_tokenized_requests(requests, hf_tokenizer, max_len, batch_size))

    # Verify results
    assert len(results) == 3  # One result per request

    for i, result in enumerate(results):
        # Check basic structure
        assert isinstance(result, PromptCompletion)
        assert result.segment_id == i

        # Check token content
        context, completion = requests[i].args
        decoded = hf_tokenizer.decode(result.ids)

        # The decoded tokens should contain the original text
        assert context in decoded or decoded.startswith(context.strip())
        assert completion in decoded or decoded.endswith(completion.strip())

        # Verify prompt_length
        prompt_tokens = result.ids[: result.prompt_length]
        decoded_prompt = hf_tokenizer.decode(prompt_tokens)

        # The decoded prompt should match or contain the context
        assert context.strip() in decoded_prompt

        # Sequence length should be within max_len
        assert len(result.ids) <= max_len


@skip_if_module_missing("lm_eval")
def test_task_config():
    task_spec = [
        TaskConfig(
            task="hellaswag",
            task_alias="hellaswag_10shot",
            num_fewshot=10,
        ),
        TaskConfig(
            task="hellaswag",
            task_alias="hellaswag_5shot",
            num_fewshot=5,
        ),
        "lambada_openai",
    ]

    config = LmEvalHarnessConfig(
        task_spec=task_spec,
    )

    q = config.to_task_dict()

    assert len(q) == 3
