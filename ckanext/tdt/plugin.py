import requests
import ckan.plugins as p
import json
import urllib2
import simplejson

from ckan.logic import get_action
import ckan.logic.action.update
from ckan import model
from logging import getLogger
from pylons import config
import ckan.lib.helpers as h

log = getLogger(__name__)

class TDTPlugin(p.SingletonPlugin):
    """This plugin hooks in when a data package has been added.
       The resulting package will be investigated for The DataTank readable sources.
       When a match has been found, the dataset will be added to The DataTank and the URI in CKAN will change
    """

    # inheriting from IDomainObjectModification makes sure that we get notifications about updates with resources
    #p.implements(p.IDomainObjectModification)
    # IConfigurable makes sure we can reuse the config class
    p.implements(p.IConfigurable)
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IResourcePreview, inherit=True)
    p.implements(p.ITemplateHelpers, inherit=True)
    p.implements(p.IResourceController, inherit=True)

    def configure(self, config):
        self.tdt_user = config.get("tdt.user","admin")
        self.tdt_host = config.get("tdt.host","http://localhost/")
        self.tdt_mandatory_params = config.get("tdt.mandatory_params","")
        #TODO make sure host always end with /
        self.tdt_pass = config.get("tdt.pass","admin")

        req = urllib2.Request(self.tdt_host+"discovery")
        opener = urllib2.build_opener()
        f = opener.open(req)
        self.tdtDiscovery = json.load(f)

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

        resourceProps = data_dict.get('resource')
        tdt_uri = resourceProps.get('tdt_uri')
        if resourceProps.get('enable-tdt') == 'on' and tdt_uri and tdt_uri != "None":
            # don't do a remote check each time - too time consuming
            #r = requests.get(tdt_uri)
            #if r.status_code != 200: log.info(str(r.status_code) +" on "+tdt_uri+" : "+ r.text)
            #return r.status_code == 200
            if p.toolkit.check_ckan_version('2.1'): return {'can_preview': True, 'quality': 2}
            else: return True
        else:
            return False

    def preview_template(self, context, data_dict):
        return 'dataviewer/tdt.html'

    def setup_template_variables(self, context, data_dict):
        p.toolkit.c.jsondump = json.dumps
        p.toolkit.c.tdt_host = self.tdt_host
        p.toolkit.c.tdt_mandatory_params = self.tdt_mandatory_params
        p.toolkit.c.id = data_dict["resource"]["id"]
        p.toolkit.c.name = data_dict["resource"]["name"]
        p.toolkit.c.tdt_subdir = config.get('ckan.site_id', 'ckan').strip()


    def after_create(self, context, resource):
        self.create_tdt_source(resource)

        ckan.logic.action.update.resource_update(context, resource)

    def before_update(self, context, current, resource):
        #context['session'].begin(subtransactions=True)

        #entity = context['model'].Resource.get(context['resource'].id)
        self.create_tdt_source(resource)
        #entity.save()

    def create_tdt_source(self, entity_dict):
        """This method should add a resource configuration to The DataTank and return the uri
        """

        # WARN if this is caused by a resource update with a name change, this will create a new TDT resource,
        # but previous one will not be deleted  -- phd, 23-12-2013

        # This should change towards a configurable array of supported formats
        if( 'enable-tdt' in entity_dict and
            entity_dict['enable-tdt'] == 'on' and
            'format' in entity_dict and
            #( entity.format.lower() == "xml" or entity.format.lower() == "json")
                    entity_dict['format'].lower() in self.tdtDiscovery['resources']['definitions']['methods']['put']['body']
          ):
            log.info("Adding to The DataTank since we have "+entity_dict['format'])
            # !! entity.name is not necessarily set in CKAN
            if(entity_dict['name'] == ""):
                entity_dict['name'] = "unnamed"
            tdt_uri = self.tdt_host + "api/definitions/" + config.get('ckan.site_id', 'ckan').strip()+"/" + entity_dict['id']
            log.info(tdt_uri)

            tdt_data = {'description': entity_dict['description'] or 'No description provided','uri':entity_dict['url'], 'type': entity_dict['format'].lower() }
            for field in entity_dict :
                if field.startswith('tdt-') and entity_dict[field]: tdt_data[field[4:]] = entity_dict[field]

            r = requests.put(tdt_uri,
                             auth=(self.tdt_user, self.tdt_pass),
                             data=json.dumps(tdt_data),
                             headers={'Content-Type' : 'application/tdt.definition+json' })


            if(r.status_code >= 200 and r.status_code < 300):
                #log.info(r.headers["content-location"])
                entity_dict['tdt_uri']=self.tdt_host + config.get('ckan.site_id', 'ckan').strip()+"/" + entity_dict['id']
            elif (r.status_code == 405):
                # store the field anyway even if the request fails - temp fix for 405 errors
                log.warn("TDT 405 Err: Dataset - \""+ entity_dict['name'] +"\" [" +tdt_uri+ "] : "+r.text)
                entity_dict['tdt_uri']=self.tdt_host + config.get('ckan.site_id', 'ckan').strip()+"/" + entity_dict['id']
            else:
                log.error("Could not add dataset - \""+ entity_dict['name'] +"\" - to The DataTank")
                log.error(str(r.status_code) + " [" +tdt_uri+ "] : "+r.text)
                log.error("Sent message >>> "+json.dumps(tdt_data)+" <<<")
                h.flash_error("TDT Error : "+r.text)
        else:
            entity_dict.pop("tdt_uri", None)
        return
    
    def delete_tdt_source(self,entity):
        """This method removes an entity from The DataTank
        """
        r = requests.put(self.tdt_host + "api/definitions/"+config.get('ckan.site_id', 'ckan').strip()+"/" + entity.id, auth=(self.tdt_user, self.tdt_pass))
        log.info(r.status_code)
        return

    def getTdtHost(self):
        return self.tdt_host

    def getMandatoryParams(self):
        return self.tdt_mandatory_params

    def get_helpers(self):
        return {
            'jsondump' : json.dumps,
            'tdt_host' : self.getTdtHost,
            'tdt_mandatory_params' : self.getMandatoryParams
        }

