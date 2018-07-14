import json, requests, time
import Tkinter as tk 
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ChromeOptions, Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

class Program:
    def __init__(self):
        opts = ChromeOptions()
        opts.add_experimental_option("detach", True)
        self.browser = webdriver.Chrome(chrome_options=opts)
        self.update_info()
        self.browser.get('')


    def add_to_cart(self):
        self.update_info()
        self.browser.get('')
        product_url=''
        size_code=''
        self.r = requests.get(''+self.info['Product_Category'])
        soup = BeautifulSoup(self.r.text, 'html.parser')
        
        for div in soup.find_all('div', 'turbolink_scroller'):
            for a in div.find_all('a', 'name-link'):
                if a.text == self.info['Product_Name'] and a.find_next('a').text == self.info['Product_Color']:
                    product_url = a.get('href')
                    break
       
        self.r = requests.get(''+product_url)
        soup = BeautifulSoup(self.r.text, 'html.parser')
        st_code = soup.find(id='st').get('value')
        if self.info['Product_Size']:
            for size in soup.find(id='s').find_all('option'):
                if size.text == self.info['Product_Size']:
                    size_code = size.get('value')                
                    break
        else:
            size_code = soup.find(id='s').get('value')

        csrf_tok = soup.find('meta', attrs={'name':'csrf-token'}).get('content')     
        cart_url = soup.find(id='cart-addf').get('action')

        self.s = requests.Session()
        self.s.get(''+product_url)
        self.s.post(''+cart_url , data = {'utf-8': '%E2%9C%93', 'X-CSRF-Token': csrf_tok, 'st': st_code, 's': size_code, 'commit': 'add to cart'})
        for cookie in self.s.cookies:
            self.browser.add_cookie({
                'name': cookie.name,
                'value': cookie.value,
                'path': '/',
                'domain': cookie.domain
            })

    def check_out(self):
        self.browser.get('')
        time.sleep(1.55)
        self.browser.execute_script('document.getElementsByName("order[billing_name]")[0].setAttribute("value", arguments[0])', self.info['Billing_Name'])
        self.browser.execute_script('document.getElementsByName("order[email]")[0].setAttribute("value", arguments[0])', self.info['Email'])
        self.browser.execute_script('document.getElementsByName("order[tel]")[0].setAttribute("value", arguments[0])', self.info['Telephone'])
        self.browser.execute_script('document.getElementsByName("order[billing_address]")[0].setAttribute("value", arguments[0])', self.info['Billing_Address'])
        self.browser.execute_script('document.getElementsByName("order[billing_address_2]")[0].setAttribute("value", arguments[0])', self.info['Billing_Address_2'])
        self.browser.execute_script('document.getElementsByName("order[billing_zip]")[0].setAttribute("value", arguments[0])', self.info['Billing_Zip'])
        self.browser.execute_script('document.getElementsByName("order[billing_city]")[0].setAttribute("value", arguments[0])', self.info['Billing_City'])
        self.browser.execute_script('document.getElementsByName("order[billing_state]")[0].value = arguments[0]', self.info['Billing_State'])
        self.browser.execute_script('document.getElementsByName("order[billing_country]")[0].value = arguments[0]', self.info['Billing_Country'])
        self.browser.execute_script('document.getElementsByName("credit_card[nlb]")[0].setAttribute("value", arguments[0])', self.info['CC_#'])
        self.browser.execute_script('document.getElementsByName("credit_card[month]")[0].value = arguments[0]', self.info['CC_Exp_Month'])
        self.browser.execute_script('document.getElementsByName("credit_card[year]")[0].value = arguments[0]', self.info['CC_Exp_Year'])
        self.browser.execute_script('document.getElementsByName("credit_card[rvv]")[0].setAttribute("value", arguments[0])', self.info['CVV'])
        self.browser.execute_script('document.getElementsByClassName("iCheck-helper")[1].click()')
        time.sleep(1.55)
        self.browser.find_element_by_name('commit').click()

    def update_info(self):
        with open('info.json') as jsonfile:
            self.info = json.load(jsonfile)
        print self.info
        
class Gui:
    fields = 'Billing Name', 'Email', 'Telephone', 'Billing Address', 'Billing Address 2', 'Billing Zip', 'Billing City', 'Billing State', 'Billing Country', 'CC #', 'CC Exp Month', 'CC Exp Year', 'CVV', 'Product Name', 'Product Color', 'Product Category', 'Product Size'
    def __init__(self, program):
        self.program = program
        self.master = tk.Tk()
        self.entries = self.make_form()
        save_button = tk.Button(self.master, text='Save', command=self.save)
        save_button.pack(side=tk.LEFT, padx=5, pady=5)
        start_button = tk.Button(self.master, text='Start', command=self.run)
        start_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    def make_form(self):
        entries = {}
        for field in self.fields:
            row = tk.Frame(self.master)
            label = tk.Label(row, width=15, text=field, anchor='w')
            entry = tk.Entry(row)
            row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            label.pack(side=tk.LEFT)
            entry.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
            key = field.replace(' ','_')
            entries[key] = entry
        return entries

    def run(self):
        self.program.add_to_cart()
        self.program.check_out()

    def save(self):      
        save_info = {}
        for entry in self.entries:
            save_info[entry] = self.entries[entry].get()
        with open('info.json', 'w') as jsonfile:
            json.dump(save_info, jsonfile)

def main():
    program = Program()
    gui = Gui(program)
    gui.master.mainloop()

if __name__ == '__main__':
    main()