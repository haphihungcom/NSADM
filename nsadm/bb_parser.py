"""Parse BBCode tags.
"""

import logging

import toml
import bbcode

from nsadm import utils


logger = logging.getLogger(__name__)


class BBRegistry():
    """Complex formatter registry.
    """

    complex_formatters = []

    @classmethod
    def register(cls, tag_name, **kwargs):
        """[summary]

        Args:
            tag_name (str): Tag name.
        """

        def decorator(class_obj):
            kwargs['obj'] = class_obj
            kwargs['tag_name'] = tag_name
            cls.complex_formatters.append(kwargs)

            # Return original class object to make tests on them possible.
            return class_obj

        return decorator

    @classmethod
    def init_complex_formatters(cls, path, config):
        """Initialize complex formatters and give them config.

        Args:
            path (str): Path to complex formatter file.
            config (dict): Complex formatter config.
        """

        try:
            utils.load_module(path)
            logger.debug('Loaded complex formatter file at "%s"', path)
        except FileNotFoundError as err:
            raise FileNotFoundError('Could not find complex formatter file at "{}"'.format(path)) from err

        inited_formatters = []
        for formatter in cls.complex_formatters:
            tag_name = formatter['tag_name']
            if tag_name in config:
                formatter['obj'].config = config[tag_name]
                logger.debug('Loaded complex formatter "%s" configuration: %r',
                              tag_name, config[tag_name])
            formatter['obj'] = formatter['obj']()
            inited_formatters.append(formatter)
            logger.debug('Loaded complex formatter "%s"', tag_name)

        cls.complex_formatters = []
        return inited_formatters


class BBFormatters():
    """Abstract class for formatter managers.
    """

    def __init__(self):
        self.formatters = []

    def load_formatters(self):
        """Load formatters into list."""

        raise NotImplementedError

    def get_formatters(self):
        """Get loaded formatters."""

        return self.formatters


class BBSimpleFormatters(BBFormatters):
    """Simple BBCode formatter manager."""

    def load_formatters(self, path):
        """Load simple formatters

        Args:
            path (str): Path to simple formatter file.
        """

        if path is None:
            return

        try:
            formatter_config = toml.load(path)
        except FileNotFoundError:
            logger.error('Simple formatter file not found at "%s"', path)
            return

        for tag_name, formatter in formatter_config.items():
            formatter['tag_name'] = tag_name
            self.formatters.append(formatter)


class BBComplexFormatters(BBFormatters):
    """Manager for complex formatters.

    Args:
        bb_registry (BBRegistry): BBCode complex formatter registry.
    """

    def load_formatters(self, bb_registry, load_path, config_path):
        """Load complex formatters.

        Args:
            load_path (str): File path to load complex formatters from.
            config_path (str): Path to complex formatter config file.
        """

        if load_path is None:
            return

        config = {}
        if config_path is not None:
            try:
                config = toml.load(config_path)
            except FileNotFoundError:
                logger.error('Complex formatter config file not found at "%s"', config_path)

        formatters = bb_registry.init_complex_formatters(load_path, config)

        for formatter in formatters:
            render_func = formatter.pop('obj').format
            formatter['func'] = render_func
            self.formatters.append(formatter)


class BBParserAdapter():
    """Adapter for third-party BBCode parser.

       Args:
            bb_config (dict): BBCode formatter configuration.
            custom_vars (dict): Custom variables to pass to formatters.
    """

    def __init__(self):
        self.parser = bbcode.Parser(newline='\n',
                                    install_defaults=False,
                                    escape_html=False,
                                    replace_links=False,
                                    replace_cosmetic=False)

    def add_simple_formatter(self, tag_name, template, **kwargs):
        """Add a simple formatter.

        Args:
            tag_name (str): Tag name.
            format_string (func): Template.
        """

        self.parser.add_simple_formatter(tag_name=tag_name,
                                         format_string=template,
                                         **kwargs)

    def add_complex_formatter(self, tag_name, render_func, **kwargs):
        """Add a complex formatter.

        Args:
            tag_name (str): Tag name.
            render_func (func): Render function.
        """

        self.parser.add_formatter(tag_name=tag_name,
                                  render_func=render_func,
                                  **kwargs)

    def format(self, text, **kwargs):
        """Call parser to format.

        Args:
            text (str): Text to format

        Returns:
            str: Formatted text
        """

        return self.parser.format(text, **kwargs)


