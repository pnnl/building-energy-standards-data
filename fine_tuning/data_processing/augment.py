import pandas as pd
import nlpaug.augmenter.word as naw
import nltk
import random

nltk.download('averaged_perceptron_tagger_eng')

# Synonym replacement using WordNet
question_aug = naw.SynonymAug(aug_src='wordnet', aug_p=0.1)

# Contextual paraphrasing
para_aug = naw.ContextualWordEmbsAug(
    model_path='bert-base-uncased',
    action='substitute',
    aug_p=0.1
)

# Polite/filler insertion
polite_words = ["please", "kindly", "could you", "would you"]
def insert_polite(text):
    polite_word = random.choice(["please", "kindly", "could you", "would you"])
    if random.random() < 0.5:
        # Add at start
        return polite_word + " " + text
    else:
        # Add at end
        return text.rstrip("?") + ", " + polite_word + "?"

df = pd.read_csv("fine_tuning/dataset/processed/questions_with_context.csv")

augmenters = [para_aug, insert_polite]
augmented_rows = []

for _, row in df.iterrows():
    # Original
    augmented_rows.append({
        'question': row['question'],
        'answer': row['answer'],
        'context': row['context']
    })

    num_aug = random.randint(1, 4)  # 1 to 4 augmentations

    for _ in range(num_aug):
        # Pick a random augmenter from the list
        aug = random.choice(augmenters)

        if isinstance(aug, naw.Augmenter):
            q_aug = aug.augment(row['question'])
            if isinstance(q_aug, list):
                q_aug = q_aug[0]
        else:
            q_aug = aug(row['question'])

        augmented_rows.append({
            'question': q_aug,
            'answer': row['answer'],
            'context': row['context']
        })

aug_df = pd.DataFrame(augmented_rows)
aug_df.to_csv("fine_tuning/dataset/processed/augmented_questions_with_context.csv", index=False)
print("Saved augmented data to augmented_questions_with_context.csv")