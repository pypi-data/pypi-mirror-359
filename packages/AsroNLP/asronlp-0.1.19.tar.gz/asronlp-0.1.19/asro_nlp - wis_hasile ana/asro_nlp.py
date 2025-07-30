import os
import pandas as pd
import time
import swifter
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.panel import Panel
import re
import nltk
from nltk.tokenize import word_tokenize
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud
import regex
import random

console = Console()

class AsroNLP:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))

        self.stopwords_path = os.path.join(base_dir, 'data', 'stopwords.txt')
        self.normalization_path = os.path.join(base_dir, 'data', 'kamuskatabaku.xlsx')
        self.news_dictionary_path = os.path.join(base_dir, 'data', 'news_dictionary.txt')
        self.root_words_path = os.path.join(base_dir, 'data', 'kata-dasar.original.txt')
        self.additional_root_words_path = os.path.join(base_dir, 'data', 'kata-dasar.txt')
        self.lexicon_positive_path = os.path.join(base_dir, 'data', 'kamus_positive.xlsx')
        self.lexicon_negative_path = os.path.join(base_dir, 'data', 'kamus_negative.xlsx')

        self.ensure_files_exist([
            self.stopwords_path,
            self.normalization_path,
            self.news_dictionary_path,
            self.root_words_path,
            self.additional_root_words_path,
            self.lexicon_positive_path,
            self.lexicon_negative_path
        ])

        nltk.download('punkt', quiet=True)
        self.stopwords = self.load_stopwords()
        self.normalization_dict = self.load_excel_dict(self.normalization_path)
        self.lexicon_positive_dict = self.load_excel_dict(self.lexicon_positive_path)
        self.lexicon_negative_dict = self.load_excel_dict(self.lexicon_negative_path)
        self.news_media = self.load_news_media()
        self.root_words = self.load_root_words()
        self.stemmer = StemmerFactory().create_stemmer()

    def ensure_files_exist(self, files):
        missing = [f for f in files if not os.path.exists(f)]
        if missing:
            raise FileNotFoundError(f"Missing required files: {missing}")

    def load_stopwords(self):
        with open(self.stopwords_path, 'r', encoding='utf-8') as f:
            return set(f.read().splitlines())

    def load_excel_dict(self, path):
        df = pd.read_excel(path, header=None, engine='openpyxl')
        dic = {}
        for k,v in zip(df[0].astype(str).str.lower(), df[1]):
            try:
                val = float(v)
                dic[k] = val
            except:
                pass
        return dic

    def load_news_media(self):
        with open(self.news_dictionary_path, 'r', encoding='utf-8') as f:
            return set(self.normalize_media_name(line.strip()) for line in f)

    def load_root_words(self):
        with open(self.root_words_path, 'r', encoding='utf-8') as f1, \
             open(self.additional_root_words_path, 'r', encoding='utf-8') as f2:
            return set(w.strip().lower() for w in f1).union(set(w.strip().lower() for w in f2))

    @staticmethod
    def normalize_media_name(name):
        if not isinstance(name, str):
            name = str(name) if name is not None else ''
        name = re.sub(r"[^\w\d\s.]", '', name)
        name = re.sub(r"\s+", ' ', name)
        return name.lower()

    @staticmethod
    def case_folding(text):
        if not isinstance(text, str):
            text = str(text) if text is not None else ''
        return text.lower()

    @staticmethod
    def clean_text_full(text):
        if not isinstance(text, str):
            text = str(text) if text is not None else ''
        text = text.lower()
        emoji_pattern = regex.compile(
            "[" 
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "\U00002700-\U000027BF"
            "\U0001F900-\U0001F9FF"
            "\U00002600-\U000026FF"
            "\U00002B00-\U00002BFF"
            "\U0001FA70-\U0001FAFF"
            "\U000025A0-\U000025FF"
            "]+", flags=regex.UNICODE)
        text = emoji_pattern.sub(' ', text)
        text = regex.sub(r'[^a-z\s]', ' ', text)
        text = regex.sub(r'\s+', ' ', text).strip()
        return text if text else None

    def clean_dataframe(self, df, text_column):
        total_before = len(df)
        df_unique = df.drop_duplicates(subset=[text_column]).copy()
        df_unique[text_column] = df_unique[text_column].astype(str).apply(self.clean_text_full)
        df_unique[text_column].replace('', pd.NA, inplace=True)
        df_cleaned = df_unique.dropna(subset=[text_column]).copy()

        # Filter lebih cerdas untuk kata satu huruf:
        def filter_row(text):
            words = text.split()
            single_char_counts = Counter([w for w in words if len(w) == 1])
            filtered_words = []
            for w in words:
                if len(w) == 1:
                    if single_char_counts[w] > 4:  # pertahankan jika lebih dari 4 kali
                        filtered_words.append(w)
                else:
                    filtered_words.append(w)
            return ' '.join(filtered_words)

        df_cleaned[text_column] = df_cleaned[text_column].apply(filter_row)

        # Hapus baris kosong setelah filter
        df_cleaned = df_cleaned[df_cleaned[text_column].str.strip() != ''].copy()
        df_cleaned.reset_index(drop=True, inplace=True)

        total_after = len(df_cleaned)
        removed = total_before - total_after
        percent_removed = removed / total_before * 100 if total_before > 0 else 0

        # Data yang di-drop
        df_removed = pd.concat([df_unique, df_cleaned]).drop_duplicates(keep=False)

        drop_out_path = 'drop_output.xlsx'
        df_removed.to_excel(drop_out_path, index=False)

        console.print(f"[bold yellow]Data cleaning info:[/bold yellow] Total awal: {total_before}, Bersih: {total_after}, Terbuang: {removed} ({percent_removed:.2f}%)")
        console.print(f"[bold yellow]Data terbuang disimpan di:[/bold yellow] {drop_out_path}")

        return df_cleaned

    @staticmethod
    def tokenize_text(text):
        if not isinstance(text, str):
            return []
        return word_tokenize(text)

    def remove_stopwords(self, tokens):
        return [t for t in tokens if t.isalpha() and len(t) > 1 and t not in self.stopwords]

    def normalize_text(self, tokens):
        return [self.normalization_dict.get(t, t) for t in tokens]

    def sentiment_analysis(self, tokens):
        score = 0
        pos_words = []
        neg_words = []
        for w in tokens:
            if not isinstance(w, str):
                continue
            w = w.lower()
            pos_score = self.lexicon_positive_dict.get(w)
            neg_score = self.lexicon_negative_dict.get(w)
            if isinstance(pos_score, (int, float)):
                score += pos_score
                pos_words.append(w)
            if isinstance(neg_score, (int, float)):
                score += neg_score
                neg_words.append(w)
        if score > 0:
            sentiment = 'Positive'
        elif score < 0:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'
        return {'Sentiment': sentiment, 'Positive_Words': ', '.join(pos_words), 'Negative_Words': ', '.join(neg_words)}

    def detect_source_type(self, source_id):
        if not isinstance(source_id, str):
            return 'Individual'
        norm = self.normalize_media_name(source_id)
        return 'Media' if any(media in norm for media in self.news_media) else 'Individual'

    def process_dataframe(self, df):
        text_col = 'full_text' if 'full_text' in df.columns else 'comment'
        df[text_col] = df[text_col].fillna('').astype(str)

        with Progress(console=console) as progress:
            task = progress.add_task("[cyan]Processing text...", total=len(df))

            df['Case_Folded_Text'] = df[text_col].apply(self.case_folding)
            progress.update(task, advance=1)

            df['Tokens'] = df[text_col].apply(self.tokenize_text)
            progress.update(task, advance=1)

            df['Filtered_Tokens'] = df['Tokens'].apply(self.remove_stopwords)
            progress.update(task, advance=1)

            df['Normalized_Text'] = df['Filtered_Tokens'].apply(self.normalize_text)
            progress.update(task, advance=1)

            df['Stemmed_Text'] = df['Normalized_Text'].swifter.apply(lambda tokens: self.stem_and_display(tokens))
            progress.update(task, advance=1)

            df['Sentiment_Results'] = df['Stemmed_Text'].apply(self.sentiment_analysis)
            progress.update(task, advance=1)

            df['Sentiment'] = df['Sentiment_Results'].apply(lambda x: x['Sentiment'])
            df['Positive_Words'] = df['Sentiment_Results'].apply(lambda x: x['Positive_Words'])
            df['Negative_Words'] = df['Sentiment_Results'].apply(lambda x: x['Negative_Words'])

        col = 'channel_title' if 'channel_title' in df.columns else 'username' if 'username' in df.columns else None
        if col is None:
            raise ValueError("DataFrame must have 'channel_title' or 'username' column")
        df['Source_Type'] = df.apply(lambda x: self.detect_source_type(x[col]), axis=1)
        return df

    def stem_and_display(self, tokens):
        console.log(f"[bold yellow]Tokens before stemming: {tokens}[/bold yellow]")
        stemmed = [self.stemmer.stem(t) for t in tokens]
        console.log(f"[bold green]Tokens after stemming: {stemmed}[/bold green]")
        return stemmed

    def visualize_dashboard_console(self, df):
        t_sentiment = Table(title="Sentiment Counts")
        t_sentiment.add_column("Sentiment")
        t_sentiment.add_column("Count", justify="right")
        for s, c in df['Sentiment'].value_counts().items():
            t_sentiment.add_row(s, str(c))

        t_source = Table(title="Source Type Counts")
        t_source.add_column("Source Type")
        t_source.add_column("Count", justify="right")
        for s, c in df['Source_Type'].value_counts().items():
            t_source.add_row(s, str(c))

        df['Category'] = df.apply(lambda x: f"{x['Sentiment']} - {x['Source_Type']}", axis=1)
        t_category = Table(title="Sentiment by Source Type")
        t_category.add_column("Category")
        t_category.add_column("Count", justify="right")
        for s, c in df['Category'].value_counts().items():
            t_category.add_row(s, str(c))

        console.print(Panel(t_sentiment))
        console.print(Panel(t_source))
        console.print(Panel(t_category))

    def visualize_dashboard_graphics(self, df):
        sentiment_colors = {
            'Positive': '#2ca02c',  # green
            'Negative': '#d62728',  # red
            'Neutral': '#ff7f0e'    # orange
        }

        sentiment_counts = df['Sentiment'].value_counts()
        total_sentiments = sentiment_counts.sum()
        sentiment_percentages = (sentiment_counts / total_sentiments * 100).round(1)
        colors = [sentiment_colors.get(s, '#7f7f7f') for s in sentiment_counts.index]

        source_counts = df['Source_Type'].value_counts()
        total_source = source_counts.sum()
        source_percentages = (source_counts / total_source * 100).round(1)

        df['Category'] = df.apply(lambda x: f"{x['Sentiment']} - {x['Source_Type']}", axis=1)
        category_counts = df['Category'].value_counts()

        fig1, axs1 = plt.subplots(1, 3, figsize=(20, 6))
        fig1.suptitle('Dashboard Sentimen dan Distribusi Sumber', fontsize=18)

        # Pie chart Sentiment dengan kotak total di tengah
        wedges, texts, autotexts = axs1[0].pie(
            sentiment_counts,
            labels=[f"{s} ({sentiment_counts[s]}, {sentiment_percentages[s]}%)" for s in sentiment_counts.index],
            autopct='%1.1f%%',
            colors=colors,
            startangle=140,
            pctdistance=0.75,
            textprops={'fontsize': 12, 'weight': 'bold', 'color': 'white'}
        )
        axs1[0].set_title(f'Sentiment Distribution', fontsize=14)
        axs1[0].axis('equal')

        bbox_props = dict(boxstyle="round,pad=0.7", fc="lightgrey", ec="black", lw=1)
        axs1[0].text(0, 0, f"Total\n{total_sentiments}", ha='center', va='center', fontsize=18, weight='bold', bbox=bbox_props)

        # Bar chart Source Type dengan nilai dan persentase di dalam batang
        bars = axs1[1].bar(
            source_counts.index,
            source_counts.values,
            color=['#1f77b4', '#ffbb78'][:len(source_counts)],
            edgecolor='black'
        )
        axs1[1].set_title('Source Type Distribution', fontsize=14)
        axs1[1].set_xlabel('Source Type')
        axs1[1].set_ylabel('Count')
        axs1[1].set_ylim(0, max(source_counts.values) * 1.2)

        for idx, bar in enumerate(bars):
            height = bar.get_height()
            val = source_counts.values[idx]
            pct = source_percentages.values[idx]
            axs1[1].text(bar.get_x() + bar.get_width() / 2, height / 2,
                         f"{val}\n({pct}%)", ha='center', va='center', fontsize=12, weight='bold', color='white')

        # Barh chart Sentiment by Source Type dengan nilai dan persen di tengah batang
        bars = axs1[2].barh(
            category_counts.index,
            category_counts.values,
            color=[sentiment_colors.get(s.split()[0], '#7f7f7f') for s in category_counts.index],
            edgecolor='black'
        )
        axs1[2].set_title('Sentiment by Source Type', fontsize=14)
        axs1[2].set_xlabel('Count')
        axs1[2].set_xlim(0, max(category_counts.values) * 1.2)

        for idx, bar in enumerate(bars):
            width = bar.get_width()
            val = category_counts.values[idx]
            pct = round(val / total_sentiments * 100, 1)
            axs1[2].text(width / 2, bar.get_y() + bar.get_height() / 2,
                         f'{val}\n({pct}%)', ha='center', va='center', fontsize=12, weight='bold', color='white')

        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.show()

        # Halaman 2: WordCloud dan Bar Frekuensi Kata per Sentimen (tanpa header bar)
        categories = ['Positive', 'Negative', 'Neutral']
        fig2, axs2 = plt.subplots(3, 2, figsize=(18, 18))
        fig2.suptitle('WordCloud dan Frekuensi Kata per Sentimen', fontsize=18)

        for i, cat in enumerate(categories):
            tokens = [t for words in df[df['Sentiment'] == cat]['Filtered_Tokens'] for t in words]
            if not tokens:
                axs2[i, 0].axis('off')
                axs2[i, 1].axis('off')
                continue
            text = ' '.join(tokens)

            # Wordcloud
            wc = WordCloud(width=600, height=400, background_color='white', colormap='tab10').generate(text)
            axs2[i, 0].imshow(wc, interpolation='bilinear')
            axs2[i, 0].axis('off')
            axs2[i, 0].set_title(f'{cat} Sentiment WordCloud', fontsize=16)

            # Bar chart frekuensi kata (top 10), warna random tapi tetap
            counts = Counter(tokens).most_common(10)
            if counts:
                words, freqs = zip(*counts)
                total_words = sum(freqs)

                colors_bar = list(plt.cm.tab20.colors)
                random.shuffle(colors_bar)
                colors_bar = colors_bar[:len(words)]

                axs2[i, 1].bar(words, freqs, color=colors_bar, edgecolor='black')
                axs2[i, 1].tick_params(axis='x', rotation=45)
                axs2[i, 1].set_ylim(0, max(freqs) * 1.2)

                for idx, freq in enumerate(freqs):
                    axs2[i, 1].text(idx, freq + total_words * 0.01, f'{freq}', ha='center', va='bottom', fontsize=12, weight='bold')

        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.show()

    def preprocess_and_analyze(self, input_path, output_path="output.xlsx"):
        try:
            df = pd.read_excel(input_path, engine='openpyxl')

            if 'full_text' in df.columns:
                text_col = 'full_text'
            elif 'comment' in df.columns:
                text_col = 'comment'
            else:
                raise ValueError("Data harus memiliki kolom 'full_text' (Twitter) atau 'comment' (YouTube)")

            df = self.clean_dataframe(df, text_column=text_col)

            start = time.time()
            df = self.process_dataframe(df)
            end = time.time()

            console.print(f"Processing time: {end - start:.2f} seconds")
            self.visualize_dashboard_console(df)
            self.visualize_dashboard_graphics(df)

            df.to_excel(output_path, index=False, engine='openpyxl')
            console.print(f"[bold green]Data saved to {output_path}[/bold green]")

        except Exception as e:
            console.print(f"[bold red]Error: {e}[/bold red]")
