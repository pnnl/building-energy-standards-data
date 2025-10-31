import argparse
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Union

import torch
import torch.multiprocessing as mp
from datasets import load_dataset
from peft import LoraConfig, PeftModel, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling,
)

def prepare_dataset(batch, tokenizer, max_input_len=512, max_output_len=256):
    # Combine context + question into input
    input_texts = [
        f"Context: {c}\nQuestion: {q}" for c, q in zip(batch["context"], batch["question"])
    ]
    target_texts = batch["answer"]

    inputs = tokenizer(
        input_texts,
        truncation=True,
        padding="max_length",
        max_length=max_input_len,
    )
    outputs = tokenizer(
        target_texts,
        truncation=True,
        padding="max_length",
        max_length=max_output_len,
    )

    # Replace pad tokens in labels with -100
    labels = [
        [(l if l != tokenizer.pad_token_id else -100) for l in label_seq]
        for label_seq in outputs["input_ids"]
    ]

    batch["input_ids"] = inputs["input_ids"]
    batch["attention_mask"] = inputs["attention_mask"]
    batch["labels"] = labels

    return batch


class CustomTrainer(Trainer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loss_log = []

    def training_step(self, model, inputs, num_items_in_batch = None,):
        loss = super().training_step(model, inputs, num_items_in_batch,)
        if self.state.global_step % 50 == 0:
            self.loss_log.append((self.state.global_step, loss.item()))
            print(f"Step {self.state.global_step}: Loss = {loss.item()}")
        return loss


def main(args):
    mp.set_start_method("spawn", force=True)
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")

    if args.quantize == True:
        from transformers import BitsAndBytesConfig
        bnb_config = BitsAndBytesConfig(
            load_in_8bit=True, llm_int8_enable_fp32_cpu_offload=True
        )
    else:
        bnb_config = None

    model = AutoModelForCausalLM.from_pretrained(
        args.model_name_or_path, quantization_config=bnb_config, dtype=torch.float16
    ).to(device)

    tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path)

    dataset = load_dataset("b-mc2/sql-create-context")

    # Take a subset of the first 1000 examples
    dataset["train"] = dataset["train"].select(range(1000))
    dataset = dataset["train"].train_test_split(test_size=0.1)

    print("Preparing dataset...")
    dataset = dataset.map(
        lambda batch: prepare_dataset(batch, tokenizer),
        batched=True,
        remove_columns=dataset["train"].column_names,
    )

    model = prepare_model_for_kbit_training(model)
    config = LoraConfig(
        r=8,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, config)

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        learning_rate=args.learning_rate,
        num_train_epochs=args.num_epochs,
        fp16=True,
        per_device_eval_batch_size=args.batch_size,
        logging_steps=100,
        save_steps=1000,
        eval_steps=1000,
    )

    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer,mlm=False)  # causal LM, so no masking)

    trainer = CustomTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["test"],
        tokenizer=tokenizer,
        data_collator=data_collator,
    )

    trainer.train()
    trainer.save_model(args.output_dir)

    with open(os.path.join(args.output_dir, "loss_log.json"), "w") as f:
        json.dump(trainer.loss_log, f)


def inference(args):
    base_model = AutoModelForCausalLM.from_pretrained(
        args.model_name_or_path,
        dtype=torch.float16,
        device_map="cuda",
    )
    peft_model = PeftModel.from_pretrained(base_model, args.output_dir)
    merged_model = peft_model.merge_and_unload()
    merged_model = base_model

    tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path)

    context = "CREATE TABLE department (name STRING role STRING age INTEGER)"
    question = "SQL query for getting how many heads of the departments are older than 56 ?"

    input_text = (
        f"You are a SQL assistant. Output ONLY the SQL query. Do NOT add explanations, results, numbers, questions, or reasoning. Only SQL.\n\nContext: {context}\n Question: {question}\nAnswer: "
    )
    inputs = tokenizer(input_text, return_tensors="pt")
    inputs = {k: v.to("cuda") for k, v in inputs.items()}

    generated_ids = merged_model.generate(
        **inputs,
        max_new_tokens=128,
        do_sample=False,
        repetition_penalty=1.2,
        eos_token_id=tokenizer.eos_token_id
    )
    answer = tokenizer.decode(
        generated_ids[0][inputs['input_ids'].shape[1]:],
        skip_special_tokens=True
    )
    print(f"{input_text}{answer}")


if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)

    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name_or_path", type=str, default="Qwen/Qwen3-1.7B")
    parser.add_argument("--data_dir", type=str, required=True)
    parser.add_argument("--json_file", type=str, default="qa_dataset.json")
    parser.add_argument("--output_dir", type=str, default="./qa_output")
    parser.add_argument("--batch_size", type=int, default=2)
    parser.add_argument("--gradient_accumulation_steps", type=int, default=4)
    parser.add_argument("--learning_rate", type=float, default=1e-3)
    parser.add_argument("--num_epochs", type=int, default=3)
    parser.add_argument("--num_proc", type=int, default=1)
    parser.add_argument("--quantize", type=bool, default=False)
    parser.add_argument(
        "--mode", type=str, choices=["train", "inference"], default="train"
    )
    args = parser.parse_args()

    if args.mode == "train":
        main(args)
    elif args.mode == "inference":
        inference(args)

