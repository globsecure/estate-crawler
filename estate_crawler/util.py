# coding=utf-8
from scrapy.selector import Selector
from scrapy.http.response.html import HtmlResponse
from htmllaundry import strip_markup
from urllib.parse import urlparse


class Structure:
    @staticmethod
    def find_in_definition(html, targetElement, targetText, indexOffset = 1):
        if not isinstance(html, Selector):
            html = Selector(html)

        matchedIndex = 'not found'
        elements = html.css(targetElement)
        elements.extract()

        for index, element in enumerate(elements):
            text = Extractor.string(element)
            if index == matchedIndex:
                return text

            if text.lower() == targetText.lower():
                matchedIndex = index + indexOffset


class Extractor:
    @staticmethod
    def euro(html, cssSelector='*') -> float:
        data = Extractor.string(html, cssSelector)

        # Flip dot and comma, remove euro sign
        data = data.replace('.', '').replace(',', '.').replace('€', '')

        # We remove other words
        words = data.strip().split(' ')
        data = words[0]

        # If we created a string ending with a . append a zero so float conversion is predictable
        if (data.endswith('.')):
            data += '0'

        return float(data)

    @staticmethod
    def string(html, cssSelector='*') -> str:
        if isinstance(html, str):
            return strip_markup(html).strip()

        if not isinstance(html, Selector):
            html = Selector(html)

        data = html.css(cssSelector).extract_first()
        if data is None:
            data = str('')

        data = strip_markup(data)
        return data.strip()

    @staticmethod
    def volume(html, cssSelector='*') -> float:
        string = Extractor.string(html, cssSelector)

        # Flip dot and comma, remove square meters from string
        volume_string = string.split('m')[0]
        volume_string = volume_string.replace('.', '').replace(',', '.')

        # If we created a string ending with a . append a zero so float conversion is predictable
        volume_string.strip()
        if (volume_string.endswith('.')):
            volume_string += '0'

        return float(volume_string)

    @staticmethod
    def images(response, cssSelector, isAbsolute=False, prefix=None) -> []:
        images = []

        for index, href in enumerate(response.css(cssSelector).extract()):
            if not isAbsolute:
                parsed_uri = urlparse(response.url)
                domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
                href = domain + href

            if isinstance(prefix, str):
                href = prefix + href

            images.append({'href': str(href)})

        return images

    @staticmethod
    def url(response, html, cssSelector) -> str:
        path = html.css(cssSelector).extract_first()
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        return domain + path

    @staticmethod
    def urlWithoutQueryString(response) -> str:
        if not isinstance(response, HtmlResponse):
            raise ValueError('Argument 1 passed into \'urlWithoutQueryString\' should be of the type HtmlResponse')

        parsed_reference = urlparse(response.url)
        return parsed_reference.scheme + "://" + parsed_reference.netloc + parsed_reference.path
