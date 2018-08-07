import botocore

from trailblazer.__about__ import __version__


# Create custom botocore session with a custom config
botocore_config = botocore.config.Config(
    parameter_validation = False,
    user_agent = 'Trailblazer/{}'.format(__version__)
)
