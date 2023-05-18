import torch
from torch.nn import functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
model_name = 'cardiffnlp/twitter-roberta-base-sentiment'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name).to(device)


# Preprocess text (username and link placeholders)
def preprocess(text):
    new_text = []

    for t in text.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)


# tweet = "I like using the new transformers library!"

def find_sentiment(tweet):
    tweet = preprocess(tweet)
    inputs = tokenizer(tweet, return_tensors='pt', truncation=True, max_length=512).to(device)
    outputs = model(**inputs)

    probs = F.softmax(outputs.logits, dim=-1)
    sentiment = ['Negative', 'Neutral', 'Positive']
    result = sentiment[probs.argmax().item()]

    max_prob, max_index = torch.max(probs, dim=1)

    return result, max_prob.item()
