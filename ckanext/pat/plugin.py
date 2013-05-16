import os
import logging
from ckan.logic.converters import convert_to_extras,\
    convert_from_extras, convert_to_tags, convert_from_tags, free_tags_only,\
    date_to_db, date_to_form
from ckan.logic import get_action, check_access
from ckan.logic.schema import form_to_db_package_schema, db_to_form_package_schema
from ckan.lib.base import c
from ckan.plugins import IDatasetForm, IConfigurer, IPackageController
from ckan.plugins import implements, SingletonPlugin
from ckan.lib.navl.validators import ignore_missing, keep_extras, not_empty
from ckan import model, authz
from datetime import datetime
from ckan.lib import base
from ckan.controllers.api import NotAuthorized

log = logging.getLogger(__name__)

METADATA = ('Titolare', 'Categorie', 'Descrizione campi', 'Copertura Geografica', 'Copertura Temporale (Data di inizio)', 
            'Copertura Temporale (Data di fine)', 'Aggiornamento', 'Data di pubblicazione', 'Data di aggiornamento',
            'Codifica Caratteri', 'Data di creazione', 'URL sito') 

UPDATING = ('Non programmato', 'Continuo', 'Orario', 'Giornaliero', 'Settimanale', 
            'Mensile', 'Annuale', 'Non definito', 'Dataset costante')
FORMATS = ('Comma Separated Value (CSV)',
           'Geographic Markup Language (GML)',
           'Keyhole Markup Language (KML)',
           'Open Documento Format per dati tabellari (ODS)',
           'Resource Desription Format (RDF)',
           'ESRI Shapefile (SHP)',
           'Tab Separated Value (TSV)',
           'Extensible Markup Language (XML)')
ENCODINGS = ('Latin-1', 'PC-850', 'UTF-8')

CATEGORY_VOCAB = u'category_vocab'
HOLDERS_VOCAB = u'holders_vocab'
COVERAGE_VOCAB = u'coverage_vocab'
DATEFIELDS = ['Copertura Temporale (Data di inizio)', 'Copertura Temporale (Data di fine)', 'Data di pubblicazione', 'Data di creazione', 'Data di aggiornamento']
ISOEXTENSION = '_iso'
VIEWFIELDS = ['Titolare', 'Referente', 'Contatto', 'Documentazione tecnica', 'Descrizione campi', 'Copertura Geografica', 'Copertura Temporale (Data di inizio)', 'Copertura Temporale (Data di fine)', 'Aggiornamento', 'Data di pubblicazione', 'Data di aggiornamento', 'Codifica Caratteri', 'Autore', 'Email autore', 'Data di creazione', 'URL sito']

