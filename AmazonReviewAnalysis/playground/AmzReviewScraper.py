import requests
from bs4 import BeautifulSoup
import pandas as pd
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
from scipy.special import softmax
from googletrans import Translator
# exampleURL = 'https://www.amazon.com/Zephyrus-Display-GeForce-Windows-GA503QS-BS96Q/product-reviews/B0992VS1BY/ref=cm_cr_getr_d_paging_btm_prev_1?ie=UTF8&reviewerType=all_reviews&pageNumber='
maxLength = 30
global reviewList
reviewList = []
AveragePos = 0
AverageNeg = 0
AverageNeu = 0

pos_val = 0

neg_val = 0

neu_val = 0

pos_rev = ""
neg_rev = ""
neu_rev = ""

Averages = []
HighestReviews = []
Highest = []
translator = Translator()


def setUrl(urlGiven):
    global url
    url = urlGiven


def setNegVal(value):
    global neg_val
    neg_val = value


def setPosVal(value):
    global pos_val
    pos_val = value


def setNeuVal(value):
    global neu_val
    neu_val = value


def setPosRev(review):
    global pos_rev
    pos_rev = review


def setNegRev(review):
    global neg_rev
    neg_rev = review


def setNeuRev(review):
    global neu_rev
    neu_rev = review


def addAvgPos(value):
    global AveragePos
    AveragePos += value


def addAvgNeg(value):
    global AverageNeg
    AverageNeg += value


def addAvgNeu(value):
    global AverageNeu
    AverageNeu += value


def getSoup(url):
    r = requests.get('http://localhost:8050/render.html',
                     params={'url': url, 'wait': 2})
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup


def analyze(review, type):
    # PreProcess Tweet
    tweet_words = []

    for word in review.split(' '):
        if word.startswith('@') and len(word) > 1:
            word = "@user"
        elif word.startswith("http"):
            word = "http"
        tweet_words.append(word)
    tweet_proc = " ".join(tweet_words)

    # load model and tokenizer
    roberta = "cardiffnlp/twitter-roberta-base-sentiment"
    model = TFAutoModelForSequenceClassification.from_pretrained(roberta)

    # Convert review to numbers
    tokenizer = AutoTokenizer.from_pretrained(roberta)

    # Sentiment Analysis
    encoded_tweet = tokenizer(tweet_proc, return_tensors='tf')

    output = model(**encoded_tweet)

    scores = output[0][0].numpy()
    scores = softmax(scores)

    for i in range(len(scores)):
        if i == 0 and type == "Negative":
            addAvgNeg(scores[i])
            if scores[i] > neg_val:
                setNegVal(scores[i])
                setNegRev(review)
            return float(scores[i])
        if i == 1 and type == "Neutral":
            addAvgNeu(scores[i])
            if scores[i] > neu_val:
                setNeuVal(scores[i])
                setNeuRev(review)
            return float(scores[i])
        if i == 2 and type == "Positive":
            addAvgPos(scores[i])
            if scores[i] > pos_val:
                setPosVal(scores[i])
                setPosRev(review)
            return float(scores[i])


def getReviews(soup):

    reviews = soup.find_all('div',  {'data-hook': 'review'})
    try:
        for item in reviews:
            if (len(reviewList) < maxLength):
                print('LENGTH OF REVIEW LIST: ', len(reviewList))
                review = {
                    "Product": soup.title.text.replace('Amazon.com: Customer reviews: ', '').strip(),
                    "Title": translator.translate(item.find('a', {'data-hook': 'review-title'}).text.strip()[19:]).text,
                    "Rating": float(item.find('i', {'data-hook': 'review-star-rating'}).text.replace(' out of 5 stars', '').strip()),
                    "Body": translator.translate(item.find('span', {'data-hook': 'review-body'}).text.strip()).text,
                    "Positive-Score": analyze(translator.translate(item.find('span', {'data-hook': 'review-body'}).text.strip()).text, "Positive"),
                    "Negative-Score": analyze(translator.translate(item.find('span', {'data-hook': 'review-body'}).text.strip()).text, "Negative"),
                    "Neutral-Score": analyze(translator.translate(item.find('span', {'data-hook': 'review-body'}).text.strip()).text, "Neutral")
                }
                print(review)
                reviewList.append(review)
            else:
                break

    except:
        pass


def AmazonReviewAnalysis(url):
    if (len(str(url)) < 100):
        return {}
    Result = {}
    temp = url
    # temp = 'https://www.amazon.com/Zephyrus-Display-GeForce-Windows-GA503QS-BS96Q/product-reviews/B0992VS1BY/ref=cm_cr_getr_d_paging_btm_prev_1?ie=UTF8&reviewerType=all_reviews&pageNumber='
    for x in range(1, 8):
        if (len(reviewList) < maxLength):
            soupA = getSoup(
                f'{temp}{x}')

            getReviews(soupA)
            print(len(reviewList))
            if not soupA.find('li', {'class': 'a-disabled a-last'}) or (len(reviewList) > maxLength):
                pass
            else:
                break
        else:
            break
    avgPos = (float(AveragePos / (len(reviewList))))
    avgNeg = (float(AverageNeg / (len(reviewList))))
    avgNeu = (float(AverageNeu / (len(reviewList))))
    Result["Highest_Positive"] = (pos_val)
    Result['Highest_Negative'] = (neg_val)
    Result['Highest_Neutral'] = (neu_val)
    Result['Average_Positive'] = avgPos
    Result['Average_Negative'] = avgNeg
    Result['Average_Neutral'] = avgNeu
    Result['Highest_Positive_Rev'] = (pos_rev)
    Result['Highest_Negative_Rev'] = (neg_rev)
    Result['Highest_Neutral_Rev'] = (neu_rev)

    MaxVal = max(avgPos, avgNeg, avgNeu)
    if (MaxVal == avgPos):
        Result[
            'DisplayMessage'] = f"After the analysis the model has determined that this product is reccomended as it's average positive score is higher than the rest at a value of {avgPos}"
    elif (MaxVal == avgNeg):
        Result[
            'DisplayMessage'] = f"After the analysis the model has determined that this product is NOT reccomended as the average negative score is higher than the rest at a value of {avgNeg}"
    elif (MaxVal == avgNeu):
        Result[
            'DisplayMessage'] = f"After the analysis the model has determined that this product is neither reccomended or not reccomended, with a neutral score of {avgNeu} it seems you would be better off looking at the reviws of this same product on another website or trusing your gut feeling about this item."
    else:
        Result['DisplayMessage'] = f"Could not determine the next course of action for this product"
    ResultList = [].append(Result)
    df = pd.DataFrame(reviewList)
    df2 = pd.DataFrame(ResultList)
    df = df._append(df2, ignore_index=True)
    df.to_excel('testing123.xlsx', index=False)
    return Result


# AmazonReviewAnalysis(
#     'https://www.amazon.com/Zephyrus-Display-GeForce-Windows-GA503QS-BS96Q/product-reviews/B0992VS1BY/ref=cm_cr_getr_d_paging_btm_prev_1?ie=UTF8&reviewerType=all_reviews&pageNumber=')
