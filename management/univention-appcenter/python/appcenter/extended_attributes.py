#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#
# Univention App Center
#  univention-app wrapper for udm's settings/extended_attributes
#
# Copyright 2016-2019 Univention GmbH
#
# http://www.univention.de/
#
# All rights reserved.
#
# The source code of this program is made available
# under the terms of the GNU Affero General Public License version 3
# (GNU AGPL V3) as published by the Free Software Foundation.
#
# Binary versions of this program provided by Univention to you as
# well as other copyrighted, protected or trademarked materials like
# Logos, graphics, fonts, specific documentations and configurations,
# cryptographic keys etc. are subject to a license agreement between
# you and Univention and not subject to the GNU AGPL V3.
#
# In the case you use this program under the terms of the GNU AGPL V3,
# the program is provided in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License with the Debian GNU/Linux or Univention distribution in file
# /usr/share/common-licenses/AGPL-3; if not, see
# <http://www.gnu.org/licenses/>.
#

import os
import re

from univention.appcenter.app import CaseSensitiveConfigParser
from univention.appcenter.log import get_base_logger
from univention.appcenter.meta import UniventionMetaClass, UniventionMetaInfo
from univention.appcenter.ucr import ucr_get
from univention.appcenter.udm import create_object_if_not_exists, create_recursive_container, remove_object_if_exists, modify_object
from univention.appcenter.utils import underscore, get_md5, read_ini_file


attribute_logger = get_base_logger().getChild('attributes')


class Attribute(UniventionMetaInfo):
	pop = True
	save_as_list = '_attrs'
	auto_set_name = True

	def ldap_name(self):
		return self.name.upper().replace('_', '-')

	def escape_value(self, value):
		return value

	def to_schema(self, obj):
		name = self.ldap_name()
		value = self.get_value(obj)
		if value is not None:
			return "%s %s" % (name, value)

	def get_value(self, obj):
		return self.escape_value(getattr(obj, self.name))


class HiddenAttribute(Attribute):
	def to_schema(self, obj):
		return None


class StringAttribute(Attribute):
	def escape_value(self, value):
		return "'%s'" % value


class DescAttribute(StringAttribute):
	def ldap_name(self):
		return 'DESC'

	def escape_value(self, value):
		return super(DescAttribute, self).escape_value(value or 'Attribute created by the App Center integration for Extended Attributes')


class BooleanAttribute(Attribute):
	def to_schema(self, obj):
		value = self.get_value(obj)
		if value:
			return self.ldap_name()


class AttributeListAttribute(Attribute):
	def escape_value(self, value):
		values = sorted(val for val in set(re.split('\s*,\s*', value or '')) if val)
		if values:
			return '( ' + ' $ '.join(values) + ' )'


class SyntaxAttribute(Attribute):
	def to_schema(self, obj):
		ret = 'SYNTAX %s EQUALITY %s' % (obj._syntax, obj._equality)
		if obj._substr:
			ret = '%s SUBSTR %s' % (ret, obj._substr)
		return ret


class SchemaObject(object):
	__metaclass__ = UniventionMetaClass

	ldap_type = None
	ldap_type_oid_suffix = None

	oid = HiddenAttribute()
	name = StringAttribute()
	ldap_desc = DescAttribute()

	def __init__(self, app, **kwargs):
		for attr in self._attrs:
			setattr(self, attr.name, kwargs.get(attr.name))

	def to_schema(self):
		info = []
		for attr in self._attrs:
			attr_schema = attr.to_schema(self)
			if attr_schema:
				info.append(attr_schema)
		info = '\n    '.join(info)
		return '%(ldap_type)s ( %(oid)s\n    %(info)s\n    )' % {'ldap_type': self.ldap_type, 'oid': self.oid, 'info': info}

	def set_standard_oid(self, app, suffix):
		oid = '1.3.6.1.4.1.10176.5000'  # Univention OID + 5000 (= reserved for App Center)
		app_hash = str(int(get_md5(app.id), 16))
		while app_hash:
			new_prefix, app_hash = app_hash[:5], app_hash[5:]
			oid = '%s.%s' % (oid, int(new_prefix))
		self.oid = '%s.%s.%s' % (oid, self.ldap_type_oid_suffix, suffix)

	def __repr__(self):
		return '<%s(%s)>' % (type(self).__name__, ', '.join('%s=%r' % (attr.name, getattr(self, attr.name)) for attr in self._attrs))


