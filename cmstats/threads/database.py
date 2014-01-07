import threading
import time
import logging

from Queue import Empty

from cmstats.model.schema.devices import Device 

class DatabaseThread(threading.Thread):
    def __init__(self, queue):
        self.running = True
        self.queue = queue
        self.count = 0

        threading.Thread.__init__(self)

    def run(self):
        while self.running:
            self.loop()

    def loop(self):
        if self.queue.qsize() > 1:
            logging.debug("Queue size: %d" % self.queue.qsize())
        try:
            work = self.queue.get_nowait()
            self.process_work(work)
            self.count += 1
            self.queue.task_done()
        except Empty:
            # Sleep if the queue was empty
            if self.count > 0:
                logging.warn("Saved %s checkins to the database." % self.count)
            self.count = 0
            time.sleep(5)
            return

    def process_work(self, work):
        Device.add(**work)
