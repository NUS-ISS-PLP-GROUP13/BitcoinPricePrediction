import torch

print("init start..")
# If there's a GPU available...
if torch.cuda.is_available():

    # Tell PyTorch to use the GPU.
    device = torch.device("cuda")

    print('There are %d GPU(s) available.' % torch.cuda.device_count())

    print('We will use the GPU:', torch.cuda.get_device_name(0))

# If not...
else:
    print('No GPU available, using the CPU instead.')
    device = torch.device("cpu")


from torch.utils.data import TensorDataset, random_split,SequentialSampler,DataLoader
import pandas as pd


from transformers import BertForSequenceClassification, AdamW, BertConfig

# Load BertForSequenceClassification, the pretrained BERT model with a single
# linear classification layer on top.
model = BertForSequenceClassification.from_pretrained(
    "bert-base-uncased", # Use the 12-layer BERT model, with an uncased vocab.
    num_labels = 2, # The number of output labels--2 for binary classification.
                    # You can increase this for multi-class tasks.
    output_attentions = False, # Whether the model returns attentions weights.
    output_hidden_states = False, # Whether the model returns all hidden-states.
)

# Tell pytorch to run this model on the GPU.
# model.cuda()

optimizer = AdamW(model.parameters(),
                  lr = 2e-5, # args.learning_rate - default is 5e-5, our notebook had 2e-5
                  eps = 1e-8 # args.adam_epsilon  - default is 1e-8.
                )

from transformers import BertTokenizer

output_file = "D:\workspace\python\Bit_coin\Controller\Model1\.model_bert_ft_bitcoin.pth"

checkpoint = torch.load(output_file, map_location='cpu')
model.load_state_dict(checkpoint['model_state_dict'])
optimizer.load_state_dict(checkpoint['optimizer_state_dict'])


# bitcoin = pd.read_csv("D:\\workspace\\python\\Bit_coin\\Controller\\Model1\\2017-1-9.csv",
#                  header=0,  usecols=[8, 9] )
#
# print(bitcoin.shape)
#
# print(bitcoin.head())
#
# print('Number of test sentences: {:,}\n'.format(bitcoin.shape[0]))
#
# bitcoin_sentence = bitcoin.update_Comments
#
# print(bitcoin_sentence.shape)
#
# print(bitcoin_sentence[0])

import numpy as np

# bitcoin_sentence = bitcoin_sentence[0:10]
#
# print(bitcoin_sentence)
# print(type(bitcoin_sentence))



def score(model, bitcoin_sentence):
    bitcoin_sentence = bitcoin_sentence.replace(np.nan, "")
    from transformers import BertTokenizer

    # Load the BERT tokenizer.
    print('Loading BERT tokenizer...')
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)
    # Tokenize all of the sentences and map the tokens to thier word IDs.
    input_ids = []
    attention_masks = []

    # For every sentence...
    for sent in bitcoin_sentence:
        encoded_dict = tokenizer.encode_plus(
            sent,  # Sentence to encode.
            add_special_tokens=True,  # Add '[CLS]' and '[SEP]'
            max_length=64,  # Pad & truncate all sentences.
            truncation=True,
            padding='max_length',
            return_attention_mask=True,  # Construct attn. masks.
            return_tensors='pt',  # Return pytorch tensors.
        )

        # Add the encoded sentence to the list.
        input_ids.append(encoded_dict['input_ids'])

        # And its attention mask (simply differentiates padding from non-padding).
        attention_masks.append(encoded_dict['attention_mask'])

    # Convert the lists into tensors.
    input_ids = torch.cat(input_ids, dim=0)
    attention_masks = torch.cat(attention_masks, dim=0)
    # labels_test = torch.tensor(labels_test)

    # Set the batch size.
    batch_size = 32

    # Create the DataLoader.
    prediction_data = TensorDataset(input_ids, attention_masks)
    prediction_sampler = SequentialSampler(prediction_data)
    prediction_dataloader = DataLoader(prediction_data, batch_size=batch_size)

    # Prediction on test set

    print('Predicting labels for {:,} test sentences...'.format(len(input_ids)))

    # Put model in evaluation mode
    model.eval()

    # Tracking variables
    predictions, true_labels = [], []

    # Predict
    for batch in prediction_dataloader:
        # Add batch to GPU
        batch = tuple(t.to(device) for t in batch)

        # Unpack the inputs from our dataloader
        b_input_ids, b_input_mask = batch

        # Telling the model not to compute or store gradients, saving memory and
        # speeding up prediction
        with torch.no_grad():
            # Forward pass, calculate logit predictions
            outputs = model(b_input_ids, token_type_ids=None,
                            attention_mask=b_input_mask)

        logits = outputs[0]

        # Move logits and labels to CPU
        logits = logits.detach().cpu().numpy()
        # label_ids = b_labels.to('cpu').numpy()

        # Store predictions and true labels
        predictions.append(logits)
        # true_labels.append(label_ids)

    print('    DONE.')

    def softmax(x):
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum(axis=0)  # only difference

    i = 0
    score = []
    for p in predictions:
        for ind in p:
            score.append(softmax(ind))

    def score_sentiment(score):
        sentiment_score = []
        for s in score:
            if (s[0] > s[1]):
                sentiment_score.append(-s[0])
            else:
                sentiment_score.append(s[1])
        return sentiment_score

    sentiment_score = score_sentiment(score)

    return sum(sentiment_score) / len(sentiment_score)

# testy = score(model, bitcoin_sentence)
#
# print(testy)
