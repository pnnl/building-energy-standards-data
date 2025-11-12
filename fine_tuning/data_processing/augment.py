import random
import numpy as np
import torch
import pandas as pd
import nlpaug.augmenter.word as naw
import nltk

SEED = 42

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False

nltk.download("averaged_perceptron_tagger_eng")

INPUT_FILE = "fine_tuning/dataset/processed/questions_with_context.csv"
OUTPUT_FILE = "fine_tuning/dataset/final/augmented_questions_with_context.csv"

# Polite/filler insertion
polite_words = ["please", "kindly", "could you", "would you"]


def insert_polite(text):
    polite_word = random.choice(polite_words)
    if random.random() < 0.5:
        # Add at start
        return polite_word + " " + text
    else:
        # Add at end
        return text.rstrip("?") + ", " + polite_word + "?"


def augment(dataset_path, output_path=None):
    # Synonym replacement using WordNet
    question_aug = naw.SynonymAug(aug_src="wordnet", aug_p=0.1)

    # Contextual paraphrasing
    para_aug = naw.ContextualWordEmbsAug(
        model_path="bert-base-uncased", action="substitute", aug_p=0.1
    )

    df = pd.read_csv(dataset_path)

    augmenters = [para_aug, insert_polite]
    augmented_rows = []

    for _, row in df.iterrows():
        # Original
        augmented_rows.append(
            {
                "question": row["question"],
                "answer": row["answer"],
                "context": row["context"],
            }
        )

        num_aug = random.randint(1, 4)  # 1 to 4 augmentations

        for _ in range(num_aug):
            # Pick a random augmenter from the list
            aug = random.choice(augmenters)

            if isinstance(aug, naw.Augmenter):
                q_aug = aug.augment(row["question"])
                if isinstance(q_aug, list):
                    q_aug = q_aug[0]
            else:
                q_aug = aug(row["question"])

            augmented_rows.append(
                {"question": q_aug, "answer": row["answer"], "context": row["context"]}
            )

    aug_df = pd.DataFrame(augmented_rows)

    if output_path:
        aug_df.to_csv(output_path, index=False)
        print(f"Saved augmented data to {output_path}")

    return aug_df


if __name__ == "__main__":
    augment(INPUT_FILE, OUTPUT_FILE)
