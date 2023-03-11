Current pipelines:


Training a model:
1) Pick an annotations file ("data/annotations/annotated-product-02-28-23-20-08-06.json")
2) Pick an output model location ("models/nyt-ingredients.crfmodel")
3) Set these environment variables respectively
e.g.    ANNOTATIONS_FILE="data/annotations/annotated-product-02-28-23-20-08-06.json"
        MODEL_FILE="models/nyt-ingredients.crfmodel"
4) Train the model
bin/train-model "$ANNOTATION_FILE" "$MODEL_FILE"