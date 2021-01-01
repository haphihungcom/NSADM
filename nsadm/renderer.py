"""Render dispatches from templates.
"""

import logging

import jinja2

from nsadm import exceptions
from nsadm import bb_parser
from nsadm import utils


logger = logging.getLogger(__name__)


class DispatchJinjaLoader(jinja2.BaseLoader):
    """Wrapper around dispatch loader for Jinja environment.
    """

    def __init__(self, dispatch_loader):
        self.dispatch_loader = dispatch_loader

    def get_source(self, environment, template):
        try:
            text = self.dispatch_loader.get_dispatch_text(template)
        except exceptions.LoaderError as err:
            if not err.suppress_nsadm_error:
                logger.error('Text %s "%s" of dispatch "%s" not found.')
            raise exceptions.DispatchRenderingError from err

        return text, template, True


class TemplateRenderer():
    """Render a dispatch template.

        Args:
            dispatch_loader (str): Dispatch loader plugin.
            filter_path (str): Path to filters file.
    """

    def __init__(self, dispatch_loader, filter_path):
        self.filter_path = filter_path
        template_loader = DispatchJinjaLoader(dispatch_loader)
        # Make access to undefined context variables generate logs.
        undef = jinja2.make_logging_undefined(logger=logger)
        self.env = jinja2.Environment(loader=template_loader, trim_blocks=True, undefined=undef)

    def load_filters(self):
        """Load all filters if filter path is set.
        """

        if self.filter_path is not None:
            filters = utils.get_funcs(self.filter_path)
            if filters is None:
                logger.info('Filter file not found!')
            else:
                loaded_filters = {}
                for jinja_filter in filters:
                    loaded_filters[jinja_filter[0]] = jinja_filter[1]
                    logger.debug('Loaded filter "%s"', jinja_filter[0])
                self.env.filters.update(loaded_filters)
                logger.info('Loaded all custom filters')

    def render(self, name, context):
        """Render a dispatch template.

        Args:
            name (str): Dispatch template name.
            context (dict): Context for the template.

        Returns:
            str: Rendered template.
        """

        return self.env.get_template(name).render(context)


class DispatchRenderer():
    """Render dispatches from templates and process custom BBCode tags.

    Args:
        dispatch_loader: Dispatch loader
        var_loader: Var loader
        bb_config (dict): BBCode parser configuration
        template_config (dict): Template renderer configuration
    """

    def __init__(self, dispatch_loader, var_loader, bb_config, template_config):
        self.template_renderer = TemplateRenderer(dispatch_loader,
                                                  template_config.get('filter_path', None))

        self.bb_parser = bb_parser.BBParser(bb_config.get('simple_formatter_path', None),
                                            bb_config.get('complex_formatter_path', None),
                                            bb_config.get('complex_formatter_config_path', None))

        self.var_loader = var_loader

        # Context all dispatches will have
        self.global_context = {}

    def load(self, dispatch_config):
        """Load template renderer filters, BBCode formatters, and setup context.
        Args:
            dispatch_config (dict): Dispatch config
        """

        self.template_renderer.load_filters()
        self.bb_parser.load_formatters()

        self.global_context = self.var_loader.get_all_vars()
        self.global_context['dispatch_info'] = utils.get_dispatch_info(dispatch_config)

    def render(self, name):
        """Render a dispatch.

        Args:
            name (str): Dispatch name.

        Returns:
            str: Rendered dispatch.
        """

        context = self.global_context
        context['current_dispatch'] = name

        rendered = self.template_renderer.render(name, context)
        rendered = self.bb_parser.format(rendered, **context)

        logger.debug('Rendered dispatch "%s"', name)

        return rendered
