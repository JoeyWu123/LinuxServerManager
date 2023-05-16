import streamlit as st
import psutil
import socket

from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=3 * 1000, key="serverStatusRefresh")

def show_home_page():
    st.title('My Linux Server Dashboard')
    host_name = socket.gethostname()
    st.caption("Host Name: "+ host_name)
    col1, col2, col3 = st.columns(3)
    col1.metric(label="CPU Usage %", value= psutil.cpu_percent(1))
    col2.metric(label="RAM Usage %", value= psutil.virtual_memory()[2])
    col3.metric(label="RAM Used (GB)", value=round(psutil.virtual_memory()[3] / 1000000000, 2))
    col4, col5, col6 = st.columns(3)
    col4.metric(label="Disk Usage %", value=psutil.disk_usage('/')[3])
    col5.metric(label="Disk Used (GB)", value=round(psutil.disk_usage('/')[1]/1000000000, 2))
    ip_address = socket.gethostbyname(host_name)
    st.text("Local IPv4 Address: "+ip_address)


if __name__ == '__main__':
    show_home_page()