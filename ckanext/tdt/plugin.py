import requests
import ckan.plugins as p
from ckan.logic import get_action
from ckan import model
from logging import getLogger

log = getLogger(__name__)

class TDTPlugin(p.SingletonPlugin):
    """This plugin hooks in when a data package has been added.
       The resulting package will be investigated for The DataTank readable sources.
       When a match has been found, the dataset will be added to The DataTank and the URI in CKAN will change
    """

    # inheriting from IDomainObjectModification makes sure that we get notifications about updates with resources
    p.implements(p.IDomainObjectModification)
    # IConfigurable makes sure we can reuse the config class
    p.implements(p.IConfigurable)
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IResourcePreview, inherit=True)

    def configure(self, config):
        self.tdt_user = config.get("tdt.user","tdtadmin")
        self.tdt_host = config.get("tdt.host","http://localhost/")
        self.tdt_pass = config.get("tdt.pass","...")

    def update_config(self, config):
        p.toolkit.add_public_directory(config, 'public')
        p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_resource('public', 'ckanext-tdt')

    def notify(self, entity, operation=None):
        # Make sure we're working with a Resource
        if isinstance(entity, model.Resource):
            ## TODO: check whether we aren't deleting
            self.create_tdt_source(entity)
        return

    def can_preview(self, data_dict):
        log.info(data_dict)
        return True

    def preview_template(self, context, data_dict):
        return 'dataviewer/tdt.html'

    def create_tdt_source(self, entity):
        """This method should add a resource configuration to The DataTank and return the uri
        """
        log.debug(entity)
        # This should change towards a configurable array of supported formats
        if(hasattr(entity, 'format') and ( entity.format.lower() == "xml" or entity.format.lower() == "json")):
            log.info("We have an XML or a JSON file! Let's do a request!")
            # !! entity.name is not necessarily set in CKAN
            if(entity.name == ""):
                entity.name = "unnamed"

            tdt_uri = self.tdt_host + "/tdtadmin/resources/ckan/" + entity.id + "/" + entity.name
            r = requests.put(tdt_uri,
                             auth=(self.tdt_user, self.tdt_pass),
                             data="resource_type=generic&generic_type=" + entity.format.upper() + "&documentation=" + entity.description +"&uri=" + entity.url)
            

            if(r.status_code == 200):
                log.info(r.headers["content-location"])
                entity.extras["tdt-url"] = r.headers["content-location"]
                #TODO: store the entity in the back-end of CKAN

                #get_action('resource_update')(context, entity)

            elif (r.status_code > 200):
                log.error("Could not add dataset \""+ entity.name +"\" to The DataTank")
                log.error(r.status_code)
        return
    
    def delete_tdt_source(self,entity):
        """This method removes an entity from The DataTank
        """
        r = requests.put(self.tdt_host + "/tdtadmin/resources/ckan/" + entity.id, auth=(self.tdt_user, self.tdt_pass))
        log.info(r.status_code)
        return
