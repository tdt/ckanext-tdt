import os
from logging import getLogger

from pylons import request

from ckan.plugins import implements, SingletonPlugin

log = getLogger(__name__)


class TDTPlugin(SingletonPlugin):
    """This plugin hooks in when a data package has been added.
       The resulting package will be investigated for The DataTank readable sources.
       When a match has been found, the dataset will be added to The DataTank and the URI in CKAN will change
    """

    def after_create(self, pkg_dict):
        """This method is called upon after a dataset package has been created.
        """

        ## STUB

        # return ???