class PatDatasetForm(SingletonPlugin):
    """This plugin demonstrates how a theme packaged as a CKAN
    extension might extend CKAN behaviour.

    In this case, we implement these extension interfaces:

      - ``IConfigurer`` allows us to override configuration normally
        found in the ``ini``-file.  Here we use it to specify where the
        form templates can be found.
      - ``IDatasetForm`` allows us to provide a custom form for a dataset
        based on the type_name that may be set for a package.  Where the
        type_name matches one of the values in package_types then this
        class will be used.
    """
    implements(IDatasetForm, inherit=True)
    implements(IConfigurer, inherit=True)
    implements(IPackageController, inherit=True)

    #IConfigurer implementation

    def update_config(self, config):
        """
        This IConfigurer implementation causes CKAN to look in the
        ```templates``` directory when looking for the package_form()
        """
        here = os.path.dirname(__file__)
        rootdir = os.path.dirname(os.path.dirname(here))
        our_public_dir = os.path.join(rootdir, 'ckanext', 'pat', 'theme', 'public')
        template_dir = os.path.join(rootdir, 'ckanext', 'pat', 'theme', 'templates')
        # set our local template and resource overrides
        config['extra_public_paths'] = ','.join([our_public_dir,
                config.get('extra_public_paths', '')])
        config['extra_template_paths'] = ','.join([template_dir,
                config.get('extra_template_paths', '')])
        # add in the extra.css
        config['ckan.template_head_end'] = config.get('ckan.template_head_end', '') +\
               '<link rel="stylesheet" href="/css/extra.css" type="text/css"> '
               
               
    #IDatasetForm implementation
     
    def new_template(self):
        """
        Returns a string representing the location of the template to be
        rendered for the new page
        """
        return 'package/new.html'

    def comments_template(self):
        """
        Returns a string representing the location of the template to be
        rendered for the comments page
        """
        return 'package/comments.html'

    def search_template(self):
        """
        Returns a string representing the location of the template to be
        rendered for the search page (if present)
        """
        return 'package/search.html'

    def read_template(self):
        """
        Returns a string representing the location of the template to be
        rendered for the read page
        """
        return 'package/read.html'

    def history_template(self):
        """
        Returns a string representing the location of the template to be
        rendered for the history page
        """
        return 'package/history.html'

    def package_form(self):
        return 'package/new_package_form.html'

    def is_fallback(self):
        """
        Returns true iff this provides the fallback behaviour, when no other
        plugin instance matches a package's type.

        As this is not the fallback controller we should return False.  If
        we were wanting to act as the fallback, we'd return True
        """
        return True

    def package_types(self):
        """
        Returns an iterable of package type strings.

        If a request involving a package of one of those types is made, then
        this plugin instance will be delegated to.

        There must only be one plugin registered to each package type.  Any
        attempts to register more than one plugin instance to a given package
        type will raise an exception at startup.
        """
        return ['dataset']

    def db_to_form_schema(self):
        """
        Returns the schema for mapping package data from the database into a
        format suitable for the form (optional)
        """
        schema = db_to_form_package_schema()
        
        schema.update({
            'tags': {
                '__extras': [keep_extras, free_tags_only]
            },
            'id': [not_empty],
            'license_url': [not_empty],
            'license_title': [not_empty],
            'isopen': [not_empty],
            'Titolare': [convert_from_extras, ignore_missing],
            'Descrizione campi': [convert_from_extras, ignore_missing],
            'Categorie': [convert_from_tags(CATEGORY_VOCAB), ignore_missing],
            'Copertura Geografica': [convert_from_extras, ignore_missing],
            'Copertura Temporale (Data di inizio)': [convert_from_extras, ignore_missing, date_to_form],
            'Copertura Temporale (Data di fine)': [convert_from_extras, ignore_missing, date_to_form],
            'Aggiornamento': [convert_from_extras, ignore_missing],
            'Data di pubblicazione': [convert_from_extras, ignore_missing, date_to_form],
            'Data di aggiornamento': [convert_from_extras, ignore_missing, date_to_form],
            'Codifica Caratteri': [convert_from_extras, ignore_missing],
            'Data di creazione': [convert_from_extras, ignore_missing],
            'URL sito': [convert_from_extras, ignore_missing],
            'DATEFIELDS': [ignore_missing],
            'VIEWFIELDS': [ignore_missing],
            'view_fields': [ignore_missing],
        })
        
        for field in DATEFIELDS:
            schema.update({field+ISOEXTENSION: [ignore_missing]})
        
        return schema

    def form_to_db_schema(self):
        """
        Returns the schema for mapping package data from a form to a format
        suitable for the database.
        """
        schema = form_to_db_package_schema()
        schema.update({
            'license_id': [not_empty],
            'Titolare': [not_empty, convert_to_extras],
            'Descrizione campi': [not_empty, convert_to_extras],
            'Categorie': [ignore_missing, convert_to_tags(CATEGORY_VOCAB)],
            'Copertura Geografica': [not_empty, convert_to_extras],
            'Copertura Temporale (Data di inizio)': [not_empty, convert_to_extras, date_to_db],
            'Copertura Temporale (Data di fine)': [convert_to_extras, date_to_db],
            'Aggiornamento': [not_empty, convert_to_extras],
            'Data di pubblicazione': [not_empty, convert_to_extras, date_to_db],
            'Data di aggiornamento': [not_empty, convert_to_extras, date_to_db],
            'Codifica Caratteri': [not_empty, convert_to_extras],
            'Data di creazione': [convert_to_extras],
            'URL sito': [convert_to_extras],
            'maintainer': [not_empty, unicode],
            'maintainer_email': [not_empty, unicode],
        })
        schema['groups']['capacity'] = [ignore_missing, unicode]
        return schema
    
    def form_to_db_schema_options(self, options):
        ''' This allows us to select different schemas for different
        purpose eg via the web interface or via the api or creation vs
        updating. It is optional and if not available form_to_db_schema
        should be used.
        If a context is provided, and it contains a schema, it will be
        returned.
        '''
        
        schema = options.get('context',{}).get('schema',None)
        if schema:
            schema.update({'Categorie': [ignore_missing, convert_to_tags(CATEGORY_VOCAB)]})
            return schema

        if options.get('api'):
            if options.get('type') == 'create':
                return self.form_to_db_schema_api_create()
            else:
                assert options.get('type') == 'update'
                return self.form_to_db_schema_api_update()
        else:
            return self.form_to_db_schema()

    def check_data_dict(self, data_dict, schema=None):
        '''Check if the return data is correct, mostly for checking out
        if spammers are submitting only part of the form'''
        in_formats = ('%Y/%m/%dT%H:%M:%S', '%Y/%m/%dT%H:%M:%S.%f')
        out_format = '%d/%m/%Y'
        for field in DATEFIELDS:
            if data_dict.has_key(field):
                data = data_dict[field]
                result = None
                if data:
                    data = data.replace("-", "/")
                    for in_format in in_formats:
                        try:
                            result = datetime.strptime(data, in_format)
                        except ValueError:
                            continue
                if result:
                    data_dict[field] = result.strftime(out_format)

    def setup_template_variables(self, context, data_dict):
        from pylons import config
        data_dict.update({'available_only': True})
        
        c.groups_available = c.userobj and \
            c.userobj.get_groups('organization') or []
        c.licences = [('', '')] + base.model.Package.get_license_options()
        c.is_sysadmin = authz.Authorizer().is_sysadmin(c.user)
        
        c.metadata = METADATA
        register = model.Package.get_license_register()
        #licences = [(l.title, l.id) for l in register.values() if l.id in ('cc-zero', 'cc-by')]
        #c.licences = licences 
        c.licence_default = c.licences[2]
        c.holders = get_action('tag_list')(context, {'vocabulary_id': HOLDERS_VOCAB})
        c.categories = get_action('tag_list')(context, {'vocabulary_id': CATEGORY_VOCAB})
        c.geographic_coverages = get_action('tag_list')(context, {'vocabulary_id': COVERAGE_VOCAB})
        c.updating = UPDATING
        c.updating_default = UPDATING[0]
        c.formats = FORMATS
        c.encodings = ENCODINGS
        c.encodings_default = ENCODINGS[2]
        #c.Data di creazione_default = datetime.now().strftime('%d/%m/%Y');

        ## This is messy as auths take domain object not data_dict
        context_pkg = context.get('package', None)
        pkg = context_pkg or c.pkg
        if pkg:
            try:
                if not context_pkg:
                    context['package'] = pkg
                check_access('package_change_state', context)
                c.auth_for_change_state = True
            except NotAuthorized:
                c.auth_for_change_state = False


    #IPackageController implementation
    
    def before_view(self, pkg_dict):
        def _lookup_field(pkg_dict, field):
            for h in pkg_dict['extras']:
                if h.get('key', '') == field:
                    return h.get('value', '')
            return None
        in_formats = ('%d/%m/%Y %H:%M', '%H:%M %d/%m/%Y', '%d/%m/%Y', '%m/%Y', '%Y')
        out_format = '%Y/%m/%d'
        for field in DATEFIELDS:
            if pkg_dict.has_key(field):
                data = pkg_dict[field]
            else:
                data = _lookup_field(pkg_dict, field)
                
            result = None
            if data:
                data = data.replace("-", "/")
                for in_format in in_formats:
                        try:
                                result = datetime.strptime(data, in_format)
                        except ValueError:
                                continue
            if result:
                pkg_dict[field+ISOEXTENSION] = result.strftime(out_format)
            else:
                pkg_dict[field+ISOEXTENSION] = None
        pkg_dict['DATEFIELDS'] = DATEFIELDS
        
        pkg_dict['VIEWFIELDS'] = VIEWFIELDS
        
        pat_view = [
                    ('Titolare', _lookup_field(pkg_dict, 'Titolare')),
                    ('Referente', pkg_dict['maintainer']),
                    ('Contatto', pkg_dict['maintainer_email']),
                    ('Documentazione tecnica', pkg_dict['url']),
                    ('Descrizione campi', _lookup_field(pkg_dict, 'Descrizione campi')),
                    ('Copertura Geografica', _lookup_field(pkg_dict, 'Copertura Geografica')),
                    ('Copertura Temporale (Data di inizio)', _lookup_field(pkg_dict, 'Copertura Temporale (Data di inizio)')),
                    ('Copertura Temporale (Data di fine)', _lookup_field(pkg_dict, 'Copertura Temporale (Data di fine)')),
                    ('Aggiornamento', _lookup_field(pkg_dict, 'Aggiornamento')),
                    ('Data di pubblicazione', _lookup_field(pkg_dict, 'Data di pubblicazione')),
                    ('Data di aggiornamento', _lookup_field(pkg_dict, 'Data di aggiornamento')),
                    ('Codifica Caratteri', _lookup_field(pkg_dict, 'Codifica Caratteri')),
                    ('Autore', pkg_dict['author']),
                    ('Email autore', pkg_dict['author_email']),
                    ('Data di creazione', _lookup_field(pkg_dict, 'Data di creazione')),
                    ('URL sito', _lookup_field(pkg_dict, 'URL sito')),
                    ]

        pkg_dict['view_fields'] = pat_view
        
        return pkg_dict
