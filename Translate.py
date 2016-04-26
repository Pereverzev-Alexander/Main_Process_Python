#!/usr/bin/python
# -*- coding: utf-8 -*-
from yandex_translate import YandexTranslate, YandexTranslateException

translate = YandexTranslate("trnsl.1.1.20160405T010910Z.5a7444dd2ae85b52.bf17409a50ae429fed0d1452e5c39f79b0d3090a")


def translateString(text):
    language = translate.detect(text)
    if language == 'en':
        return translate.translate(text, 'ru')['text']
    elif language == 'ru':
        return translate.translate(text, 'en')['text']
    else:
        print('Not eng or rus text!')