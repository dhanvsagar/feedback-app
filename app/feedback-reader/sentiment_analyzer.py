from textblob import TextBlob

def analyze_sentiment(text):
    # Simple sentiment analysis - returns positive, negative, or neutral
    if not text or text.strip() == '':
        return 'neutral'
    
    try:
        blob = TextBlob(str(text))
        polarity = blob.sentiment.polarity
        
        if polarity > 0:
            return 'positive'
        elif polarity < 0:
            return 'negative'
        else:
            return 'neutral'
    except:
        return 'neutral'