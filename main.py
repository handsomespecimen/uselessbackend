from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import urllib.parse
import time
import re

app = Flask(__name__)

def clean(text):
    text = text.replace('`', '')
    text = text.translate(str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹', '0123456789'))
    text = text.translate(str.maketrans('₀₁₂₃₄₅₆₇₈₉', '0123456789'))
    return text

def get_reaction_products(chemical_input):
    prompt = '[OUTPUT ONLY JSON WITH REACTION PRODUCTS FROM ONLY THE INPUT COMPOUNDS (WHICH ARE SINGULAR MOLECULES) IN THE GIVEN QUANTITIES WITH FORMAT {"products":["compound",...]}. ATOMS IN BOTH INPUT AND OUTPUT MUST BE THE SAME, DO NOT ADD OR REMOVE ANY, ADHERE WITH LAW OF CONSERVATION OF MASS. INCLUDE WASTE IF PRESENT. IF NO REACTION, RETURN INPUT. IF MULTIPLE OF THE SAME COMPOUND ARE PRODUCED THEN LIST THEM ONE BY ONE] {input:{'+f"{chemical_input}"+'}}'
    
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    start_time = time.time()
    try:
        driver.get(f"https://isou.chat/search?q={urllib.parse.quote(prompt)}")
        time.sleep(1)
        driver.refresh()
        while True:
            if time.time()-start_time > 60:
                return {"error": "timed out"}
            labels = driver.find_elements(By.XPATH, "/html/body/div/div/div[3]/div[2]/div/div[1]/div[2]/div[1]/div[2]/div[2]/div/p")
            if labels:
                first_label = labels[0]
                time.sleep(.5)
                if len(driver.find_elements(By.XPATH, "/html/body/div/div/div[3]/div[2]/div/div[1]/div[2]/div[1]/div[2]/div[2]/div/p")) > 1:
                    return clean(first_label.text)
                if first_label.text and not first_label.text.endswith("..."):
                    return clean(first_label.text)
            time.sleep(.5)
    finally:
        driver.quit()

@app.route('/reaction', methods=['GET', 'POST'])
def reaction():
    if request.method == 'POST':
        data = request.get_json()
        chemical_input = data.get('input')
    else:
        chemical_input = request.args.get('input')
    if not chemical_input:
        return jsonify({"error": "no input"}),400
    try:
        result = get_reaction_products(chemical_input)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}),500

if __name__ == '__main__':
    app.run(debug=True)
