
LBD_DATA_DIR:=~/data/bccwj/lbd/split

# $LBD_MODEL_DIR:=~/data/bccwj/model/lbd-distlibert-model
# LBD_MODEL_NAME:=bandainamco-mirai/distilbert-base-japanese

LBD_MODEL_DIR:=~/data/bccwj/model/lbd-bert-model
LBD_MODEL_NAME:=cl-tohoku/bert-base-japanese-whole-word-masking
LBD_TRAIN_OPT:=

LBD_INPUT_TRAIN:=$(LBD_DATA_DIR)/train.jsonl
LBD_INPUT_TEST:=$(LBD_DATA_DIR)/test.txt
LBD_OUTPUT_MODEL:=$(LBD_MODEL_DIR)/out/pytorch_model.bin
$(LBD_OUTPUT_MODEL): $(LBD_INPUT_TRAIN)
	poetry run python3 -m bunkai.algorithm.lbd.train \
		-i $(LBD_INPUT_TRAIN) -m $(LBD_MODEL_DIR)\
		--base $(LBD_MODEL_NAME) $(LBD_TRAIN_OPT)
lbd-train: $(LBD_OUTPUT_MODEL)
$(LBD_MODEL_DIR)/test.prediction: $(LBD_OUTPUT_MODEL)  $(LBD_INPUT_TEST)
	sed "s/│//g" $(LBD_INPUT_TEST) \
	| poetry run python3 -m bunkai.algorithm.lbd.predict \
		-m $(LBD_MODEL_DIR)/out -b 10 > $@
$(LBD_MODEL_DIR)/test.score.jsonl: $(LBD_MODEL_DIR)/test.prediction $(LBD_INPUT_TEST)
	python3 -m bunkai.experiment.evaluate --lb -i $< -g $(LBD_INPUT_TEST) > $@
lbd-test: $(LBD_MODEL_DIR)/test.score.jsonl
lbd: lbd-train lbd-test

