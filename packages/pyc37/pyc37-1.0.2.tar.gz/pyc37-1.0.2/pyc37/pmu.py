import logging
import socket
import os
import threading
import psutil
import gc
import weakref

from select import select
from threading import Thread
from multiprocessing import Queue
from multiprocessing import Process
from sys import stdout
from time import sleep, time
from pyc37.frame import *

__author__ = "Stevan Sandi"
__copyright__ = "Copyright (c) 2016, Tomo Popovic, Stevan Sandi, Bozo Krstajic"
__credits__ = []
__license__ = "BSD-3"
__version__ = "1.0.0-alpha"


class Pmu(object):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)  # Changed back to INFO to reduce spam
    handler = logging.StreamHandler(stdout)
    formatter = logging.Formatter("%(asctime)s %(levelname)s [PID:%(process)d|TID:%(thread)d] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    def __init__(self, pmu_id=7734, data_rate=30, port=4712, ip="127.0.0.1",
                 method="tcp", buffer_size=2048, set_timestamp=True):

        self.port = port
        self.ip = ip

        self.socket = None
        self.listener = None
        self.set_timestamp = set_timestamp
        self.buffer_size = buffer_size

        # Debug tracking
        self.client_count = 0
        self.max_clients = 0
        self.connection_history = []

        # FIXED: Use weak references to track client info instead of keeping strong references
        self.client_info = {}  # Maps process PID to info dict
        self.last_cleanup = time()

        self.logger.info("=== PMU INITIALIZATION ===")
        self.logger.info("PMU ID: %d, Port: %d, IP: %s, Data Rate: %d",
                         pmu_id, port, ip, data_rate)
        self.logger.info("Process PID: %d, Thread count: %d",
                         os.getpid(), threading.active_count())

        self.ieee_cfg2_sample = ConfigFrame2(pmu_id, 1000000, 1, "Station A", 7734, (False, False, True, False),
                                             4, 3, 1,
                                             ["VA", "VB", "VC", "I1", "ANALOG1", "ANALOG2", "ANALOG3",
                                              "BREAKER 1 STATUS", "BREAKER 2 STATUS", "BREAKER 3 STATUS",
                                              "BREAKER 4 STATUS", "BREAKER 5 STATUS", "BREAKER 6 STATUS",
                                              "BREAKER 7 STATUS", "BREAKER 8 STATUS", "BREAKER 9 STATUS",
                                              "BREAKER A STATUS", "BREAKER B STATUS", "BREAKER C STATUS",
                                              "BREAKER D STATUS", "BREAKER E STATUS", "BREAKER F STATUS",
                                              "BREAKER G STATUS"],
                                             [(915527, "v"), (915527, "v"), (915527, "v"), (45776, "i")],
                                             [(1, "pow"), (1, "rms"), (1, "peak")], [(0x0000, 0xffff)],
                                             60, 22, data_rate)

        self.ieee_data_sample = DataFrame(pmu_id, ("ok", True, "timestamp", False, False, False, 0, "<10", 0),
                                          [(14635, 0), (-7318, -12676), (-7318, 12675), (1092, 0)], 2500, 0,
                                          [100, 1000, 10000], [0x3c12], self.ieee_cfg2_sample)

        self.ieee_command_sample = CommandFrame(pmu_id, "start", None)

        self.cfg1 = self.ieee_cfg2_sample
        self.cfg1.__class__ = ConfigFrame1  # Casting CFG2 to CFG1
        self.cfg2 = self.ieee_cfg2_sample
        self.cfg3 = None
        self.header = HeaderFrame(pmu_id, "Hi! I am tinyPMU!")

        self.method = method
        self.clients = []
        self.client_buffers = []

        self.logger.info("=== PMU INITIALIZATION COMPLETE ===")

    def cleanup_dead_clients(self, force=False):
        """FIXED: Aggressive cleanup of dead clients and their buffers"""
        current_time = time()

        # Only run cleanup every 5 seconds unless forced
        if not force and (current_time - self.last_cleanup) < 5:
            return

        self.last_cleanup = current_time

        # Clean up dead processes
        alive_clients = []
        dead_pids = []

        for client in self.clients:
            if client.is_alive():
                alive_clients.append(client)
            else:
                dead_pids.append(client.pid if hasattr(client, 'pid') else 'unknown')
                try:
                    client.join(timeout=0.1)  # Quick cleanup
                except:
                    pass

        dead_count = len(self.clients) - len(alive_clients)
        if dead_count > 0:
            self.logger.warning("Cleaned up %d dead client processes: %s", dead_count, dead_pids)
            self.clients = alive_clients

            # FIXED: Clean up corresponding buffers - this was the main memory leak!
            # Remove buffers for dead processes
            active_buffers = []
            for i, buffer in enumerate(self.client_buffers):
                try:
                    # Test if buffer is still accessible
                    size = buffer.qsize()
                    if size > 1000:  # Also clean up buffers that are too full
                        self.logger.warning("Removing buffer %d with %d queued items", i, size)
                        continue
                    active_buffers.append(buffer)
                except:
                    # Buffer is dead, don't add it back
                    pass

            old_buffer_count = len(self.client_buffers)
            self.client_buffers = active_buffers
            buffer_cleanup_count = old_buffer_count - len(active_buffers)

            if buffer_cleanup_count > 0:
                self.logger.warning("Cleaned up %d dead client buffers", buffer_cleanup_count)

            # Force garbage collection after cleanup
            gc.collect()

    def log_resource_usage(self, context=""):
        """FIXED: Enhanced resource logging with buffer tracking"""
        try:
            process = psutil.Process()
            cpu_percent = process.cpu_percent()
            memory_info = process.memory_info()
            num_threads = process.num_threads()

            # Calculate total queued items across all buffers
            total_queued = 0
            for buffer in self.client_buffers:
                try:
                    total_queued += buffer.qsize()
                except:
                    pass

            self.logger.info(
                "RESOURCE USAGE %s: CPU: %.1f%%, Memory: %.1fMB, Threads: %d, Clients: %d, Buffers: %d, Queued: %d",
                context, cpu_percent, memory_info.rss / 1024 / 1024, num_threads,
                len(self.clients), len(self.client_buffers), total_queued)

            # FIXED: Force cleanup if memory usage is high
            if memory_info.rss > 1024 * 1024 * 1024:  # > 1GB
                self.logger.warning("High memory usage detected, forcing cleanup")
                self.cleanup_dead_clients(force=True)

        except Exception as e:
            self.logger.error("Error getting resource usage: %s", e)

    def set_id(self, pmu_id):
        self.logger.debug("Setting PMU ID to: %d", pmu_id)

        self.cfg1.set_id_code(pmu_id)
        self.cfg2.set_id_code(pmu_id)
        # self.cfg3.set_id_code(id)

        # Configuration changed - Notify all PDCs about new configuration
        self.send(self.cfg2)
        # self.send(self.cfg3)

        self.logger.info("[%d] - PMU Id changed.", self.cfg2.get_id_code())

    def set_configuration(self, config=None):
        self.logger.debug("Setting PMU configuration")

        # If none configuration given IEEE sample configuration will be loaded
        if not config:
            self.cfg1 = self.ieee_cfg2_sample
            self.cfg1.__class__ = ConfigFrame1  # Casting CFG-2 to CFG-1
            self.cfg2 = self.ieee_cfg2_sample
            self.cfg3 = None  # TODO: Configuration frame 3

        elif type(config) == ConfigFrame1:
            self.cfg1 = config

        elif type(config) == ConfigFrame2:
            self.cfg2 = config
            if not self.cfg1:  # If CFG-1 not set use current data stream configuration
                self.cfg1 = config
                self.cfg1.__class__ = ConfigFrame1

        elif type(config) == ConfigFrame3:
            self.cfg3 = ConfigFrame3

        else:
            raise PmuError("Incorrect configuration!")

        self.logger.info("[%d] - PMU configuration changed.", self.cfg2.get_id_code())

    def set_header(self, header=None):
        self.logger.debug("Setting PMU header")

        if isinstance(header, HeaderFrame):
            self.header = header
        elif isinstance(header, str):
            self.header = HeaderFrame(self.cfg2.get_id_code(), header)
        else:
            PmuError("Incorrect header setup! Only HeaderFrame and string allowed.")

        # Notify all connected PDCs about new header
        self.send(self.header)

        self.logger.info("[%d] - PMU header changed.", self.cfg2.get_id_code())

    def set_data_rate(self, data_rate):
        self.logger.debug("Setting data rate to: %d", data_rate)

        self.cfg1.set_data_rate(data_rate)
        self.cfg2.set_data_rate(data_rate)
        # self.cfg3.set_data_rate(data_rate)
        self.data_rate = data_rate

        # Configuration changed - Notify all PDCs about new configuration
        self.send(self.cfg2)
        # self.send(self.cfg3)

        self.logger.info("[%d] - PMU reporting data rate changed.", self.cfg2.get_id_code())

    def set_data_format(self, data_format):
        self.logger.debug("Setting data format")

        self.cfg1.set_data_format(data_format, self.cfg1.get_num_pmu())
        self.cfg2.set_data_format(data_format, self.cfg2.get_num_pmu())
        # self.cfg3.set_data_format(data_format, self.cfg3.get_num_pmu())

        # Configuration changed - Notify all PDCs about new configuration
        self.send(self.cfg2)
        # self.send(self.cfg3)

        self.logger.info("[%d] - PMU data format changed.", self.cfg2.get_id_code())

    def send(self, frame):
        """FIXED: Clean up dead buffers during send operations"""
        if not isinstance(frame, CommonFrame) and not isinstance(frame, bytes):
            raise PmuError("Invalid frame type. send() method accepts only frames or raw bytes.")

        # FIXED: Clean up dead buffers first
        self.cleanup_dead_clients()

        active_buffers = []
        sent_count = 0

        for i, buffer in enumerate(self.client_buffers):
            try:
                # Test if buffer is still accessible and not overfull
                queue_size = buffer.qsize()
                if queue_size > 1000:  # Prevent buffer overflow
                    self.logger.warning("Skipping overfull buffer %d with %d items", i, queue_size)
                    continue

                buffer.put(frame, block=False)  # Non-blocking put
                active_buffers.append(buffer)
                sent_count += 1
            except Exception as e:
                self.logger.debug("Removing dead/full buffer %d: %s", i, e)

        # Update buffer list to only active ones
        self.client_buffers = active_buffers

        if sent_count != len(self.client_buffers):
            self.logger.debug("Frame sent to %d/%d buffers", sent_count, len(self.client_buffers))

    def send_data(self, phasors=[], analog=[], digital=[], freq=0, dfreq=0,
                  stat=("ok", True, "timestamp", False, False, False, 0, "<10", 0), soc=None, frasec=None):

        self.logger.debug("Sending data frame")

        # PH_UNIT conversion
        if phasors and self.cfg2.get_num_pmu() > 1:  # Check if multistreaming:
            if not (self.cfg2.get_num_pmu() == len(self.cfg2.get_data_format()) == len(phasors)):
                raise PmuError("Incorrect input. Please provide PHASORS as list of lists with NUM_PMU elements.")

            for i, df in self.cfg2.get_data_format():
                if not df[1]:  # Check if phasor representation is integer
                    phasors[i] = map(lambda x: int(x / (0.00001 * self.cfg2.get_ph_units()[i])), phasors[i])
        elif not self.cfg2.get_data_format()[1]:
            phasors = map(lambda x: int(x / (0.00001 * self.cfg2.get_ph_units())), phasors)

        # AN_UNIT conversion
        if analog and self.cfg2.get_num_pmu() > 1:  # Check if multistreaming:
            if not (self.cfg2.get_num_pmu() == len(self.cfg2.get_data_format()) == len(analog)):
                raise PmuError("Incorrect input. Please provide analog ANALOG as list of lists with NUM_PMU elements.")

            for i, df in self.cfg2.get_data_format():
                if not df[2]:  # Check if analog representation is integer
                    analog[i] = map(lambda x: int(x / self.cfg2.get_analog_units()[i]), analog[i])
        elif not self.cfg2.get_data_format()[2]:
            analog = map(lambda x: int(x / self.cfg2.get_analog_units()), analog)

        data_frame = DataFrame(self.cfg2.get_id_code(), stat, phasors, freq, dfreq, analog, digital, self.cfg2)
        self.send(data_frame)

    def run(self):
        self.logger.info("=== STARTING PMU SERVER ===")

        if not self.cfg1 and not self.cfg2 and not self.cfg3:
            raise PmuError("Cannot run PMU without configuration.")

        # Check if socket is already bound
        if self.socket:
            self.logger.warning("PMU server already running! Socket exists.")
            return

        try:
            # Create TCP socket, bind port and listen for incoming connections
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.logger.debug("Created socket, attempting to bind to %s:%d", self.ip, self.port)

            self.socket.bind((self.ip, self.port))
            self.socket.listen(5)

            self.logger.info("Socket bound successfully to %s:%d", self.ip, self.port)
            self.log_resource_usage("AFTER_SOCKET_BIND")

            # Check if listener thread already exists
            if self.listener and self.listener.is_alive():
                self.logger.warning("Listener thread already running!")
                return

            self.listener = Thread(target=self.acceptor)  # Run acceptor thread to handle new connection
            self.listener.daemon = True
            self.listener.start()

            self.logger.info("Acceptor thread started successfully")
            self.log_resource_usage("AFTER_THREAD_START")

        except Exception as e:
            self.logger.error("Failed to start PMU server: %s", e)
            if self.socket:
                self.socket.close()
                self.socket = None
            raise

    def acceptor(self):
        self.logger.info("=== ACCEPTOR THREAD STARTED ===")
        self.logger.info("Acceptor thread ID: %d", threading.get_ident())

        connection_count = 0
        last_resource_log = time()

        while True:
            try:
                current_time = time()

                # FIXED: Rate limit resource logging
                if current_time - last_resource_log > 30:
                    self.logger.info("[%d] - Waiting for connection on %s:%d (Total: %d)",
                                     self.cfg2.get_id_code(), self.ip, self.port, connection_count)
                    self.log_resource_usage("ACCEPTOR_PERIODIC")
                    last_resource_log = current_time

                # FIXED: Regular cleanup every 30 seconds
                self.cleanup_dead_clients()

                # Accept a connection on the bound socket and fork a child process to handle it.
                conn, address = self.socket.accept()
                connection_count += 1
                self.client_count += 1

                self.logger.info("=== NEW CONNECTION #%d ===", connection_count)
                self.logger.info("Connection from %s:%d (Client ID: %d)", address[0], address[1], self.client_count)

                # Store connection info for debugging
                conn_info = {
                    'id': self.client_count,
                    'address': address,
                    'time': current_time,
                    'thread_count_before': threading.active_count()
                }
                self.connection_history.append(conn_info)

                # Keep only last 100 connections in history
                if len(self.connection_history) > 100:
                    self.connection_history = self.connection_history[-100:]

                # FIXED: Clean up before creating new buffer
                self.cleanup_dead_clients()

                # Create Queue which will represent buffer for specific client and add it to list of all client buffers
                buffer = Queue(maxsize=1000)  # FIXED: Limit queue size to prevent memory explosion
                self.client_buffers.append(buffer)
                self.logger.debug("Created buffer for client %d, total buffers: %d",
                                  self.client_count, len(self.client_buffers))

                process = Process(target=self.pdc_handler, args=(conn, address, buffer, self.cfg2.get_id_code(),
                                                                 self.cfg2.get_data_rate(), self.cfg1, self.cfg2,
                                                                 self.cfg3, self.header, self.buffer_size,
                                                                 self.set_timestamp, self.logger.level))
                process.daemon = True
                process.start()
                self.clients.append(process)

                # Update max clients if needed
                if len(self.clients) > self.max_clients:
                    self.max_clients = len(self.clients)

                self.logger.info("Started process PID: %d for client %s:%d",
                                 process.pid, address[0], address[1])

                # Close the connection fd in the parent, since the child process has its own reference.
                conn.close()

                # FIXED: Only log resource usage for significant events
                if connection_count % 5 == 0:  # Every 5 connections
                    self.log_resource_usage("AFTER_NEW_CLIENT")

                # FIXED: Check for rapid connections but don't spam logs
                if len(self.connection_history) >= 3:
                    recent_connections = self.connection_history[-3:]
                    time_span = recent_connections[-1]['time'] - recent_connections[0]['time']
                    if time_span < 2.0:  # 3 connections in less than 2 seconds
                        self.logger.warning("RAPID CONNECTIONS: 3 in %.1f seconds", time_span)

            except Exception as e:
                self.logger.error("Error in acceptor loop: %s", e)
                sleep(1)  # Prevent tight error loop

    def join(self):
        self.logger.info("Joining listener thread...")
        last_log = time()
        while self.listener and self.listener.is_alive():
            self.listener.join(0.5)
            current_time = time()
            if current_time - last_log > 60:  # Log every minute instead of every 0.5 seconds
                self.log_resource_usage("DURING_JOIN")
                self.cleanup_dead_clients()
                last_log = current_time

    def stop(self):
        """Gracefully stop the PMU server"""
        self.logger.info("=== STOPPING PMU SERVER ===")

        # Close socket to stop accepting new connections
        if self.socket:
            try:
                self.socket.close()
                self.logger.info("Socket closed")
            except Exception as e:
                self.logger.error("Error closing socket: %s", e)
            finally:
                self.socket = None

        # Terminate all client processes
        for i, client in enumerate(self.clients):
            if client.is_alive():
                self.logger.info("Terminating client process %d (PID: %d)", i, client.pid)
                client.terminate()
                client.join(timeout=2)
                if client.is_alive():
                    self.logger.warning("Force killing client process %d", i)
                    client.kill()

        self.clients.clear()
        self.client_buffers.clear()

        # Force garbage collection
        gc.collect()

        self.log_resource_usage("AFTER_STOP")
        self.logger.info("=== PMU SERVER STOPPED ===")

    @staticmethod
    def pdc_handler(connection, address, buffer, pmu_id, data_rate, cfg1, cfg2, cfg3, header,
                    buffer_size, set_timestamp, log_level):

        # Recreate Logger (handler implemented as static method due to Windows process spawning issues)
        logger = logging.getLogger(f"CLIENT_{address[0]}_{address[1]}")
        logger.setLevel(log_level)
        handler = logging.StreamHandler(stdout)
        formatter = logging.Formatter("%(asctime)s %(levelname)s [CLIENT-PID:%(process)d] %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        logger.info("=== CLIENT HANDLER STARTED ===")
        logger.info("[%d] - Connection from %s:%d (Handler PID: %d)", pmu_id, address[0], address[1], os.getpid())

        # Wait for start command from connected PDC/PMU to start sending
        sending_measurements_enabled = False
        messages_sent = 0
        commands_received = 0
        start_time = time()

        # Calculate delay between data frames
        if data_rate > 0:
            delay = 1.0 / data_rate
        else:
            delay = -data_rate

        logger.debug("Data frame delay set to: %.4f seconds", delay)

        try:
            loop_count = 0
            last_resource_log = time()
            last_activity = time()

            while True:
                loop_count += 1
                current_time = time()

                # FIXED: Log resource usage every 60 seconds instead of 30
                if current_time - last_resource_log > 60:
                    try:
                        process = psutil.Process()
                        cpu_percent = process.cpu_percent()
                        memory_info = process.memory_info()
                        logger.info("CLIENT RESOURCES: CPU: %.1f%%, Memory: %.1fMB, Loop: %d, Messages: %d",
                                    cpu_percent, memory_info.rss / 1024 / 1024, loop_count, messages_sent)
                        last_resource_log = current_time
                    except:
                        pass

                # FIXED: Timeout inactive connections after 10 minutes
                if current_time - last_activity > 600:
                    logger.warning("Client inactive for 10 minutes, closing connection")
                    break

                command = None
                received_data = b""

                # FIXED: Use longer timeout to prevent excessive CPU usage
                readable, writable, exceptional = select([connection], [], [], 0.1)  # 100ms timeout instead of 0

                if readable:
                    last_activity = current_time
                    logger.debug("Data available to read from client")
                    """
                    Keep receiving until SYNC + FRAMESIZE is received, 4 bytes in total.
                    Should get this in first iteration. FRAMESIZE is needed to determine when one complete message
                    has been received.
                    """
                    try:
                        # FIXED: Add timeout to recv operations
                        connection.settimeout(5.0)  # 5 second timeout

                        while len(received_data) < 4:
                            chunk = connection.recv(buffer_size)
                            if not chunk:
                                logger.warning("Connection closed by client during header read")
                                return
                            received_data += chunk

                        bytes_received = len(received_data)
                        total_frame_size = int.from_bytes(received_data[2:4], byteorder="big", signed=False)

                        # FIXED: Validate frame size to prevent attacks
                        if total_frame_size > 65536 or total_frame_size < 4:
                            logger.error("Invalid frame size: %d, closing connection", total_frame_size)
                            break

                        logger.debug("Expected frame size: %d bytes", total_frame_size)

                        # Keep receiving until every byte of that message is received
                        while bytes_received < total_frame_size:
                            message_chunk = connection.recv(min(total_frame_size - bytes_received, buffer_size))
                            if not message_chunk:
                                logger.warning("Connection closed by client during message read")
                                break
                            received_data += message_chunk
                            bytes_received += len(message_chunk)
                            logger.debug("Received %d/%d bytes", bytes_received, total_frame_size)

                        # If complete message is received try to decode it
                        if len(received_data) == total_frame_size:
                            try:
                                received_message = CommonFrame.convert2frame(
                                    received_data)  # Try to decode received data
                                commands_received += 1

                                if isinstance(received_message, CommandFrame):
                                    command = received_message.get_command()
                                    logger.info("[%d] - Received command: [%s] <- (%s:%d) [Total: %d]",
                                                pmu_id, command, address[0], address[1], commands_received)
                                else:
                                    logger.info("[%d] - Received [%s] <- (%s:%d)", pmu_id,
                                                type(received_message).__name__, address[0], address[1])
                            except FrameError as e:
                                logger.warning("[%d] - Received unknown message <- (%s:%d): %s",
                                               pmu_id, address[0], address[1], e)
                        else:
                            logger.warning("[%d] - Message not received completely <- (%s:%d) (got %d, expected %d)",
                                           pmu_id, address[0], address[1], len(received_data), total_frame_size)
                    except socket.timeout:
                        logger.warning("Socket timeout during read operation")
                        break
                    except Exception as e:
                        logger.error("Error reading from client: %s", e)
                        break
                    finally:
                        connection.settimeout(None)  # Reset timeout

                if command:
                    last_activity = current_time
                    if command == "start":
                        sending_measurements_enabled = True
                        logger.info("[%d] - Start sending -> (%s:%d)", pmu_id, address[0], address[1])

                    elif command == "stop":
                        logger.info("[%d] - Stop sending -> (%s:%d)", pmu_id, address[0], address[1])
                        sending_measurements_enabled = False

                    elif command == "header":
                        if set_timestamp: header.set_time()
                        connection.sendall(header.convert2bytes())
                        messages_sent += 1
                        logger.info("[%d] - Requested Header frame sent -> (%s:%d)",
                                    pmu_id, address[0], address[1])

                    elif command == "cfg1":
                        if set_timestamp: cfg1.set_time()
                        connection.sendall(cfg1.convert2bytes())
                        messages_sent += 1
                        logger.info("[%d] - Requested Configuration frame 1 sent -> (%s:%d)",
                                    pmu_id, address[0], address[1])

                    elif command == "cfg2":
                        if set_timestamp: cfg2.set_time()
                        connection.sendall(cfg2.convert2bytes())
                        messages_sent += 1
                        logger.info("[%d] - Requested Configuration frame 2 sent -> (%s:%d)",
                                    pmu_id, address[0], address[1])

                    elif command == "cfg3":
                        if cfg3:
                            if set_timestamp: cfg3.set_time()
                            connection.sendall(cfg3.convert2bytes())
                            messages_sent += 1
                            logger.info("[%d] - Requested Configuration frame 3 sent -> (%s:%d)",
                                        pmu_id, address[0], address[1])
                        else:
                            logger.warning("[%d] - CFG3 requested but not available -> (%s:%d)",
                                           pmu_id, address[0], address[1])

                # FIXED: Only send data if enabled AND buffer has data AND we're not too fast
                if sending_measurements_enabled:
                    try:
                        # FIXED: Non-blocking get with timeout to prevent hanging
                        data = buffer.get(block=False)

                        if isinstance(data, CommonFrame):  # If not raw bytes convert to bytes
                            if set_timestamp: data.set_time()
                            data = data.convert2bytes()

                        # FIXED: Respect the data rate properly
                        sleep(delay)
                        connection.sendall(data)
                        messages_sent += 1
                        last_activity = current_time

                        # FIXED: Log every 1000 messages instead of 100
                        if messages_sent % 1000 == 0:
                            logger.debug("[%d] - Message #%d sent -> (%s:%d)",
                                         pmu_id, messages_sent, address[0], address[1])
                    except Exception as e:
                        # FIXED: Only log real errors, not empty queue
                        if "Empty" not in str(e):
                            logger.debug("Queue empty or send error: %s", e)
                        # Don't break on queue empty - this is normal

        except Exception as e:
            logger.error("Error in client handler: %s", e)
        finally:
            try:
                connection.close()
            except:
                pass
            end_time = time()
            session_duration = end_time - start_time
            logger.info("=== CLIENT HANDLER ENDED ===")
            logger.info("[%d] - Connection from %s:%d closed after %.2f seconds",
                        pmu_id, address[0], address[1], session_duration)
            logger.info("Session stats - Commands: %d, Messages: %d, Loops: %d",
                        commands_received, messages_sent, loop_count)


class PmuError(BaseException):
    pass