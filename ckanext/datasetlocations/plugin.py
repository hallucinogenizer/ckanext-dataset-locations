import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from collections import OrderedDict


def create_locations():
    user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
    context = {'user': user['name']}
    try:
        data = {'id': 'locations'}
        toolkit.get_action('vocabulary_show')(context, data)
    except toolkit.ObjectNotFound:
        data = {'name': 'locations'}
        vocab = toolkit.get_action('vocabulary_create')(context, data)
        for tag in (u'Islamabad', u'Karachi', u'Multan', u'Peshawar'):
            data = {'name': tag, 'vocabulary_id': vocab['id']}
            toolkit.get_action('tag_create')(context, data)

def locations():
    create_locations()
    try:
        tag_list = toolkit.get_action('tag_list')
        current_locations = tag_list(data_dict={'vocabulary_id': 'locations'})
        return current_locations
    except toolkit.ObjectNotFound:
        return None


class DatasetCategoriesPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IFacets)

    def update_config(self, config):
        pass

    def dataset_facets(self, facets_dict, package_type):
        # facets_dict['category'] = toolkit._('Category')
        facets = OrderedDict()
        facets['category'] = toolkit._('Categories')
        facets['locations'] = toolkit._('Locations')
        facets['tags']=toolkit._('Tags')
        facets['res_format']=toolkit._('Formats')
        facets['organization'] = toolkit._('Organizations')
        return facets

class DatasetlocationsPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'datasetlocations')

    # IDatasetForm
    def get_helpers(self):
        return {'locations': locations}

    def create_package_schema(self):
        # let's grab the default schema in our plugin
        schema = super(DatasetlocationsPlugin, self).create_package_schema()
        # our custom field
        schema.update({
            'locations': [toolkit.get_validator('ignore_missing'),
                            toolkit.get_converter('convert_to_extras')]
        })
        return schema

    def update_package_schema(self):
        schema = super(DatasetlocationsPlugin, self).update_package_schema()
        # our custom field
        schema.update({
            'locations': [toolkit.get_validator('ignore_missing'),
                            toolkit.get_converter('convert_to_extras')]
        })
        return schema

    def _modify_package_schema(self, schema):
        schema.update({
            'locations': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_tags')('locations')
            ]
        })
        return schema

    def show_package_schema(self):
        schema = super(DatasetlocationsPlugin, self).show_package_schema()

        schema['tags']['__extras'].append(toolkit.get_converter('free_tags_only'))
        schema.update({
            'locations': [
                toolkit.get_converter('convert_from_tags')('locations'),
                toolkit.get_validator('ignore_missing')]
            })
        return schema

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return False

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []
