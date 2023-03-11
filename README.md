## Setup

You'll need to install [CRFSuite](http://www.chokkan.org/software/crfsuite/) on your system to generate and use the CRF models in this project.

Optionally, you could instead use [CRF++](http://taku910.github.io/crfpp/), but you will have to modify the bash scripts in ```bin/```, specifically ```bin/train-model```, ```bin/parse-ingredients``` and ```bin/parse-products``` to use CRF++ instead.

Training and tagging is done by converting annotations and input into CRF++ format as an intermediate step, so all you'll need to do is remove the command that converts from CRF++ to CRFSuite format, and use CRF++ to train and tag instead.

Specifically, these lines are of interest:
```bash
pipenv run python bin/crfpp_to_crfsuite.py 
crfsuite tag ... 
crfsuite train ... 
```

You may also need to mess with ```bin/read_results.py```, as CRFSuite only outputs tags, and not the items which were tagged (as opposed to CRF++, which outputs items and respective tag simultaneously).

# Current pipelines:

These instructions assume that you are using CRFSuite. If you're using CRF++, sorry - some of these might need some additional work.


## Training a model:
1. Pick an annotations file (e.g. "data/annotations/annotated-ingredients.json")
2. Pick an output model location (e.g. "models/ingredients.crfmodel")
3. Set these environment variables respectively
e.g.
```bash
ANNOTATIONS_FILE="data/annotations/annotated-ingredients.json"
MODEL_FILE="models/nyt-ingredients.crfmodel"
```
4. Train the model
```bash
bin/train-model "$ANNOTATION_FILE" "$MODEL_FILE"
```

The ``` bin/train-model ``` script does these things in sequence:
1. Converts the annotations to an intermediate CRF++ friendly format.
2. Converts this intermediate format to a CRFSuite friendly format.
3. Uses CRFSuite to train a model on the data in the CRFSuite friendly format.


## Parsing ingredients

1. Pick a model that you've previously trained on ingredient annotations (e.g. "models/ingredients.crfmodel")
2. Put all of your desired ingredients in a .txt file, separated by a newline.
This will look like:
```
1 cup plain flour
250g shallots, diced finely
500mL beef stock
Salt, to taste (optional)
```
3. Run ```bin/parse-ingredients``` with your model file and ingredients file specified in the following order:
```bash
bin/parse-ingredients "models/ingredients.crfmodel" "ingredients.txt" > "output.json"
```

The output is a json file with the parsed ingredients, as well as the probability given by the model for these particular tags.

```json
{"prob": 0.983397, "QTY": ["1"], "UNIT": ["cup"], "VARIANT": ["plain"], "NAME": ["flour"]}
```

## Scraping and parsing products

1. Run ```pipenv run python scraping/coles.py```. This scrapes the Coles website for products listed online, and dumps the data into ```data/products.json```.
2. Pick a model that you've previously trained on product annotations (e.g. "models/product.crfmodel")
3. Run ```bin/parse-products``` with your model file and ```data/products.json``` specified in the following order:
```bash
bin/parse-products "models/products.crfmodel" "data/products.json" > "parsed-products.json"
``` 

This process generats a json file identical to the scraped products json file, with the addition of tags for that product and the probability of that tag as given by the model. 


## Creating a product metric space

This step takes a .csv file filled with triplets that are then used to train a metric learning algorithm. This generates a lower-dimensional vector space that can express the similarities between products in a more space-efficient way. 

[Metric Learning @ metric-learn](http://contrib.scikit-learn.org/metric-learn/introduction.html)

[Similarity learning @ Wikipedia](https://en.wikipedia.org/wiki/Similarity_learning)

We are using triplets instead of annotated singles or pairs. This is because we assume that products can fit in multiple classes (which are super- or sub-sets of each other e.g. meat, beef, beef + burger, beef + sausage), and that we have no way to specify the similarity directly between two items.

Using triplets allow us to define the similarity measure using comparisons between products relatively:

> Beef Sausage is closer to Beef than Greek Yoghurt

instead of:

> Beef Sausage is 0.28494 close to Beef

---




# Todo

- [ ] Add more annotations
- [ ] Convert from ingredient tags to the product metric space
- [ ] Parse an entire recipe and identify cost per serving