import string
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords

# Download stopwords safely
try:
    stop_words = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords")
    stop_words = set(stopwords.words("english"))


def clean_text(text):
    if not text:
        return ""

    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    words = text.split()
    words = [word for word in words if word not in stop_words]

    return " ".join(words)


# 🎯 Job Match Score
def calculate_similarity_score(job_desc, resume_text):

    documents = [job_desc, resume_text]
    documents = [clean_text(doc) for doc in documents]

    if all(doc.strip() == "" for doc in documents):
        return 0

    tfidf = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=5000
    )

    matrix = tfidf.fit_transform(documents)
    score = cosine_similarity(matrix[0:1], matrix[1:2]).flatten()[0]

    return round(score * 100, 2)


# 📊 ATS Resume Score
def calculate_ats_score(resume_text):

    resume_text = resume_text.lower()

    ats_keywords = [
        "education",
        "experience",
        "skills",
        "projects",
        "internship",
        "certifications",
        "summary",
        "objective"
    ]

    score = 0

    # Keyword match score (70%)
    keyword_count = sum(1 for word in ats_keywords if word in resume_text)
    keyword_score = (keyword_count / len(ats_keywords)) * 70

    # Resume length score (30%)
    word_count = len(resume_text.split())

    if word_count >= 400:
        length_score = 30
    elif word_count >= 250:
        length_score = 20
    else:
        length_score = 10

    score = keyword_score + length_score

    return round(score, 2)