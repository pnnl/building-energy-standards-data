import argparse
import json
import os

import torch
import torch.multiprocessing as mp
from datasets import load_dataset
from peft import LoraConfig, get_peft_model
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)


def prepare_dataset(batch, tokenizer, max_input_len=512, max_output_len=128):
    input_texts = [
        f"Translate the following question to a single correct SQL query given this context. Output ONLY the SQL query ending with a semicolon (;). Do NOT include explanations, comments, or extra SQL statements.\n\nContext: {c}\nQuestion: {q}"
        for c, q in zip(batch["context"], batch["question"])
    ]
    target_texts = batch["answer"]

    inputs = tokenizer(input_texts, max_length=max_input_len, truncation=True)
    labels = tokenizer(
        target_texts, max_length=max_output_len, truncation=True
    ).input_ids

    # Replace pad tokens with -100 for loss calculation
    labels = [
        [l if l != tokenizer.pad_token_id else -100 for l in seq] for seq in labels
    ]

    ignored_ratio = sum(l == -100 for seq in labels for l in seq) / sum(
        len(seq) for seq in labels
    )
    print(f"Average % of ignored tokens: {ignored_ratio:.3f}")

    inputs["labels"] = labels

    return inputs


class CustomTrainer(Seq2SeqTrainer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loss_log = []
        self._logged_steps = set()

    def training_step(self, model, inputs, num_items_in_batch=None):
        # Compute loss
        loss = super().training_step(model, inputs, num_items_in_batch)
        step = self.state.global_step

        # Print loss every batch
        print(f"[Batch] Global Step {step}: Loss = {loss.item()}")

        # Log every 50 steps
        if step % 50 == 0 and step not in self._logged_steps:
            self._logged_steps.add(step)
            self.loss_log.append((step, loss.item()))
            print(f"=== Step {step} summary: Loss = {loss.item()} ===")

        # Gradient accumulation logging
        if self.args.gradient_accumulation_steps > 1:
            if (step + 1) % self.args.gradient_accumulation_steps == 0:
                print(f"[Grad Accum Completed] Step {step}")

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
            load_in_8bit=True,
            quantization_config=bnb_config,
            llm_int8_enable_fp32_cpu_offload=True,
        )
    else:
        bnb_config = None

    model = AutoModelForSeq2SeqLM.from_pretrained(
        args.model_name_or_path,
        torch_dtype=torch.float16,
    ).to(device)

    tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path)

    dataset = load_dataset(args.dataset_name_or_path)

    # Take a subset of the first 1000 examples
    # dataset["train"] = dataset["train"].select(range(1000))

    dataset = dataset["train"].train_test_split(test_size=0.1)

    print("Preparing dataset...")
    dataset = dataset.map(
        lambda batch: prepare_dataset(batch, tokenizer),
        batched=True,
        remove_columns=dataset["train"].column_names,
    )

    config = LoraConfig(
        r=8,
        lora_alpha=32,
        target_modules=["q", "v"],
        lora_dropout=0.05,
        bias="none",
        task_type="SEQ_2_SEQ_LM",
    )
    model = get_peft_model(model, config)

    training_args = Seq2SeqTrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        learning_rate=args.learning_rate,
        num_train_epochs=args.num_epochs,
        fp16=False,
        per_device_eval_batch_size=args.batch_size,
        eval_strategy="steps",
        logging_steps=5,
        save_steps=15,
        eval_steps=15,
        predict_with_generate=True,  # now supported
    )

    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model, padding=True)

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
    model.save_pretrained(args.output_dir + "-withAdapter")

    with open(os.path.join(args.output_dir, "loss_log.json"), "w") as f:
        json.dump(trainer.loss_log, f)


def inference(args):
    base_model = args.model_name_or_path
    finetuned_model = args.output_dir

    model = AutoModelForSeq2SeqLM.from_pretrained(
        base_model,
        dtype=torch.float32,
        device_map="mps",
    )

    tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path)
    tokenizer.model_max_length = 1024

    context = """"CREATE TABLE hvac_minimum_requirements_furnaces_90_1
        (id INTEGER PRIMARY KEY, 
        template TEXT NOT NULL,
        equipment_type TEXT NOT NULL,
        fuel_type TEXT NOT NULL,
        electric_power_phase NUMERIC,
        minimum_capacity NUMERIC,
        maximum_capacity NUMERIC,
        minimum_combo_unit_cooling_capacity NUMERIC,
        maximum_combo_unit_cooling_capacity NUMERIC,
        subtype TEXT,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        minimum_annual_fuel_utilization_efficiency NUMERIC,
        minimum_thermal_efficiency NUMERIC,
        minimum_combustion_efficiency NUMERIC,
        standby_mode_power NUMERIC,
        off_mode_power NUMERIC,
        annotation TEXT)"""
    question = """what afue is required for a 150 kbtu / hr natural turf field installed in 2018?"""

    input_text = f"Translate the following question to a single correct SQL query given this context. Output ONLY the SQL query ending with a semicolon (;). Do NOT include explanations, comments, or extra SQL statements.\n\n Context: {context}\n Question: {question}"
    inputs = tokenizer(input_text, return_tensors="pt").to("mps")

    generated_ids = model.generate(
        **inputs,
        max_new_tokens=512,
        repetition_penalty=1.2,
        eos_token_id=tokenizer.eos_token_id,
    )

    answer = tokenizer.decode(generated_ids[0], skip_special_tokens=True)

    print(f"\n\n{input_text}\nAnswer:{answer}")


if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)

    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name_or_path", type=str, default="google/flan-t5-xl")
    parser.add_argument(
        "--dataset_name_or_path", type=str, default="b-mc2/sql-create-context"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./fine_tuning/output/flan-t5-output-withAdapter",
    )
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--gradient_accumulation_steps", type=int, default=4)
    parser.add_argument("--learning_rate", type=float, default=1e-4)
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
