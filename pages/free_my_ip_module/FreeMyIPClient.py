import pandas as pd
import logging.config
import requests
import os


class FreeMyIPClient():
    # The following setting refers to https://freemyip.com/help
    def __init__(self):
        self.update_base_link = "https://freemyip.com/update?"
        self.check_ip_link = "http://freemyip.com/checkip"
        logging.config.fileConfig(os.getcwd() + "/pages/free_my_ip_module/logging.conf")
        self.logger = logging.getLogger('FreeMyIPService')

    def check_ip_address(self):
        self.logger.info("Calling FreeMyIP API with request link {}".format(self.check_ip_link))
        response = requests.get(self.check_ip_link)
        return response.text.strip()

    def update_domain_with_static_IP(self, token, domain, ip):
        request_link = self.update_base_link + 'token={}&domain={}&myip={}'.format(token, domain, ip)
        self.logger.info("Calling FreeMyIP API with request link {}".format(request_link))
        response = requests.get(request_link)
        return response.text.strip()

    def update_domain_with_dynamic_IP(self, token, domain):
        request_link = self.update_base_link + 'token={}&domain={}'.format(token, domain)
        self.logger.info("Calling FreeMyIP API with request link {}".format(request_link))
        response = requests.get(request_link)
        return response.text.strip()

    def update_txt_record_for_domain(self, token, domain, txt):
        formalized_txt = txt.replace(" ", "%20")
        request_link = self.update_base_link + 'token={}&domain={}&txt={}'.format(token, domain, formalized_txt)
        self.logger.info("Calling FreeMyIP API with request link {}".format(request_link))
        response = requests.get(request_link)
        return response.text.strip()


if __name__ == '__main__':
    freeMyIPClient = FreeMyIPClient()
    response = freeMyIPClient.update_domain_with_dynamic_IP('justTest', "mydomain.freemyip.com", )
    print(response)
