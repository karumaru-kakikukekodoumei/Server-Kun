import os
import sys
import requests
import bz2
from gensim.corpora import WikiCorpus
from tqdm import tqdm
import tensorflow as tf
from transformers import AutoTokenizer, TFGPT2LMHeadModel

from pyknp import Juman

class WikipediaTrainer:
    def __init__(self, base_model_name="rinna/japanese-gpt2-small", new_model_dir="models/wikipedia_base"):
        self.base_model_name = base_model_name
        self.new_model_dir = new_model_dir
        self.data_dir = "AI/data"
        self.wiki_dump_path = os.path.join(self.data_dir, "jawiki-latest-pages-articles.xml.bz2")
        self.wiki_text_path = os.path.join(self.data_dir, "wiki_jp.txt")
        self.wiki_wakati_path = os.path.join(self.data_dir, "wiki_jp_wakati.txt")

        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.new_model_dir, exist_ok=True)

        try:
            self.juman = Juman()
        except Exception as e:
            print(f"Warning: Failed to initialize Juman++. Morphological analysis will be skipped.")
            print(f"Make sure Juman++ is installed and in your PATH. Error: {e}")
            self.juman = None

    def download_wikipedia_dump(self):
        """
        日本語Wikipediaの最新ダンプをダウンロードする
        """
        if os.path.exists(self.wiki_dump_path):
            print("Wikipedia dump already exists. Skipping download.")
            return

        url = "https://dumps.wikimedia.org/jawiki/latest/jawiki-latest-pages-articles.xml.bz2"
        print(f"Downloading Wikipedia dump from {url} ... (This may take a very long time)")

        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                with open(self.wiki_dump_path, 'wb') as f, tqdm(
                    total=total_size, unit='iB', unit_scale=True, desc="jawiki-dump"
                ) as pbar:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        pbar.update(len(chunk))
            print("Download complete.")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download Wikipedia dump: {e}")
            sys.exit(1)

    def extract_and_clean_text(self):
        """
        ダンプファイルからテキストを抽出し、整形する
        """
        if os.path.exists(self.wiki_text_path):
            print("Cleaned Wikipedia text already exists. Skipping extraction.")
            return

        print("Extracting and cleaning text from Wikipedia dump... (This may also take a while)")

        # gensimのWikiCorpusはファイル名を渡すと自動でbzip2を展開してくれる
        wiki = WikiCorpus(self.wiki_dump_path, lemmatize=False, dictionary={})

        count = 0
        with open(self.wiki_text_path, 'w', encoding='utf-8') as output_file:
            # tqdmを使って進捗を表示
            with tqdm(total=sum(1 for _ in wiki.get_texts()), desc="Extracting articles") as pbar:
                for text in wiki.get_texts():
                    article = " ".join(text)
                    output_file.write(article + "\n")
                    count += 1
                    pbar.update(1)

        print(f"Finished extracting {count} articles to {self.wiki_text_path}")

    def add_bot_description(self):
        """
        学習データにBOT自身の仕様説明を追加する
        """
        print("Adding bot description to the training data...")

        bot_description = """
このボット「AI-KUN」は、サーバーの会話から学習し、ユーザーと自然な対話を行うAIです。
以下に主な機能とコマンドを示します。

【コマンドラインコマンド】
- research: サーバーの会話履歴をすべて収集し、学習用データを作成します。
- learning: 収集したデータを使ってAIを追加学習させます。

【ディスコードコマンド】
- !AI-KUN Run: AIを起動し、このチャンネルでの対話を開始します。
- !AI-KUN Stop: AIの動作を一時的に停止します。
- !AI-KUN NO: このチャンネルでAIが反応しないように設定します。

AIは定期的に最新の会話を学習し、賢くなっていきます。
"""
        try:
            with open(self.wiki_text_path, 'r+', encoding='utf-8') as f:
                content = f.read()
                f.seek(0, 0)
                f.write(bot_description.strip() + '\n\n' + content)
            print("Bot description added successfully.")
        except IOError as e:
            print(f"Error adding bot description: {e}")
            sys.exit(1)

    def morphological_analysis(self):
        """
        Juman++を使ってテキストを分かち書きする
        """
        if self.juman is None:
            print("Skipping morphological analysis because Juman++ is not available.")
            print(f"Copying {self.wiki_text_path} to {self.wiki_wakati_path} as a fallback.")
            try:
                import shutil
                shutil.copyfile(self.wiki_text_path, self.wiki_wakati_path)
            except IOError as e:
                print(f"Error copying file: {e}")
                sys.exit(1)
            return

        if os.path.exists(self.wiki_wakati_path):
            print("Wakati text file already exists. Skipping morphological analysis.")
            return

        print("Performing morphological analysis... (This will take an extremely long time)")
        try:
            with open(self.wiki_text_path, 'r', encoding='utf-8') as f_in, \
                 open(self.wiki_wakati_path, 'w', encoding='utf-8') as f_out:

                total_lines = sum(1 for line in f_in)
                f_in.seek(0) # ファイルポインタを先頭に戻す

                with tqdm(total=total_lines, desc="Analyzing sentences") as pbar:
                    for line in f_in:
                        line = line.strip()
                        if line:
                            result = self.juman.analysis(line)
                            wakati_text = " ".join(mrph.midasi for mrph in result.mrph_list())
                            f_out.write(wakati_text + "\n")
                        pbar.update(1)
            print(f"Finished morphological analysis. Output: {self.wiki_wakati_path}")
        except Exception as e:
            print(f"An error occurred during morphological analysis: {e}")
            sys.exit(1)

    def train_model(self, epochs=1, batch_size=2):
        """
        整形済みデータでベースモデルを追加学習する
        """
        if os.path.exists(os.path.join(self.new_model_dir, "tf_model.h5")):
            print("Pre-trained Wikipedia model already exists. Skipping training.")
            return

        print("Starting training on Wikipedia data...")

        print("Loading tokenizer and model...")
        tokenizer = AutoTokenizer.from_pretrained(self.base_model_name)
        model = TFGPT2LMHeadModel.from_pretrained(self.base_model_name)

        if tokenizer.pad_token is None:
            tokenizer.add_special_tokens({'pad_token': '[PAD]'})
            model.resize_token_embeddings(len(tokenizer))

        print("Loading and preparing dataset...")
        try:
            with open(self.wiki_wakati_path, 'r', encoding='utf-8') as f:
                full_text = f.read()
        except FileNotFoundError:
            print(f"Error: Processed data file not found at {self.wiki_wakati_path}. Please run the data preparation steps first.")
            sys.exit(1)

        tokenized_text = tokenizer.encode(full_text)

        examples = []
        block_size = 128
        for i in range(0, len(tokenized_text) - block_size + 1, block_size):
            examples.append(tokenized_text[i:i + block_size])

        if not examples:
            print("Not enough text data to create training examples.")
            return

        inputs, labels = [], []
        for ex in examples:
            inputs.append(ex[:-1])
            labels.append(ex[1:])

        dataset = tf.data.Dataset.from_tensor_slices((inputs, labels))
        dataset = dataset.shuffle(len(examples)).batch(batch_size, drop_remainder=True)

        optimizer = tf.keras.optimizers.Adam(learning_rate=5e-5)
        loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
        model.compile(optimizer=optimizer, loss=loss)

        print(f"Starting fine-tuning for {epochs} epoch(s)...")
        model.fit(dataset, epochs=epochs)

        print("Training finished. Saving new base model...")
        model.save_pretrained(self.new_model_dir)
        tokenizer.save_pretrained(self.new_model_dir)
        print(f"New base model saved to {self.new_model_dir}")

    def run_full_pipeline(self):
        """
        データ準備から学習までの全パイプラインを実行する
        """
        self.download_wikipedia_dump()
        self.extract_and_clean_text()
        self.add_bot_description()
        self.morphological_analysis()
        self.train_model()
        print("Base model training complete.")

if __name__ == "__main__":
    trainer = WikipediaTrainer()
    trainer.run_full_pipeline()