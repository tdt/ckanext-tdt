import requests
import ckan.plugins as p
from ckan import model

from logging import getLogger

log = getLogger(__name__)

log.info("Loading TDT Plugin class")

class TDTPlugin(p.SingletonPlugin):
    """This plugin hooks in when a data package has been added.
       The resulting package will be investigated for The DataTank readable sources.
       When a match has been found, the dataset will be added to The DataTank and the URI in CKAN will change
    """

    # inheriting from IDomainObjectModification makes sure that we get notifications about updates with resources
    p.implements(p.IDomainObjectModification)

    def notify(self, entity, operation=None):
        # Make sure we're working with a Resource
        if isinstance(entity, model.Resource):
            self.create_tdt_source(entity)
        return


    def create_tdt_source(self, entity):
        """This method should add a resource configuration to The DataTank and return the uri
        """
        log.info(entity)
        if(hasattr(entity, 'format') and entity.format.lower() == "itsps"):
            log.info("We have an ITS PS FILE! Let's do a request!")
            r = requests.put("http://localhost/test", data="testing - check access.log afterwards")
            log.info(r.status_code)

        return
