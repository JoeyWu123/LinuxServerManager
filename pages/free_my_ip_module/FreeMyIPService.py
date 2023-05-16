import logging
import logging.config
import os
import pandas as pd
import time
import json

from service import find_syslog, Service
from pages.free_my_ip_module.FreeMyIPClient import FreeMyIPClient
from filelock import Timeout, FileLock

from pages.free_my_ip_module.DomainDataOperator import DomainDataOperator


class FreeMyIPService(Service):
    def __init__(self):
        super(FreeMyIPService, self).__init__(name='FreeMyIPService', pid_dir='/var/run')
        logging.config.fileConfig(os.getcwd() + "/pages/free_my_ip_module/logging.conf")
        self.logger = logging.getLogger('FreeMyIPService')
        self._domain_data_operator = DomainDataOperator(os.getcwd() + "/pages/free_my_ip_module")
        self._freeMyIPClient = FreeMyIPClient()
        self._static_dns_heartbeat_interval = 3600 * 12 * 30  # 30 days as default
        self._latest_time_stamp_of_static_dns_heartbeat = 0
        self._latest_time_stamp_of_txt_record_heartbeat = 0
        with open(os.getcwd() + "/pages/free_my_ip_module/FreeMyIPServiceConfig.json", 'r') as f:
            config_data = json.load(f)
            self._ddns_heartbeat_interval = int(config_data['HeartBeatInterval']) * 3600

    def run(self):
        self.logger.info("The service is running now")
        while not self.got_sigterm():
            try:
                self.run_once()
            except Exception as e:
                self.logger.error(e)
            self.logger.info("The next execution will be sechduled after {} hours".format(self._ddns_heartbeat_interval/3600))
            self.pause_service(self._ddns_heartbeat_interval)
        self.logger.info("The service is stopped")


    # Use the following function for test purpose
    def run_once(self):
        domain_data = self._domain_data_operator.get_domain_data()
        current_time = time.time()
        any_static_dns_refreshed = False
        any_txt_record_refreshed = False
        for i in domain_data.index:
            if (domain_data["Domain Type"][i] == 'Dynamic Domain(DDNS)'):
                update_ddns_response = self._freeMyIPClient.update_domain_with_dynamic_IP(domain_data["Token"][i],
                                                                                          domain_data[
                                                                                              "Full Domain"][
                                                                                              i])
                if (update_ddns_response != "OK"):
                    self.logger.error(
                        "Fail in updating DDNS for domain {} with token:{}; FreeMyIP Response: {}".format(
                            domain_data["Full Domain"][i], domain_data["Token"][i], update_ddns_response))
                else:
                    self.logger.info(
                        "Successfully update DDNS for domain {} with token:{}; FreeMyIP Response: {}".format(
                            domain_data["Full Domain"][i], domain_data["Token"][i], update_ddns_response))
            if (domain_data["Domain Type"][i] == 'Static Domain'):
                # send heartbeat request for static domain every month
                if current_time - self._latest_time_stamp_of_static_dns_heartbeat >= 3600 * 24 * 30:
                    update_static_dns_response = self._freeMyIPClient.update_domain_with_static_IP(
                        domain_data["Token"][i], domain_data["Full Domain"][i], domain_data["IP Address"][i])
                    if (update_static_dns_response != "OK"):
                        self.logger.error(
                            "Fail in making requesting to keep static DNS resolution for domain {} with token:{} and IP Address: {}; FreeMyIP Response: {}".format(
                                domain_data["Full Domain"][i], domain_data["Token"][i],
                                domain_data["IP Address"][i], update_static_dns_response))
                    else:
                        self.logger.info(
                            "Successfully make request to keep static DNS resolution for domain {} with token:{} and IP Address: {}; FreeMyIP Response: {}".format(
                                domain_data["Full Domain"][i], domain_data["Token"][i],
                                domain_data["IP Address"][i], update_static_dns_response))
                        any_static_dns_refreshed = True
                else:
                    self.logger.info(
                        "Skipping sending heartbeat request to keep static domain {} because the last refresh request is within 30 days".format(
                            domain_data["Full Domain"][i]))
            if (pd.isna(domain_data["TXT Record"][i]) == False):
                if current_time - self._latest_time_stamp_of_txt_record_heartbeat >= 3600 * 24 * 30:
                    update_txt_response = self._freeMyIPClient.update_txt_record_for_domain(domain_data["Token"][i],
                                                                                            domain_data["Full Domain"][
                                                                                                i],
                                                                                            domain_data["TXT Record"][
                                                                                                i])
                    if (update_txt_response != "OK"):
                        self.logger.error(
                            "Fail in refreshing txt record for domain {} with token:{} and TXT Record:{}; FreeMyIP Response: {}".format(
                                domain_data["Full Domain"][i], domain_data["Token"][i], domain_data["TXT Record"][i],
                                update_txt_response))
                    else:
                        self.logger.info(
                            "Successfully refresh txt record for domain {} with token:{} and TXT Record:{}; FreeMyIP Response: {}".format(
                                domain_data["Full Domain"][i], domain_data["Token"][i], domain_data["TXT Record"][i],
                                update_txt_response))
                        any_txt_record_refreshed = True
                else:
                    self.logger.info(
                        "Skipping sending heartbeat request to keep txt record for domain {} because the last refresh request is within 30 days".format(
                            domain_data["Full Domain"][i]))
            time.sleep(0.1)  # control the rate to call FreeMyIP API
        if (any_static_dns_refreshed):
            self._latest_time_stamp_of_static_dns_heartbeat = current_time
        if (any_txt_record_refreshed):
            self._latest_time_stamp_of_txt_record_heartbeat = current_time

    def pause_service(self,pause_time_in_second):
        for i in range(pause_time_in_second):
            if self.got_sigterm():
                break
            time.sleep(1)



if __name__ == '__main__':
    freeMyIPService = FreeMyIPService()
    freeMyIPService.run_once()