class BBParserLoader():
    """Load BBCode parser with formatters.

        Args:
            parser (BBParserCore): BBCode parser adapter.
    """

    def __init__(self, parser):
        self.parser = parser

    def load_parser(self, simple_formatters, complex_formatters):
        """Load and get loaded parser,

        Args:
            simple_formatters (BBSimpleFormatters): Simple formatter manager.
            complex_formatters (BBComplexFormatters): Complex formatter manager.

        Returns:
            Parser object.
        """


        self.load_simple_formatters(simple_formatters)
        self.load_complex_formatters(complex_formatters)
        logger.info('Loaded all BBCode formatters')

        return self.parser

    def load_simple_formatters(self, simple_formatters):
        """Load all simple formatters into parser.
        """

        for formatter in simple_formatters.get_formatters():
            if 'template' not in formatter:
                logger.error("Simple formatter '%s' doesn't have template", formatter['tag_name'])
                continue

            self.parser.add_simple_formatter(
                tag_name=formatter['tag_name'],
                template=formatter['template'],
                escape_html=False,
                replace_links=False,
                replace_cosmetic=False,
                newline_closes=formatter.get('newline_closes', False),
                same_tag_closes=formatter.get('same_tag_closes', False),
                standalone=formatter.get('standalone', False),
                render_embedded=formatter.get('render_embedded', True),
                strip=formatter.get('strip', False),
                swallow_trailing_newline=formatter.get('swallow_trailing_newline', False))

            logger.debug('Loaded simple BBCode formatter: %r', formatter)

    def load_complex_formatters(self, complex_formatters):
        """Load all complex formatters into parser.
        """

        for formatter in complex_formatters.get_formatters():
            self.parser.add_complex_formatter(
                tag_name=formatter['tag_name'],
                render_func=formatter['func'],
                escape_html=False,
                replace_links=False,
                replace_cosmetic=False,
                newline_closes=formatter.get('newline_closes', False),
                same_tag_closes=formatter.get('same_tag_closes', False),
                standalone=formatter.get('standalone', False),
                render_embedded=formatter.get('render_embedded', True),
                strip=formatter.get('strip', False),
                swallow_trailing_newline=formatter.get('swallow_trailing_newline', False))
            logger.debug('Loaded complex formatter "%s"', formatter['tag_name'])


class BBParser():
    """Render NSCode tags from custom BBCode tags.

    Args:
        simple_formatter_path (str): Simple formatter file path
        complex_formatter_path (str): Complex formatter file path
        complex_formatter_config_path (str): Complex formatter config file path
    """

    def __init__(self, simple_formatter_path,
                 complex_formatter_path,
                 complex_formatter_config_path):
        self.simple_formatter_path = simple_formatter_path
        self.complex_formatter_path = complex_formatter_path
        self.complex_formatter_config_path = complex_formatter_config_path

        self.parser = BBParserAdapter()
        self.simple_formatters = BBSimpleFormatters()
        self.registry = BBRegistry()
        self.complex_formatters = BBComplexFormatters()

    def load_formatters(self):
        """Load all formatters from their files.
        """

        self.simple_formatters.load_formatters(self.simple_formatter_path)
        self.complex_formatters.load_formatters(self.registry, self.complex_formatter_path,
                                                self.complex_formatter_config_path)

        loader = BBParserLoader(self.parser)
        self.parser = loader.load_parser(self.simple_formatters, self.complex_formatters)

    def format(self, text, **kwargs):
        """Format BBCode text.

        Args:
            text (str): Text
        """

        return self.parser.format(text=text, **kwargs)
