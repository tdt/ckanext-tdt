import requests
import ckan.plugins as p
import json

from ckan.logic import get_action
from ckan import model
from logging import getLogger
from pylons import config

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
        self.tdt_user = config.get("tdt.user","admin")
        self.tdt_host = config.get("tdt.host","http://localhost/")
        #TODO make sure host always end with /
        self.tdt_pass = config.get("tdt.pass","admin")

    def update_config(self, config):
        p.toolkit.add_public_directory(config, 'public')
        p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_resource('public', 'ckanext-tdt')

    def notify(self, entity, operation=None):
        # Make sure we're working with a Resource
        if isinstance(entity, model.Resource):
            if operation:
                if operation == model.domain_object.DomainObjectOperation.deleted:
                    self.delete_tdt_source(entity)
                else:
                    self.create_tdt_source(entity)
        return

    def can_preview(self, data_dict):
        """ This function will test whether the resource exists at TDT's side and if it returns a nice HTTP 200 OK
        """
        rid = data_dict["resource"]["id"]
        rname = data_dict["resource"]["name"]
        if(rname == ""):
            rname = "unnamed"

        tdt_uri = self.tdt_host + config.get('ckan.site_id', 'ckan').strip()+ "/" + rid
        for key,v in data_dict.get('resource').items():
            if key == "tdt_uri":
                tdt_uri = v

        if tdt_uri:
            r = requests.get(tdt_uri)
            if r.status_code != 200: log.info(str(r.status_code) +" on "+tdt_uri+" : "+ r.text)
            return r.status_code == 200
        else:
            return False

    def preview_template(self, context, data_dict):
        return 'dataviewer/tdt.html'

    def setup_template_variables(self, context, data_dict):
        p.toolkit.c.tdt_host = self.tdt_host
        p.toolkit.c.id = data_dict["resource"]["id"]
        p.toolkit.c.name = data_dict["resource"]["name"]
        p.toolkit.c.tdt_subdir = config.get('ckan.site_id', 'ckan').strip()


    def create_tdt_source(self, entity):
        """This method should add a resource configuration to The DataTank and return the uri
        """

        # WARN if this is caused by a resource update with a name change, this will create a new TDT resource,
        # but previous one will not be deleted  -- phd, 23-12-2013

        # This should change towards a configurable array of supported formats
        if(hasattr(entity, 'format') and ( entity.format.lower() == "xml" or entity.format.lower() == "json")):
            log.info("Adding to The DataTank since we have an XML or a JSON")
            # !! entity.name is not necessarily set in CKAN
            if(entity.name == ""):
                entity.name = "unnamed"
            tdt_uri = self.tdt_host + "api/definitions/" + config.get('ckan.site_id', 'ckan').strip()+"/" + entity.id
            log.info(tdt_uri)
            r = requests.put(tdt_uri,
                             auth=(self.tdt_user, self.tdt_pass),
                             data=json.dumps({'description': entity.description,'uri':entity.url }),
                             headers={'Content-Type' : 'application/tdt.' + entity.format.lower() })

            # store the field anyway even if the request fails - temp fix for 405 errors
            entity.extras['tdt_uri']=self.tdt_host + config.get('ckan.site_id', 'ckan').strip()+"/" + entity.id


            if(r.status_code >= 200 and r.status_code < 300):
                log.info(r.headers["content-location"])
            else:
                log.error("Could not add dataset - \""+ entity.name +"\" - to The DataTank")
                log.error(str(r.status_code) + " [" +tdt_uri+ "] : "+r.text)

        return
    
    def delete_tdt_source(self,entity):
        """This method removes an entity from The DataTank
        """
        r = requests.put(self.tdt_host + "api/definitions/"+config.get('ckan.site_id', 'ckan').strip()+"/" + entity.id, auth=(self.tdt_user, self.tdt_pass))
        log.info(r.status_code)
        return

