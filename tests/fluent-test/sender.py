__author__ = 'hoangnn'
from fluent import sender, event
from logging import warning, info, basicConfig, INFO

if __name__ == "__main__":
    sender.setup('fluentd.test', host='sachcu.mobi', port=3008)
    event.Event('follow',{'from': 'userA', 'to': 'userB'})
    basicConfig(level=INFO)
    info("Test warning log")