class ExtendedAttribute(SchemaObject):
	ldap_type = 'attributetype'
	ldap_type_oid_suffix = 1

	description = HiddenAttribute()
	description_de = HiddenAttribute()
	long_description = HiddenAttribute()
	long_description_de = HiddenAttribute()

	syntax = SyntaxAttribute()
	single_value = BooleanAttribute()
	default = HiddenAttribute()

	module = HiddenAttribute()

	belongs_to = HiddenAttribute()
	position = HiddenAttribute()
	full_width = HiddenAttribute()
	disable_web = HiddenAttribute()
	copyable = HiddenAttribute()
	required = HiddenAttribute()
	options = HiddenAttribute()
	tab_name = HiddenAttribute()

	@property
	def dn(self):
		return 'cn=%s,%s,%s' % (self.name, self.position, ucr_get('ldap/base'))

	def __init__(self, app, **kwargs):
		if 'syntax' not in kwargs:
			kwargs['syntax'] = 'String'
		if 'belongs_to' not in kwargs:
			kwargs['belongs_to'] = '%sUser' % (app.id,)
		if 'position' not in kwargs:
			kwargs['position'] = 'cn=%s,cn=custom attributes,cn=univention' % app.id
		if 'module' not in kwargs:
			kwargs['module'] = 'users/user'
		if 'single_value' not in kwargs:
			kwargs['single_value'] = True
		if 'full_width' not in kwargs:
			kwargs['full_width'] = False
		if 'tab_name' not in kwargs:
			kwargs['tab_name'] = '    %s' % (app.name,)
		kwargs['module'] = re.split('\s*,\s*', kwargs['module'])
		if 'options' in kwargs:
			kwargs['options'] = re.split('\s*,\s*', kwargs.get('options', []))
		kwargs.setdefault('options', [])
		super(ExtendedAttribute, self).__init__(app, **kwargs)
		self._udm_syntax = None
		if self.syntax == 'Boolean':
			self._syntax = '1.3.6.1.4.1.1466.115.121.1.7'
			self._equality = 'booleanMatch'
			self._substr = None
			self._udm_syntax = 'TrueFalseUp'
		elif self.syntax == 'BooleanString':
			self._syntax = '1.3.6.1.4.1.1466.115.121.1.15'
			self._equality = 'caseIgnoreMatch'
			self._substr = 'caseIgnoreSubstringsMatch'
			self._udm_syntax = 'TrueFalseUp'
		elif self.syntax == 'String':
			self._syntax = '1.3.6.1.4.1.1466.115.121.1.15'
			self._equality = 'caseIgnoreMatch'
			self._substr = 'caseIgnoreSubstringsMatch'
			#self._syntax = '1.3.6.1.4.1.1466.115.121.1.26'
			#self._equality = 'caseIgnoreIA5Match'
			#self._substr = None
			self._udm_syntax = 'string'
		else:
			raise NotImplementedError('Syntax %r not supported' % self.syntax)


class ExtendedOption(SchemaObject):
	name = HiddenAttribute()
	position = HiddenAttribute()
	description = HiddenAttribute()
	long_description = HiddenAttribute()
	description_de = HiddenAttribute()
	long_description_de = HiddenAttribute()
	default = HiddenAttribute()
	editable = HiddenAttribute()
	module = HiddenAttribute()
	object_class = HiddenAttribute()

	def __init__(self, app, **kwargs):
		if 'position' not in kwargs:
			kwargs['position'] = 'cn=%s,cn=custom attributes,cn=univention' % app.id
		if 'module' not in kwargs:
			kwargs['module'] = 'users/user'
		kwargs.setdefault('editable', True)
		kwargs.setdefault('description', app.name)
		#kwargs.setdefault('object_class', kwargs['name'])
		kwargs['module'] = re.split('\s*,\s*', kwargs['module'])
		super(ExtendedOption, self).__init__(app, **kwargs)
		self.icon = '%s.svg' % (self.name,)

	@property
	def dn(self):
		return 'cn=%s,%s,%s' % (self.name, self.position, ucr_get('ldap/base'))


