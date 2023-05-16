import logging
import logging.config
import os
import pandas as pd

from filelock import Timeout, FileLock
class DomainDataOperator():

    def __init__(self,free_my_ip_service_path):
        self._domain_data_path = free_my_ip_service_path+"/DomainData.csv"
        self._file_lock_path = free_my_ip_service_path+"/DomainData.csv.lock"
        logging.config.fileConfig(free_my_ip_service_path+'/logging.conf')
        self.logger = logging.getLogger('FreeMyIPService')
        self._file_lock = FileLock(self._file_lock_path, timeout=60)
        dir_list = os.listdir(free_my_ip_service_path)
        if ("DomainData.csv" not in dir_list):
            initial_data_frame = pd.DataFrame(columns=["FreeMyIP Domain Name", "Full Domain", "Token", "Domain Type", "IP Address", "TXT Record"])
            self.write_domain_data_to_csv(initial_data_frame)
        self._domain_data = self.read_domain_data_from_csv()

    def insert_or_override_domain_data(self, domain_name, token, domain_type, ip="", txt_record=""):
        index = self._domain_data[self._domain_data['FreeMyIP Domain Name'] == domain_name].index
        if (len(index) == 0):
            self._domain_data.loc[len(self._domain_data)] = pd.Series(
                {"FreeMyIP Domain Name": domain_name, "Full Domain": domain_name + ".freemyip.com", "Token": token,
                 "Domain Type": domain_type, "IP Address": ip, "TXT Record": txt_record})
        else:
            self._domain_data.loc[index[0]] = pd.Series(
                {"FreeMyIP Domain Name": domain_name, "Full Domain": domain_name + ".freemyip.com", "Token": token,
                 "Domain Type": domain_type, "IP Address": ip, "TXT Record": txt_record})
        self.write_domain_data_to_csv()
        return True

    def remove_domain_data(self,domain_name):
        index = self._domain_data[self._domain_data['FreeMyIP Domain Name'] == domain_name].index
        if len(index) == 0:
            return False
        else:
            self._domain_data =  self._domain_data.drop(axis=0, index=index[0])
            self.write_domain_data_to_csv()
            return True
    def get_domain_data(self):
        # get the latest data, in the case the file is changed
        self._domain_data = self.read_domain_data_from_csv()
        return self._domain_data.copy()
    def read_domain_data_from_csv(self):
        try:
            with self._file_lock.acquire(timeout=60):
                return pd.read_csv(self._domain_data_path,dtype=str)
        except Timeout:
            self.logger.error("The service is broken down as it cannot gain the lock to operate " + self._domain_data_path)
            raise Timeout("The service is broken down as it cannot gain the lock to operate " + self._domain_data_path)

    def write_domain_data_to_csv (self):
            try:
                with self._file_lock.acquire(timeout=60):
                    self._domain_data.to_csv(self._domain_data_path, index=False)
            except Timeout:
                self.logger.error("The service is broken down as it cannot gain the lock to operate " + self._domain_data_path)
                raise Timeout("The service is broken down as it cannot gain the lock to operate " + self._domain_data_path)
