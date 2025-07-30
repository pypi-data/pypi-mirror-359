from robot.api.deco import keyword
import datetime
from Browser import Browser
import faker

class NS_Common_Keywords(object):

    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LIBRARY_DOC_FORMAT = "ROBOT"
    ROBOT_EXIT_ON_FAILURE = True

    @keyword('Selecteer Waarde In Combobox')
    def selecteer_waarde_in_combobox(self, xpath, value):
        browser = Browser()
        browser.click(xpath)
        browser.type_text(xpath, value, delay=0.01)
        browser.press_keys(xpath, 'Enter')

    @keyword('Selecteer Waarde In Multiselect Combobox')
    def selecteer_waarde_in_multiselect_combobox(self, xpath, value):
        browser = Browser()
        browser.click(xpath)
        browser.sleep(0.1)
        browser.type_text(xpath, value)
        browser.sleep(0.1)
        browser.press_keys(xpath, 'ArrowDown')
        browser.sleep(0.1)
        browser.press_keys(xpath, 'Enter')
        browser.sleep(0.1)
        browser.press_keys(xpath, 'Tab')
        browser.press_keys(xpath, 'Tab')

    @keyword('Get Modal Container')
    def get_modal_container(self, title):
        browser = Browser()
        xpath = f'//h4[contains(text(),"{title}")]/ancestor::div[contains(@class, "modal-dialog")]'
        return browser.get_element(xpath)

    @keyword('Close Modal')
    def close_modal(self, title, action):
        browser = Browser()
        container = self.get_modal_container(title)
        browser.click(f'{container}//button[text()="{action}"]')
        self.wacht_tot_element_onzichtbaar_is(container)

    @keyword('Wait For Modal')
    def wait_for_modal(self, title):
        browser = Browser()
        xpath = f'//h4[contains(text(),"{title}")]/ancestor::div[contains(@class, "modal-dialog")]'
        browser.wait_for_elements_state(xpath, 'visible')

    @keyword('Dismiss Modal')
    def dismiss_modal(self, title):
        self.close_modal(title, '.modal-header > .close')

    @keyword('Pas Format Aan Van Datum')
    def pas_format_aan_van_datum(self, datum, input_format='%d-%m-%Y', output_format='%Y-%m-%d'):
        return datetime.datetime.strptime(datum, input_format).strftime(output_format)

    @keyword('Bepaal Huidige Datum')
    def bepaal_huidige_datum(self, format='%d-%m-%Y'):
        return datetime.datetime.now().strftime(format)

    @keyword('Bepaal Datum Plus Extra Dagen')
    def bepaal_datum_plus_extra_dagen(self, aantal_dagen, begin_datum=None, format='%d-%m-%Y'):
        if begin_datum:
            start = datetime.datetime.strptime(begin_datum, format)
        else:
            start = datetime.datetime.now()
        nieuwe_datum = start + datetime.timedelta(days=int(aantal_dagen))
        return nieuwe_datum.strftime(format)

    @keyword('Creeer Willekeurige Zin')
    def creeer_willekeurige_zin(self):
        fake = faker.Faker('nl_NL')
        return fake.sentence(nb_words=8)

    @keyword('Creeer Willekeurig Woord')
    def creeer_willekeurig_woord(self):
        fake = faker.Faker('nl_NL')
        return fake.word()

    @keyword('Wacht Tot Element Onzichtbaar Is')
    def wacht_tot_element_onzichtbaar_is(self, xpath):
        browser = Browser()
        count = browser.get_element_count(xpath)
        tries = 0
        while count and tries < 100:
            browser.sleep(0.05)
            count = browser.get_element_count(xpath)
            tries += 1

    @keyword('Wacht Op Laden Element')
    def wacht_op_laden_element(self, xpath, eindstatus='visible', wachttijd='10s'):
        browser = Browser()
        browser.wait_for_elements_state(xpath, eindstatus, timeout=wachttijd)

    @keyword('Wacht Op Het Laden Van Een Tabel')
    def wacht_op_het_laden_van_een_tabel(self, xpath):
        browser = Browser()
        aantal = 0
        tries = 0
        while not aantal and tries < 10:
            browser.sleep(0.05)
            aantal = browser.get_element_count(f'{xpath}//div[@class="paging-status"]')
            tries += 1

    @keyword('Tel Aantal Regels Van Tabel')
    def tel_aantal_regels_van_tabel(self, xpath):
        browser = Browser()
        return browser.get_element_count(f'{xpath}//div[@role="row"]')

    @keyword('Wacht Op Herladen Data Tabel')
    def wacht_op_herladen_data_tabel(self, xpath, aantal_regels):
        browser = Browser()
        nieuw_aantal = aantal_regels
        tries = 0
        while nieuw_aantal == aantal_regels and tries < 20:
            browser.sleep(0.05)
            nieuw_aantal = self.tel_aantal_regels_van_tabel(xpath)
            tries += 1

    @keyword('Formatteer Bedrag')
    def formatteer_bedrag(self, amount):
        return '{:,.2f}'.format(float(amount)).replace(',', 'X').replace('.', ',').replace('X', '.')
