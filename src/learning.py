import os
import glob
from transformers import TFGPT2LMHeadModel, AutoTokenizer
import tensorflow as tf

class AILearner:
    """
    AIの学習とモデル管理を行うクラス
    """
    def __init__(self, model_name="rinna/japanese-gpt2-small", model_dir="models"):
        self.model_name = model_name
        self.model_dir = model_dir
        self.model_path = os.path.join(self.model_dir, "fine_tuned")
        self.model = None
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        # Add a padding token if it doesn't exist
        if self.tokenizer.pad_token is None:
            self.tokenizer.add_special_tokens({'pad_token': '[PAD]'})

        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)

    def fine_tune(self, data_path, epochs=3, batch_size=2):
        """
        指定されたデータでモデルをファインチューニングする
        """
        print("Loading and preparing dataset...")
        text_files = glob.glob(os.path.join(data_path, "*.txt"))
        if not text_files:
            print("No data found to train on. Please run 'research' first.")
            return

        full_text = ""
        for file in text_files:
            with open(file, "r", encoding="utf-8") as f:
                full_text += f.read()

        tokenized_text = self.tokenizer.encode(full_text)

        # Create input/output pairs for training
        examples = []
        block_size = 128  # Max sequence length for the model
        for i in range(0, len(tokenized_text) - block_size + 1, block_size):
            examples.append(tokenized_text[i:i + block_size])

        if not examples:
            print("Not enough text data to create training examples. Need more conversation history.")
            return

        inputs, labels = [], []
        for ex in examples:
            inputs.append(ex[:-1])
            labels.append(ex[1:])

        dataset = tf.data.Dataset.from_tensor_slices((inputs, labels))
        dataset = dataset.shuffle(len(examples)).batch(batch_size, drop_remainder=True)

        print("Loading pre-trained model...")
        model = TFGPT2LMHeadModel.from_pretrained(self.model_name)
        model.resize_token_embeddings(len(self.tokenizer))

        optimizer = tf.keras.optimizers.Adam(learning_rate=5e-5)
        loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
        model.compile(optimizer=optimizer, loss=loss)

        print(f"Starting fine-tuning for {epochs} epochs...")
        model.fit(dataset, epochs=epochs)

        print("Fine-tuning finished. Saving model...")
        self.save_model(model)

    def predict(self, text, max_length=50):
        """
        入力テキストに対して応答を生成する
        """
        if self.model is None:
            self.load_model()

        if self.model is None:
            return "モデルが読み込まれていません。先に 'learning' コマンドを実行してください。"

        input_ids = self.tokenizer.encode(text, return_tensors='tf')

        # モデルによる応答生成
        output_sequences = self.model.generate(
            input_ids=input_ids,
            max_length=max_length,
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            early_stopping=True,
            pad_token_id=self.tokenizer.pad_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
        )

        # 生成されたテキストのデコード
        generated_text = self.tokenizer.decode(output_sequences[0], skip_special_tokens=True)

        return generated_text

    def load_model(self):
        """
        学習済みモデルを読み込む
        """
        print(f"Loading model from {self.model_path}")
        if os.path.exists(self.model_path):
            self.model = TFGPT2LMHeadModel.from_pretrained(self.model_path)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            print("Model loaded successfully.")
        else:
            print("No fine-tuned model found. Please run 'learning' first.")

    def save_model(self, model):
        """
        モデルを保存する
        """
        model.save_pretrained(self.model_path)
        self.tokenizer.save_pretrained(self.model_path)
        print(f"Model saved to {self.model_path}")