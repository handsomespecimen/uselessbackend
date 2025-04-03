from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
import urllib.parse
import time
import re

app = Flask(__name__)

def clean(text):
    if not text:
        return ""
    text = text.replace('`', '').replace('"', '')
    text = text.translate(str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉', '01234567890123456789'))
    return text

def get(compounds):
    if not compounds or not isinstance(compounds, list):
        return {"error": "invalid format"}
    input = ",".join(compounds)
    prompt = f'[OUTPUT ONLY JSON WITH REACTION PRODUCTS FROM ONLY THE INPUT COMPOUNDS (WHICH ARE SINGULAR MOLECULES) IN THE GIVEN QUANTITIES WITH FORMAT {"products":["compound",...]}. ATOMS IN BOTH INPUT AND OUTPUT MUST BE THE SAME, DO NOT ADD OR REMOVE ANY, ADHERE WITH LAW OF CONSERVATION OF MASS. INCLUDE WASTE IF PRESENT. IF NO REACTION, RETURN INPUT. IF MULTIPLE OF THE SAME COMPOUND ARE PRODUCED THEN LIST THEM ONE BY ONE] {{input:{input}}}'
    options = Options()
    options.headless = True
    try:
        driver = webdriver.Firefox(options=options)
        starttime = time.time()
        try:
            driver.get(f"https://isou.chat/search?q={urllib.parse.quote(prompt)}")
            time.sleep(1)
            while True:
                if time.time() - starttime > 60:
                    return {"error": "timed out"}
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, "div.message-content p")
                    if elements:
                        response = elements[-1].text
                        if response and not response.endswith("..."):
                            jsonmatch = re.search(r'\{.*\}', response)
                            if jsonmatch:
                                return {"products": jsonmatch.group()}
                            return {"products": [clean(response)]}
                except WebDriverException as e:
                    return {"error": f"server error: {str(e)}"}
                time.sleep(.5)
        finally:
            driver.quit()
    except Exception as e:
        return {"error": f"server error: {str(e)}"}

@app.route('/reaction', methods=['POST'])
def reaction():
    try:
        data = request.get_json()
        if not data or 'input' not in data:
            return jsonify({"error": "invalid input"}), 400
        result = get(data['compounds'])
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"server error: {str(e)}"}), 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
