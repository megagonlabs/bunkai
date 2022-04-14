
# Training of lbd (Linebreak Disambiguator)

## Install dependences

```console
poetry install --no-root -E lb -E train
```

## Preparation BCCWJ without newspaper texts

```bash
unzip ~/bccwj/disk.3/CORE_OT/core_M-XML.zip -d ~/data/3rd/bccwj/ver.1.1/core_nonumtrans_mxml/
poetry run python3 -m bunkai.experiment.convert.bccwj -i ~/data/3rd/bccwj/ver.1.1/core_nonumtrans_mxml/core_M-XML -o ~/data/bccwj/files/

mkdir -p ~/data/bccwj/lbd
poetry run python3 -m bunkai.experiment.statics -i ~/data/bccwj/files -o ~/data/bccwj/lbd/stat.bccwj.jsonl

# Generate data
find ~/data/bccwj/files -type f | grep -v PN | sort | xargs cat | poetry run python3 -m bunkai.algorithm.lbd.corpus -o ~/data/bccwj/lbd/source-without-pn.jsonl
poetry run python3 -m bunkai.algorithm.lbd.corpus -i ~/data/bccwj/lbd/source-without-pn.jsonl -o ~/data/bccwj/lbd/split --split
```

### Train with BERT

```bash
poetry run make lbd
```

### Train with DistliBERT

```bash
poetry run make lbd \
    LBD_MODEL_DIR=~/data/bccwj/model/lbd-distlibert-model \
    LBD_MODEL_NAME=bandainamco-mirai/distilbert-base-japanese
```
