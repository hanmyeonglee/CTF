from transformers import GPT2Tokenizer, GPT2LMHeadModel, Trainer, TrainingArguments
from datasets import load_dataset

# 1. 데이터 로드 및 전처리
dataset = load_dataset("wikitext", "wikitext-2-raw-v1")  # 예제 데이터로 위키텍스트 사용
tokenizer = GPT2Tokenizer.from_pretrained("gpt2-medium")

# 모델이 EOS 토큰을 사용하는 방식에 맞추기 위해 padding 및 EOS 토큰 설정
tokenizer.pad_token = tokenizer.eos_token

def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=128)

tokenized_datasets = dataset.map(tokenize_function, batched=True, remove_columns=["text"])

# 2. 모델 불러오기
model = GPT2LMHeadModel.from_pretrained("gpt2-medium")

# 3. 훈련 설정
training_args = TrainingArguments(
    output_dir="./results",
    overwrite_output_dir=True,
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    weight_decay=0.01,
    per_device_train_batch_size=1,  # GPU 메모리가 6GB일 경우 낮은 배치 사이즈가 필요
    per_device_eval_batch_size=1,
    num_train_epochs=3,
    save_strategy="epoch",
    fp16=True  # 16비트 훈련으로 메모리 사용량 절감
)

# 4. Trainer 정의
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["validation"],
)

# 5. 훈련 시작
trainer.train()
