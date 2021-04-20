
BCCWJ_DATA_DIR:=~/data/bccwj/files
BCCWJ_GOLD:=$(BCCWJ_DATA_DIR).without-pn.txt
$(BCCWJ_GOLD): $(BCCWJ_DATA_DIR)
	find $< -type f | grep -v PN | sort | xargs cat \
	    | poetry run python3 -m bunkai.experiment.evaluate --trim -i /dev/stdin -o $@
VANILLA_MODEL_DIR:=~/data/bccwj/model-vanilla
VANILLA_TEST:=$(VANILLA_MODEL_DIR)/test.prediction
$(VANILLA_TEST): $(BCCWJ_GOLD)
	mkdir -p $(dir $@) \
	&& sed "s/│//g" $(BCCWJ_GOLD) | poetry run bunkai > $@
VANILLA_TEST_TRIM:=$(VANILLA_MODEL_DIR)/test.prediction.trim
$(VANILLA_TEST_TRIM): $(VANILLA_TEST)
	poetry run python3 -m bunkai.experiment.evaluate --trim -i $< -o $@

VANILLA_TEST_EVAL:=$(VANILLA_MODEL_DIR)/test.score.jsonl
$(VANILLA_TEST_EVAL): $(VANILLA_TEST_TRIM)
	python3 -m bunkai.experiment.evaluate -i $< -g $(BCCWJ_GOLD) -o $@
vanilla-test: $(VANILLA_TEST_EVAL)

