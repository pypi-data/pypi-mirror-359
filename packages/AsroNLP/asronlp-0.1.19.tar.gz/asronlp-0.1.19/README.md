# AsroNLP

**AsroNLP** adalah paket Natural Language Processing (NLP) khusus untuk pengolahan teks Bahasa Indonesia. Paket ini menyediakan fitur preprocessing lengkap seperti pembersihan teks, tokenisasi, normalisasi, stemming, serta analisis sentimen berbasis kamus leksikon positif dan negatif.

---

## Fitur Utama

- Pembersihan teks dari emoji, angka, simbol, URL, mention, dan duplikat data
- Tokenisasi teks Bahasa Indonesia menggunakan NLTK
- Penghapusan stopwords Bahasa Indonesia
- Normalisasi kata menggunakan kamus kata baku
- Stemming dengan algoritma Sastrawi
- Analisis sentimen dengan kamus leksikon positif dan negatif
- Deteksi sumber komentar (Media atau Individual)
- Visualisasi hasil analisis: distribusi sentimen, wordcloud, dan frekuensi kata
- Mendukung data dari YouTube (`comment`) dan Twitter (`full_text`)

---

## Instalasi

Instalasi paket AsroNLP beserta dependensinya dapat dilakukan dengan:

```bash
pip install asronlp
pip install asronlp==0.1.19

Contoh
from asro_nlp import AsroNLP

nlp = AsroNLP()
nlp.preprocess_and_analyze('data/input_data.xlsx', 'data/output_result.xlsx')
