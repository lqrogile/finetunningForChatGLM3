#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Annotated, Union

import typer
from peft import AutoPeftModelForCausalLM, PeftModelForCausalLM
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
)

ModelType = Union[PreTrainedModel, PeftModelForCausalLM]
TokenizerType = Union[PreTrainedTokenizer, PreTrainedTokenizerFast]

app = typer.Typer(pretty_exceptions_show_locals=False)


def _resolve_path(path: Union[str, Path]) -> Path:
    return Path(path).expanduser().resolve()


def load_model_and_tokenizer(model_dir: Union[str, Path]) -> tuple[ModelType, TokenizerType]:
    model_dir = _resolve_path(model_dir)
    if (model_dir / 'adapter_config.json').exists():
        model = AutoPeftModelForCausalLM.from_pretrained(
            model_dir, trust_remote_code=True, device_map='auto'
        )
        tokenizer_dir = model.peft_config['default'].base_model_name_or_path
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_dir, trust_remote_code=True, device_map='auto'
        )
        tokenizer_dir = model_dir
    tokenizer = AutoTokenizer.from_pretrained(
        tokenizer_dir, trust_remote_code=True
    )
    return model, tokenizer


@app.command()
def main(
        model_dir: Annotated[str, typer.Argument(help='')],
        prompt: Annotated[str, typer.Option(help='')],
):
    model, tokenizer = load_model_and_tokenizer(model_dir)
    # prompt += "你是针对金融文本摘要生成微调后的大语言模型，用户将输入金融领域的文本，你针对用户输入的文本生成摘要，要求包括输入文本的关键信息，在最后输出给用户前，你需要调整语言风格，使其看起来更加严谨准确，且符合摘要的格式。"
    history = []
    response, _ = model.chat(tokenizer, prompt, history)
    print(response)


if __name__ == '__main__':
    app()
