from flask import Flask, request
from flask_restful import Resource, Api
from flask_jsonpify import jsonify

from estnltk import Text
from estnltk.vabamorf.morf import synthesize

app = Flask(__name__)
api = Api(app)


class Interpreter(Resource):
    def get(self):
        text = Text(request.args.get("text"))
        text.tag_layer(['ner', 'timexes'])

        named_entities = []
        named_entity_labels = []
        named_entity_spans = []
        for named_entity in text.ner:
            named_entities.append(" ".join(["|".join(set(word.lemma)) for word in named_entity]))
            named_entity_labels.append(named_entity["nertag"])
            named_entity_spans.append([named_entity.start, named_entity.end])

        timexes = []
        for timex in text.timexes:
            timexes.append(
                {
                    "text": timex.enclosing_text,
                    "tid": timex["tid"],
                    "type": timex["type"],
                    "value": timex["value"]
                }
            )

        words = []
        lemmas = []
        forms = []
        word_texts = []

        for ma in text.morph_analysis:
            analysis = []
            for annotation in ma.annotations:
                analysis.append(
                    {
                        "lemma": annotation.lemma,
                        "form": annotation.form,
                        "partofspeech": annotation.partofspeech
                    }
                )
            words.append(
                {"text": ma.text, "start": ma.start, "analysis": analysis}
            )

            lemmas.append("|".join(set(ma.lemma)))
            forms.append("|".join(set(ma.form)))
            word_texts.append(ma.enclosing_text)

        result = {
            'words': words,
            'lemmas': lemmas,
            'forms': forms,
            'word_texts': word_texts,
            'timexes': timexes,
            'named_entities': named_entities,
            'named_entity_labels': named_entity_labels,
            'named_entity_spans': named_entity_spans
        }

        return jsonify(result)


class Generator(Resource):
    def get(self):
        lemma = request.args.get('lemma')
        form = request.args.get('form')
        return self.generate(lemma, form)

    @staticmethod
    def generate(lemma, form):
        return synthesize(lemma, form)


api.add_resource(Interpreter, '/parse')
api.add_resource(Generator, '/generate')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
