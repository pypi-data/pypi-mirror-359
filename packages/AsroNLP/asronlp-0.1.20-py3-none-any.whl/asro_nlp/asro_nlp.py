import os
import pandas as pd
import time
import swifter
from rich.console import Console
from rich.progress import Progress
from rich.panel import Panel
from rich.table import Table
import re
import nltk
from nltk.tokenize import word_tokenize
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from collections import Counter
import regex
import random
from wordcloud import WordCloud
import matplotlib.pyplot as plt

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
        for k, v in zip(df[0].astype(str).str.lower(), df[1]):
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

        def filter_row(text):
            words = text.split()
            single_char_counts = Counter([w for w in words if len(w) == 1])
            filtered_words = []
            for w in words:
                if len(w) == 1:
                    if single_char_counts[w] <= 4:
                        filtered_words.append(w)
                else:
                    filtered_words.append(w)
            return ' '.join(filtered_words)

        df_cleaned[text_column] = df_cleaned[text_column].apply(filter_row)
        df_cleaned[text_column].replace('', pd.NA, inplace=True)
        df_cleaned = df_cleaned.dropna(subset=[text_column]).copy()
        df_cleaned.reset_index(drop=True, inplace=True)

        total_after = len(df_cleaned)
        removed = total_before - total_after
        percent_removed = removed / total_before * 100 if total_before > 0 else 0

        df_removed = pd.concat([df_unique, df_cleaned]).drop_duplicates(keep=False)
        df_removed.to_excel('drop_output.xlsx', index=False)

        console.print(f"[bold yellow]Data cleaning info:[/bold yellow] Total awal: {total_before}, Bersih: {total_after}, Terbuang: {removed} ({percent_removed:.2f}%)")
        console.print(f"[bold yellow]Data terbuang disimpan di:[/bold yellow] drop_output.xlsx")

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

    def stem_and_display(self, tokens):
        console.log(f"[bold yellow]Tokens before stemming: {tokens}[/bold yellow]")
        stemmed = [self.stemmer.stem(t) for t in tokens]
        console.log(f"[bold green]Tokens after stemming: {stemmed}[/bold green]")
        return stemmed

    def process_dataframe(self, df):
        text_col = 'full_text' if 'full_text' in df.columns else 'comment' if 'comment' in df.columns else None
        if text_col is None:
            raise ValueError("DataFrame must have 'full_text' or 'comment' column")

        df[text_col] = df[text_col].fillna('').astype(str)

        with Progress(console=console) as progress:
            task = progress.add_task("[cyan]Processing text...", total=7)

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

            before_dropdup = len(df)
            df.drop_duplicates(subset=['Stemmed_Text'], inplace=True)
            after_dropdup = len(df)
            console.print(f"[yellow]Drop duplicates after stemming: {before_dropdup} -> {after_dropdup}[/yellow]")

            df.dropna(subset=['Stemmed_Text'], inplace=True)
            df.reset_index(drop=True, inplace=True)

            df['Sentiment_Results'] = df['Stemmed_Text'].apply(self.sentiment_analysis)
            df['Sentiment'] = df['Sentiment_Results'].apply(lambda x: x['Sentiment'])
            df['Positive_Words'] = df['Sentiment_Results'].apply(lambda x: x['Positive_Words'])
            df['Negative_Words'] = df['Sentiment_Results'].apply(lambda x: x['Negative_Words'])
            progress.update(task, advance=1)

            col = 'channel_title' if 'channel_title' in df.columns else 'username' if 'username' in df.columns else None
            if col is None:
                raise ValueError("DataFrame must have 'channel_title' or 'username' column")

            df['Source_Type'] = df.apply(lambda x: self.detect_source_type(x[col]), axis=1)

        console.print(f"[green]Columns after processing: {df.columns.tolist()}[/green]")
        console.print(f"[green]Sentiment distribution: {df['Sentiment'].value_counts().to_dict()}[/green]")

        return df

    def add_relevance_column(self, df):
        df['Relevance'] = df['Sentiment'].apply(lambda s: 'Relevant' if s in ['Positive', 'Negative'] else 'Not Relevant')
        return df

    def print_statistic_report(self, df_original, df_cleaned, df_processed, waktu_proses):
        total_awal = len(df_original)
        col_text = [col for col in ['full_text', 'comment'] if col in df_original.columns][0]
        duplikat = df_original.duplicated(subset=[col_text]).sum()
        dibuang = total_awal - len(df_cleaned)
        bersih = len(df_cleaned)

        sentiment_counts = df_processed['Sentiment'].value_counts()
        total_sentiment = sentiment_counts.sum()
        sentiment_percent = (sentiment_counts / total_sentiment * 100).round(2)

        source_counts = df_processed['Source_Type'].value_counts()
        total_source = source_counts.sum()
        source_percent = (source_counts / total_source * 100).round(2)

        relevance_counts = df_processed['Relevance'].value_counts()
        total_relevance = relevance_counts.sum()
        relevance_percent = (relevance_counts / total_relevance * 100).round(2)

        console.print(Panel.fit(f"""
[bold red]Laporan Statistik Data dan Sentimen[/bold red]

Total data awal           : {total_awal}
Data duplikat             : {duplikat}
Data dibuang (dropout)    : {dibuang} ({(dibuang / total_awal * 100) if total_awal else 0:.2f}%)
Data bersih setelah cleaning: {bersih}

-- Distribusi Sentimen --
Positive : {sentiment_counts.get('Positive',0)} ({sentiment_percent.get('Positive',0):.2f}%)
Negative : {sentiment_counts.get('Negative',0)} ({sentiment_percent.get('Negative',0):.2f}%)
Neutral  : {sentiment_counts.get('Neutral',0)}  ({sentiment_percent.get('Neutral',0):.2f}%)

-- Distribusi Sumber --
Media      : {source_counts.get('Media',0)} ({source_percent.get('Media',0):.2f}%)
Individual : {source_counts.get('Individual',0)} ({source_percent.get('Individual',0):.2f}%)

-- Distribusi Relevansi --
Relevant     : {relevance_counts.get('Relevant',0)} ({relevance_percent.get('Relevant',0):.2f}%)
Not Relevant : {relevance_counts.get('Not Relevant',0)} ({relevance_percent.get('Not Relevant',0):.2f}%)

Waktu proses analisis: {waktu_proses:.2f} detik
""", title="Statistik Lengkap", style="bold white on dark_blue"))

    def preprocess_and_analyze(self, input_path, output_path="output.xlsx"):
        try:
            df = pd.read_excel(input_path, engine='openpyxl')

            if 'full_text' in df.columns:
                text_col = 'full_text'
            elif 'comment' in df.columns:
                text_col = 'comment'
            else:
                raise ValueError("Data harus memiliki kolom 'full_text' (Twitter) atau 'comment' (YouTube)")

            df_cleaned = self.clean_dataframe(df, text_column=text_col)

            start = time.time()
            df_processed = self.process_dataframe(df_cleaned)
            df_processed = self.add_relevance_column(df_processed)
            end = time.time()

            self.print_statistic_report(df, df_cleaned, df_processed, end - start)

            self.visualize_dashboard_console(df_processed)
            self.visualize_dashboard_graphics(df_processed)

            df_processed.to_excel(output_path, index=False, engine='openpyxl')
            console.print(f"[bold green]Data saved to {output_path}[/bold green]")

            return df_processed

        except Exception as e:
            console.print(f"[bold red]Error: {e}[/bold red]")
            return None

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

        t_relevance = Table(title="Relevance Counts")
        t_relevance.add_column("Relevance")
        t_relevance.add_column("Count", justify="right")
        for s, c in df['Relevance'].value_counts().items():
            t_relevance.add_row(s, str(c))

        df['Category'] = df.apply(lambda x: f"{x['Sentiment']} - {x['Source_Type']}", axis=1)
        t_category = Table(title="Sentiment by Source Type")
        t_category.add_column("Category")
        t_category.add_column("Count", justify="right")
        for s, c in df['Category'].value_counts().items():
            t_category.add_row(s, str(c))

        console.print(Panel(t_sentiment))
        console.print(Panel(t_source))
        console.print(Panel(t_relevance))
        console.print(Panel(t_category))

    def visualize_dashboard_graphics(self, df):
        sentiment_colors = {
            'Positive': '#2ca02c',
            'Negative': '#d62728',
            'Neutral': '#ff7f0e'
        }
        source_colors = {
            'Individual': '#1f77b4',
            'Media': '#ffbb78'
        }
        relevance_colors = {
            'Relevant': '#1f77b4',
            'Not Relevant': '#ff7f0e'
        }

        sentiment_counts = df['Sentiment'].value_counts()
        total_sentiments = sentiment_counts.sum()
        sentiment_percentages = (sentiment_counts / total_sentiments * 100).round(1)
        colors = [sentiment_colors.get(s, '#7f7f7f') for s in sentiment_counts.index]

        source_counts = df['Source_Type'].value_counts()
        total_source = source_counts.sum()
        source_percentages = (source_counts / total_source * 100).round(1)

        relevance_counts = df['Relevance'].value_counts()
        total_relevance = relevance_counts.sum()
        relevance_percentages = (relevance_counts / total_relevance * 100).round(1)
        relevance_colors_list = [relevance_colors.get(s, '#7f7f7f') for s in relevance_counts.index]

        df['Category'] = df.apply(lambda x: f"{x['Sentiment']} - {x['Source_Type']}", axis=1)
        category_counts = df['Category'].value_counts()
        total_category = category_counts.sum()

        fig = plt.figure(figsize=(14, 10))
        fig.suptitle('Dashboard Sentimen dan Analisis Kata', fontsize=16, y=0.98)

        ax1 = plt.subplot2grid((4, 6), (0, 0), colspan=2)
        wedges, texts, autotexts = ax1.pie(
            sentiment_counts,
            labels=[f"{s} ({sentiment_counts[s]}, {sentiment_percentages[s]}%)" for s in sentiment_counts.index],
            autopct='%1.1f%%',
            colors=colors,
            startangle=140,
            pctdistance=0.75,
            textprops={'fontsize': 8, 'weight': 'normal', 'color': 'black'}
        )
        ax1.set_title('Distribusi Sentimen', fontsize=12)
        ax1.axis('equal')
        ax1.text(0, 0, f"Total\n{total_sentiments}", ha='center', va='center', fontsize=12)

        ax3 = plt.subplot2grid((4, 6), (0, 4), colspan=2)
        wedges2, texts2, autotexts2 = ax3.pie(
            relevance_counts,
            labels=[f"{s} ({relevance_counts[s]}, {relevance_percentages[s]}%)" for s in relevance_counts.index],
            autopct='%1.1f%%',
            colors=relevance_colors_list,
            startangle=140,
            pctdistance=0.75,
            textprops={'fontsize': 8, 'weight': 'normal', 'color': 'black'}
        )
        ax3.set_title('Distribusi Relevansi', fontsize=12)
        ax3.axis('equal')
        ax3.text(0, 0, f"Total\n{total_relevance}", ha='center', va='center', fontsize=12)

        ax2 = plt.subplot2grid((4, 6), (0, 2), colspan=2)
        bars = ax2.bar(
            source_counts.index,
            source_counts.values,
            color=[source_colors[s] for s in source_counts.index],
            edgecolor='black',
            width=0.6
        )
        ax2.set_title('Distribusi Jenis Sumber', fontsize=12)
        ax2.set_xlabel('Jenis Sumber', fontsize=10)
        ax2.set_ylabel('Jumlah', fontsize=10)
        ax2.set_ylim(0, max(source_counts.values) * 1.2)
        ax2.tick_params(axis='x', labelsize=9)
        ax2.tick_params(axis='y', labelsize=9)
        for idx, bar in enumerate(bars):
            height = bar.get_height()
            val = source_counts.values[idx]
            pct = source_percentages.values[idx]
            ax2.text(bar.get_x() + bar.get_width() / 2, height / 2,
                     f"{val}\n({pct}%)", ha='center', va='center', fontsize=8, color='black')

        ax4 = plt.subplot2grid((4, 6), (1, 0), colspan=6)
        bars = ax4.barh(
            category_counts.index,
            category_counts.values,
            color=[sentiment_colors.get(s.split()[0], '#7f7f7f') for s in category_counts.index],
            edgecolor='black',
            height=0.6
        )
        ax4.set_title('Sentimen menurut Jenis Sumber', fontsize=12)
        ax4.set_xlabel('Jumlah', fontsize=10)
        ax4.set_xlim(0, max(category_counts.values) * 1.2)
        ax4.tick_params(axis='x', labelsize=9)
        ax4.tick_params(axis='y', labelsize=9)
        for idx, bar in enumerate(bars):
            width = bar.get_width()
            val = category_counts.values[idx]
            pct = round(val / total_category * 100, 1)
            ax4.text(width / 2, bar.get_y() + bar.get_height() / 2,
                     f'{val} ({pct}%)', ha='center', va='center', fontsize=8, color='black')

        categories = ['Positive', 'Negative', 'Neutral']
        for i, cat in enumerate(categories):
            row = 2
            col = i * 2
            ax_wc = plt.subplot2grid((4, 6), (row, col), colspan=2)
            ax_bar = plt.subplot2grid((4, 6), (row + 1, col), colspan=2)

            tokens = [t for words in df[df['Sentiment'] == cat]['Filtered_Tokens'] for t in words]
            if not tokens:
                ax_wc.axis('off')
                ax_bar.axis('off')
                continue
            text = ' '.join(tokens)

            wc = WordCloud(width=300, height=200, background_color='white', colormap='tab10').generate(text)
            ax_wc.imshow(wc, interpolation='bilinear')
            ax_wc.axis('off')
            ax_wc.set_title(f'WordCloud {cat}', fontsize=11)

            counts = Counter(tokens).most_common(5)
            if counts:
                words, freqs = zip(*counts)

                colors_bar = list(plt.cm.tab20.colors)
                random.shuffle(colors_bar)
                colors_bar = colors_bar[:len(words)]

                ax_bar.bar(words, freqs, color=colors_bar, edgecolor='black')
                ax_bar.tick_params(axis='x', rotation=45, labelsize=9)
                ax_bar.tick_params(axis='y', labelsize=9)
                ax_bar.set_ylim(0, max(freqs) * 1.2)
                ax_bar.set_title(f'Frekuensi Kata Top 5 - {cat}', fontsize=11)

                for idx, freq in enumerate(freqs):
                    ax_bar.text(idx, freq + 0.5, f'{freq}', ha='center', fontsize=8)

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.subplots_adjust(top=0.92, hspace=0.45)
        plt.show()