class ObjectClass(SchemaObject):
	ldap_type = 'objectclass'
	ldap_type_oid_suffix = 2

	auxiliary = BooleanAttribute()
	sup = Attribute()
	may = AttributeListAttribute()
	must = AttributeListAttribute()

	def __init__(self, app, **kwargs):
		if 'auxiliary' not in kwargs:
			kwargs['auxiliary'] = True
		if 'sup' not in kwargs:
			kwargs['sup'] = 'top'
		if 'may' not in kwargs:
			kwargs['may'] = ''
		if 'must' not in kwargs:
			kwargs['must'] = ''
		super(ObjectClass, self).__init__(app, **kwargs)


def get_extended_attributes(app):
	attributes = []
	object_classes = []
	extended_options = []
	parser = read_ini_file(app.get_cache_file('attributes'), CaseSensitiveConfigParser)
	object_class_suffix = 1
	attribute_suffix = 1
	for section in parser.sections():
		kwargs = dict([underscore(key), value] for key, value in parser.items(section))
		kwargs['name'] = section
		if kwargs.get('type') == 'ObjectClass':
			object_class = ObjectClass(app, **kwargs)
			if object_class.oid is None:
				object_class.set_standard_oid(app, object_class_suffix)
				object_class_suffix += 1
			attribute_logger.debug('Adding %s to list of classes' % section)
			object_classes.append(object_class)

			# for backwards compatibility with UCS 4.3 we can't use the new type == ExtendedOption, so this flag is the equivalent
			if kwargs.get('add_extended_option') == '1':
				okwargs = kwargs.copy()
				okwargs['name'] = kwargs.get('option_name', '%sUser' % (app.id,))
				okwargs.setdefault('object_class', object_class.name)
				option = ExtendedOption(app, **okwargs)
				attribute_logger.debug('Adding %s to list of options' % (okwargs['name'],))
				extended_options.append(option)
		elif kwargs.get('type') == 'ExtendedOption':  # Can't be used if System < UCS 4.4, use add_extended_option instead!
			option = ExtendedOption(app, **kwargs)
			attribute_logger.debug('Adding %s to list of options' % section)
			extended_options.append(option)
		elif kwargs.get('type') == 'ExtendedAttribute':
			attribute = ExtendedAttribute(app, **kwargs)
			attribute_logger.debug('Adding %s to list of attributes' % section)
			if attribute.oid is None:
				attribute.set_standard_oid(app, attribute_suffix)
				attribute_suffix += 1
			attributes.append(attribute)
		else:  # ignore, so that it is extensible for the future :-)
			attribute_logger.warn('Unknown attribute type for section %s: %r' % (section, kwargs.get('type')))

	if app.generic_user_activation:
		# TODO: remove this useless attribute, objectClass=appidUser should be enough for future apps
		attribute_name = app.generic_user_activation
		if attribute_name == 'Version1':  # backwards compatibility
			attribute_name = '%sActivated' % (app.id,)
			if attribute_name not in [attr.name for attr in attributes]:
				attribute_logger.debug('Adding %s to list of attributes' % attribute_name)
				attribute = ExtendedAttribute(app, name=attribute_name, description='Activate user for %s' % app.name, description_de='Nutzer für %s aktivieren' % app.name, syntax='Boolean')
				attribute.set_standard_oid(app, attribute_suffix)
				attribute.full_width = False
				attribute.disable_web = True  # important!
				attribute.default = True  # important! the boolean flag is the extended option, so this must be enabled
				attributes.insert(0, attribute)

		option_name = app.generic_user_activation
		if option_name is True:
			option_name = '%sUser' % (app.id,)
		if option_name not in [opt.name for opt in extended_options]:
			attribute_logger.debug('Adding %s to list of options' % option_name)
			option = ExtendedOption(app, name=option_name, object_class=option_name, long_description='Activate user for %s' % app.name, long_description_de='Nutzer für %s aktivieren' % app.name)
			extended_options.insert(0, option)

	for attribute in attributes:
		if attribute.belongs_to not in [obj.name for obj in object_classes]:
			class_name = attribute.belongs_to
			object_class = ObjectClass(app, name=class_name)
			object_class.set_standard_oid(app, object_class_suffix)
			object_class_suffix += 1
			object_classes.insert(0, object_class)
		object_class = [obj for obj in object_classes if obj.name == attribute.belongs_to][0]
		if attribute.name not in re.split('\s*,\s*', object_class.must):
			object_class.may = '%s, %s' % (object_class.may, attribute.name)
		if option in extended_options:
			if option.name == attribute.belongs_to:
				attribute.options.append(option.name)

	for option in extended_options:
		if option.object_class not in [obj.name for obj in object_classes]:
			class_name = option.object_class
			object_class = ObjectClass(app, name=class_name)
			object_class.set_standard_oid(app, object_class_suffix)
			object_class_suffix += 1
			object_classes.insert(0, object_class)

	return attributes, object_classes, extended_options


