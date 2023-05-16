import streamlit as st
import os
import sys
from pages.free_my_ip_module.DomainDataOperator import DomainDataOperator
from pages.free_my_ip_module.FreeMyIPService import FreeMyIPService
import json
import time
import pandas as pd

domain_data_operator = DomainDataOperator(os.getcwd() + "/pages/free_my_ip_module")


def show_dns_free_my_ip_page():
    global domain_data_operator
    # freeMyIPService = FreeMyIPService()
    tab1, tab2, tab3 = st.tabs(["Service Status", "Service Configuration", "Service Log and Metrics"])
    with tab1:
        st.subheader("FreeMyIPService Status:")
        freeMyIPService = FreeMyIPService()
        freeMyIPService_status = freeMyIPService.is_running()
        if (freeMyIPService_status == False):
            st.markdown(":red[Stopped]")
            if (st.button("Start the Service")):
                freeMyIPService.start()
                # allow 15 seconds to stop/start the service

                show_progress_bar(15, "Starting the service...")
                st.experimental_rerun()
        else:
            st.markdown(":green[Running]")
            with open(os.getcwd() + "/pages/free_my_ip_module/FreeMyIPServiceConfig.json", 'r') as f:
                data = json.load(f)
            st.text("DDNS HeartBeat Interval: " + str(data['HeartBeatInterval']) + " Hours")
            if (st.button("Stop the Service")):
                freeMyIPService.stop()
                # allow 15 seconds to stop/start the service
                show_progress_bar(15, "Stopping the service...")
                st.experimental_rerun()

    with tab2:
        operation = st.columns(2)[0].selectbox("Operation", ("Add/Override Domain", "Delete Domain"))
        if operation == "Add/Override Domain":
            col1, col2, col3, col4 = st.columns(4)
            domain_name = col1.text_input("Domain Name", placeholder="Required")
            col2.markdown("#")
            col2.text(".freemyip.com")

            token = col3.text_input("Token", placeholder="Required")
            domain_type = col4.selectbox("Domain Type", ("Dynamic Domain(DDNS)", "Static Domain"))
            # start new row
            col5, col6, col7, col8 = st.columns(4)
            txt_record = col5.text_input("TXT Record", placeholder="Optional")
            ip = ""
            if domain_type == "Static Domain":
                ip = col6.text_input("IP Address", placeholder="Required")
            if (st.button("Update")):
                if (check_if_input_is_valid_for_insert_or_override(domain_name, token, domain_type, ip) == False):
                    st.warning("Required Field(s) have empty value")
                else:
                    domain_data_operator.insert_or_override_domain_data(domain_name, token, domain_type, ip, txt_record)
                    st.info("The domain data is updated. Please stop/start the FreeMyIP Service to take effect")
        if operation == "Delete Domain":
            col1, col2 = st.columns(2)
            domain_name = col1.text_input("Domain To Delete")
            col2.markdown("#")
            col2.text(".freemyip.com")
            if (st.button("Delete")):
                if (check_if_input_is_valid_for_delete(domain_name) == False):
                    st.warning("Required Field(s) have empty value")
                else:
                    operation_result = domain_data_operator.remove_domain_data(domain_name)
                    if (operation_result == False):
                        st.info(
                            "No domain name wasn't removed because the domain name you input doesn't exist in the table")
                    else:
                        st.info(
                            "The domain name you input was successfully removed from table. This FreeMyIP service will no longer send heartbeat message to FreeMyIP server to keep this deleted domain name")

        domain_data = domain_data_operator.get_domain_data()
        st.table(domain_data)
    with tab3:
        max_lines_displayed = int(st.selectbox("Max Lines Displayed", (10, 100, 300, 500, 1000)))
        full_txt = ""
        with open("/var/log/FreeMyIPService.log",'r') as my_log:
            all_lines = my_log.readlines()
        all_lines.reverse()
        for index in range(min(len(all_lines),max_lines_displayed)):
            full_txt = full_txt+all_lines[index]
        st.text(full_txt)


def check_if_input_is_valid_for_insert_or_override(domain_name, token, domain_type, ip=""):
    if (len(domain_name) == 0 or len(token) == 0):
        return False
    if (domain_type == "Static Domain" and len(ip) == 0):
        return False
    return True


def check_if_input_is_valid_for_delete(domain_name):
    if (len(domain_name) == 0):
        return False
    return True


def show_progress_bar(second_to_wait, bar_text):
    my_bar = st.progress(0, text=bar_text)
    for percent_complete in range(100):
        time.sleep(second_to_wait / 100)
        my_bar.progress(percent_complete + 1, text=bar_text)


if __name__ == '__main__':
    show_dns_free_my_ip_page()
