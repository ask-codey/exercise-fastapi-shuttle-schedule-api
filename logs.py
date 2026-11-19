"""The shuttle API's logging: where log lines go, their format, and the filter that keeps secrets out of them.
setup_logging is ready; HideSecrets.filter is for you to finish.

HideSecrets is a filter on the handler that writes every logger's lines, so it sees every line before it's written.
It splits the line's message on single spaces and changes three kinds of word:

  a word that starts with password=    becomes  password=***
  a word that starts with token=       becomes  token=***
  the word right after the word Bearer becomes  ***

Every other word stays as it was. It puts the new message, its words joined with single spaces, in record.msg, sets
record.args to (), and returns True, so the line is still written. For example:

  logger.info("Sign-in form: username=%s password=%s", "ana", "correct-horse-staple")
  is written as  Sign-in form: username=ana password=***

  logger.info("Header Authorization: Bearer %s", "abc.def.ghi")
  is written as  Header Authorization: Bearer ***
"""
import logging


class HideSecrets(logging.Filter):
    def filter(self, record):
        # Hide the secrets the description above lists, then keep the line.
        return True


def setup_logging(level):
    """Writes every logger's lines to the terminal at level and louder, as TIME LEVEL LOGGER: MESSAGE, through
    HideSecrets. Ready to use: main.py calls it once, with settings.log_level."""
    handler = logging.StreamHandler()
    handler.addFilter(HideSecrets())
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s", handlers=[handler])