def get_schema(app):
	ret = []
	attributes, object_classes, __ = get_extended_attributes(app)
	for attribute in attributes:
		ret.append(attribute.to_schema())
	for object_class in object_classes:
		ret.append(object_class.to_schema())
	return '\n\n'.join(ret)


def create_extended_attribute(attribute, app, layout_position, lo, pos):
	attrs = {}
	attribute_position = '%s,%s' % (attribute.position, ucr_get('ldap/base'))
	create_recursive_container(attribute_position, lo, pos)
	pos.setDn(attribute_position)
	attrs['name'] = attribute.name
	attrs['shortDescription'] = attribute.description
	if attribute.long_description:
		attrs['longDescription'] = attribute.long_description
	if attribute.description_de:
		attrs['translationShortDescription'] = [('de_DE', attribute.description_de)]
	if attribute.long_description_de:
		attrs['translationLongDescription'] = [('de_DE', attribute.long_description_de)]
	attrs['syntax'] = attribute._udm_syntax or attribute.syntax
	attrs['multivalue'] = not attribute.single_value
	if attribute.default:
		attrs['default'] = attribute.default
	attrs['tabPosition'] = str(layout_position)
	attrs['tabName'] = attribute.tab_name
	attrs['groupName'] = app.name
	attrs['ldapMapping'] = attribute.name
	attrs['objectClass'] = attribute.belongs_to
	attrs['module'] = attribute.module
	attrs['deleteObjectClass'] = True
	attrs['mayChange'] = True
	attrs['fullWidth'] = attribute.full_width
#	attrs['hook'] = None
	attrs['disableUDMWeb'] = attribute.disable_web
#	attrs['groupPosition'] = None
#	attrs['tabAdvanced'] = None
#	attrs['overwriteTab'] = None
#	attrs['overwritePosition'] = None
	attrs['valueRequired'] = attribute.required
#	attrs['notEditable'] = None
#	attrs['doNotSearch'] = None
	attrs['copyable'] = attribute.copyable
	attrs['options'] = attribute.options
	attribute_logger.debug('Creating DN: %s' % attribute.dn)
	if not create_object_if_not_exists('settings/extended_attribute', lo, pos, **attrs):
		attribute_logger.debug('... already exists. Overwriting!')
		modify_object('settings/extended_attribute', lo, pos, attribute.dn, **attrs)


def remove_extended_attribute(attribute, lo, pos):
	attribute_logger.debug('Removing DN: %s' % attribute.dn)
	remove_object_if_exists('settings/extended_attribute', lo, pos, attribute.dn)


def create_extended_option(option, app, lo, pos):
	attrs = {}
	option_position = '%s,%s' % (option.position, ucr_get('ldap/base'))
	create_recursive_container(option_position, lo, pos)
	pos.setDn(option_position)
	attrs['name'] = option.name
	attrs['shortDescription'] = option.description
	if option.long_description:
		attrs['longDescription'] = option.long_description
	if option.description_de:
		attrs['translationShortDescription'] = [('de_DE', option.description_de)]
	if option.long_description_de:
		attrs['translationLongDescription'] = [('de_DE', option.long_description_de)]
	attrs['default'] = option.default
	attrs['editable'] = option.editable
	attrs['module'] = option.module
	attrs['objectClass'] = option.object_class
	attrs['isApp'] = '1'
	attribute_logger.debug('Creating DN: %s' % option.dn)
	if not create_object_if_not_exists('settings/extended_options', lo, pos, **attrs):
		attribute_logger.debug('... already exists. Overwriting!')
		modify_object('settings/extended_options', lo, pos, option.dn, **attrs)

	icon = '/usr/share/univention-management-console-frontend/js/dijit/themes/umc/icons/scalable/%s' % (option.icon,)
	if not os.path.exists(icon):
		os.symlink(app.logo_name, icon)


def remove_extended_option(option, lo, pos):
	attribute_logger.debug('Removing DN: %s' % option.dn)
	remove_object_if_exists('settings/extended_option', lo, pos, option.dn)
