## MODELS

**There are two tasks in our project**

* Bitcoin Price prediction according sentiment score, trends, comment counts, previous days closing price.
* Topic Modelling to find out Topics people are talking under different market situations.

**First task involves two-stage**

* Sentiment score generating based on fine-tuning BERT. (Model1a)
* Bitcoin Price prediction according sentiment score, trends, comment counts, previous days closing price. (Model1b)

 **Second task: Topic Modelling**

- Build a LDA model using whole comments data to get a overview  on this task.

* Based on overview observation, divided whole data set into 4 years(2017-2020) respectively, fine tuning the model (stop-words, bigram, model metrics...)
* Fine the best number of topics for each year.
* Generating the most popular views, related comments.
* Summarize instruction tips for bitcoin traders. 
