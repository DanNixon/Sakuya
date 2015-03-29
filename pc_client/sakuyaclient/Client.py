import argparse
import logging
import sys
import ConfigParser
import importlib

from sakuyaclient.NotificationCentre import NotificationCentre
from sakuyaclient.sinks.TiLDADriver import TiLDADriver


class Client(object):

    def runFromCommandLine(self):
        """
        Gets command line options and starts Sakuya client.
        """
        parser = argparse.ArgumentParser(description='Client for Sakuya development aid')

        parser.add_argument(
            '--tilda-test',
            action='store_true',
            help='Perform a test of the TiLDA MKe and exit'
        )

        parser.add_argument(
            '-i', '--interval',
            action='store',
            type=float,
            help='Time in seconds between polling sources (overrides value in config file)'
        )

        parser.add_argument(
            '--config-file',
            action='store',
            help='File to save log to'
        )

        parser.add_argument(
            '--log-file',
            action='store',
            default='sakuya.log',
            help='File to save log to'
        )

        parser.add_argument(
            '--log-level',
            action='store',
            default='INFO',
            help='Logging level [DEBUG,INFO,WARNING,ERROR,CRITICAL]'
        )

        props = parser.parse_args()

        log_level = getattr(logging, props.log_level.upper(), None)
        if not isinstance(log_level, int):
            log_level = logging.INFO

        logging.basicConfig(level=log_level, filename=props.log_file)
        logging.getLogger(__name__).info('Sakuya started')

        if props.tilda_test:
            self.doTildaTest(props)
        else:
            self.startClient(props)


    def parseConfigFile(self, filename):
        """
        Parses the configuration file.

        @param filename Config filename
        @returns Tuple of global options and plugin options
        """

        config = ConfigParser.ConfigParser()
        config.read(filename)

        plugin_names = config.sections()

        sakuya = None
        if config.has_section('sakuya'):
            sakuya = dict(config.items('sakuya'))
            plugin_names.remove('sakuya')

        plugins = {'sink':dict(), 'source':dict()}
        for plugin in plugin_names:
            if not config.has_option(plugin, 'type'):
                logging.getLogger(__name__).warning('Plugin %s has no type, skipping')
                pass

            if not config.has_option(plugin, 'class'):
                logging.getLogger(__name__).warning('Plugin %s has no class, skipping')

            plugin_type = config.get(plugin, 'type')
            if not plugin_type in ['sink', 'source']:
                logging.getLogger(__name__).warning('Plugin %s has invalid type, skipping')
                pass

            plugins[plugin_type][plugin] = dict(config.items(plugin))

        return sakuya, plugins


    def startClient(self, props):
        """
        Runs the client application.

        @param props Application properties
        """

        sakuya_config, plugin_config = self.parseConfigFile(props.config_file);

        if props.interval is not None:
            interval = props.interval
        else:
            interval = float(sakuya_config.get('interval', '300'))

        # Create notification manager
        notifications = NotificationCentre(interval)

        print plugin_config

        # Create and add sources
        for source_name, source_config in plugin_config['source'].items():
            try:
                plugin_module = importlib.import_module('sakuyaclient.sources.%s' % source_config['class'])
                plugin_class = getattr(plugin_module, source_config['class'])
                source = plugin_class(source_config)
                notifications.add_notification_source(source_name, source)
            except RuntimeError:
                logging.getLogger(__name__).warning('Error creating source %s, skipping' % source_name)
                pass

        # Create and add sinks
        for sink_name, sink_config in plugin_config['sink'].items():
            try:
                plugin_module = importlib.import_module('sakuyaclient.sinks.%s' % sink_config['class'])
                plugin_class = getattr(plugin_module, sink_config['class'])
                sink = plugin_class(sink_config)
                notifications.add_notification_sink(sink_name, sink)
            except RuntimeError:
                logging.getLogger(__name__).warning('Error creating sink %s, skipping' % sink_name)
                pass

        # Start update loop
        notifications.start()


    def doTildaTest(self, props):
        """
        Runs a simple test of the TiLDA.

        @param props Application properties
        """
        import time
        from sakuyaclient.tilda_driver import BacklightTypes

        logging.getLogger(__name__).info('Running TiLDA test...')

        tilda = TiLDADriver()

        if props.port == 'auto':
            tilda.auto_connect(props.baud)
        else:
            tilda.connect(props.port, props.baud)

        tilda.set_led(1, 10, 0, 0)
        tilda.set_led(2, 0, 10, 0)

        tilda.send_notification(0, 0, 'Test notif. #1', 'NOW')
        tilda.send_notification(1, 1, 'Test notif. #2', 'NOW')
        tilda.send_notification(2, 2, 'Test notif. #3', 'NOW')
        tilda.send_notification(3, 3, 'Test notif. #4', 'NOW')

        tilda.set_backlight(BacklightTypes.ON.value)
        time.sleep(1)
        tilda.set_backlight(BacklightTypes.OFF.value)

        tilda.release()

        sys.stdout.write('TiLDA tested.\n')
