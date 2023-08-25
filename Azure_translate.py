import time
import requests, uuid, json

class Azure_Translate:
    def __init__(self) -> None:
        # Add your key and endpoint
        self.key = "cf6f187264f14c9fb4ff84c7c2e80c0a"
        self.endpoint = "https://api.cognitive.microsofttranslator.com"

        # location, also known as region.
        # required if you're using a multi-service or regional (not global) resource. It can be found in the Azure portal on the Keys and Endpoint page.
        self.location = "japaneast"

        self.path = '/translate'
        self.constructed_url = self.endpoint + self.path

        self.params = {
            'api-version': '3.0',
            'from': 'en',
            'to': ['yue']
        }

    def translate(self, input_language="en", output_language="yue", text=""):

        if input_language != "en":
            input_language = "yue"
        if output_language != "en":
            output_language = "yue"

        headers = {
            'Ocp-Apim-Subscription-Key': self.key,
            # location required if you're using a multi-service or regional (not global) resource.
            'Ocp-Apim-Subscription-Region': self.location,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }
        self.params = {
            'api-version': '3.0',
            'from': input_language,
            'to': [output_language]
        }
        # You can pass more than one object in body.
        body = [{
            'text': text
        }]
        s = time.perf_counter()

        request = requests.post(self.constructed_url, params=self.params, headers=headers, json=body)
        response = request.json()

        # self.logger.info(json.dumps(response, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': '))) 
        output = response[0]['translations'][0]['text'] 

        return output