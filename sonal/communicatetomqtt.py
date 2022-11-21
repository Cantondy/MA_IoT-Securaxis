from threading import Thread, Event
from multiprocessing import Value
import queue
import logging
from ctypes import c_bool
import time
import random
import json
import uuid
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)

class CommunicateToMQTT(Thread):

    def __init__(
            self,
            _queue,
            device_id,
            wrapper_function,
            host,
            port,
            username,
            password,
            client_name,
            index,
            sending_interval,
            topic
    ):
        super(CommunicateToMQTT, self).__init__()
        self.is_started = Value(c_bool, False)
        self._queue = _queue
        self._index = index
        self._wrapper_function = wrapper_function
        self._sending_interval = sending_interval
        self._device_id = device_id
        self._client_name = client_name
        self.__first_request = True
        self.__last_sending_time = 0
        self._topic = topic
        self.heartbeat = Event()
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        
        # The client object is used to interact with your Azure IoT hub.
        self._mqtt = mqtt.Client()
       

    def stop(self):
        self.is_started.value = False

    def sendBulkToMQTT(self, bulk_array):
        """
        Function that publish the results through MQTT
        """
        try:
            self._mqtt.connect(self.host,self.port)
            logger.info('%s: Success Connection to the broker',type(self).__name__)
        except:
            logger.error('%s: Failed to connect to MQTT Broker: %s ',type(self).__name__,error)
        try:
            logger.info('%s: Send data to Broker - bulk_array = %s',type(self).__name__,bulk_array)
            array = json.dumps(bulk_array)
            result = self._mqtt.publish(self._topic,array)
            if (result[0]==0):
                 logger.info('%s: Send data to Broker - Published[%s]',type(self).__name__,result[1])
            else:
                 logger.info('%s: error Sending data to Broker ',type(self).__name__)
            #try:
            #   self._mqtt.send_message_to_output(msg, self._topic)
            #   logging.info('%s: Success - %s Published }',type(self).__name__,msg)
            #except Expection as error:
             #  logging.error('%s: send data error %s',type(self).__name__,error)
        except Exception as error:
            logging.error('%s: send data error %s',type(self).__name__,error)

    def run(self):

        logger.info('%s: Starting thread.',type(self).__name__)

        self.is_started.value = True
        while self.is_started.value:

            if time.time() - self.__last_sending_time < self._sending_interval:
                time.sleep(0.1)
                continue

            # Get all data from queue
            data = []
            while True:
                try:
                    data.append(self._queue.get_nowait())
                except queue.Empty:
                    time.sleep(0.1)
                    break

            # Try to send data to MQTT.
            # If this fails, put the data in the queue again.
            try:
                output = {}
                output['id'] = self._device_id
                output['c'] = self._client_name
                index_name = ''
                if self._index.find('vehicle-detection') !=-1:
                    index_name = 'vd'
                if self._index.find('sound-level') != -1:
                        index_name = 'nl'
                        # Send sound-level frequency bands during first request
                        if self.__first_request:
                            output['f'] = data[0][1].tolist()
                            self.__first_request = False
                if self._index.find('heartbeat') != -1:
                        index_name = 'hb'
                if self._index.find('sound-alert') != -1:
                        index_name = 'sa'
                output[index_name] = []
                for d in data:
                    output[index_name].append(self._wrapper_function(d))

                if len(output[index_name]) != 0:
                    self.sendBulkToMQTT(output)

            except Exception as error:
                logger.error('%s: Failed to send data to MQTT at index %s: %s',type(self).__name__,self._index,error)
                for d in data:
                    self._queue.put(d)

            self.__last_sending_time = time.time()

            self.heartbeat.set()

        logger.info('%s: Exiting thread.',type(self).__name__)
