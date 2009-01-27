# -*- coding: utf-8 -*-
#
# Univention Admin Modules
#  admin policy for the DHCP dnsupdate settings
#
# Copyright (C) 2004, 2005, 2006 Univention GmbH
#
# http://www.univention.de/
#
# All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# Binary versions of this file provided by Univention to you as
# well as other copyrighted, protected or trademarked materials like
# Logos, graphics, fonts, specific documentations and configurations,
# cryptographic keys etc. are subject to a license agreement between
# you and Univention.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import sys, string
import univention.admin.syntax
import univention.admin.filter
import univention.admin.handlers
import univention.admin.localization

translation=univention.admin.localization.translation('univention.admin.handlers.policies')
_=translation.translate

class dhcp_dnsupdateFixedAttributes(univention.admin.syntax.select):
	name='dhcp_dnsupdateFixedAttributes'
	choices=[
		('univentionDhcpDdnsHostname',_('DDNS Hostname')),
		('univentionDhcpDdnsDomainname',_('DDNS Domainname')),
		('univentionDhcpDdnsRevDomainname',_('DDNS Reverse Domainname')),
		('univentionDhcpDdnsUpdates',_('DDNS Updates')),
		('univentionDhcpDdnsDdnsUpdateStyle',_('DDNS Update Style')),
		('univentionDhcpDdnsDoForwardUpdates',_('DDNS Do Forward Update')),
		('univentionDhcpDdnsUpdateStaticLeases',_('Update Static Leases')),
		('univentionDhcpDdnsClientUpdates',_('Client Updates'))
		]

module='policies/dhcp_dnsupdate'
operations=['add','edit','remove','search']

policy_oc="univentionPolicyDhcpDnsUpdate"
policy_apply_to=["dhcp/host", "dhcp/pool", "dhcp/service", "dhcp/subnet", "dhcp/sharedsubnet", "dhcp/shared"]
policy_position_dn_prefix="cn=dnsupdate,cn=dhcp"
policies_group="dhcp"
usewizard=1
childs=0
short_description=_('Policy: DHCP DNS Update')
policy_short_description=_('DNS Update')
long_description=''
options={
}
property_descriptions={
	'name': univention.admin.property(
			short_description=_('Name'),
			long_description='',
			syntax=univention.admin.syntax.string,
			multivalue=0,
			options=[],
			required=1,
			may_change=0,
			identifies=1,
		),
	'ddnsHostname': univention.admin.property(
			short_description=_('DDNS Hostname'),
			long_description=_("Hostname that will be used for the client's A and PTR records"),
			syntax=univention.admin.syntax.string,
			multivalue=0,
			options=[],
			required=0,
			may_change=1,
			identifies=0
			),
	'ddnsDomainname': univention.admin.property(
			short_description=_('DDNS Domainname'),
			long_description=_("Domain name that will be appended to the client's hostname to form a fully-qualified domain-name (FQDN)"),
			syntax=univention.admin.syntax.string,
			multivalue=0,
			options=[],
			required=0,
			may_change=1,
			identifies=0
			),
	'ddnsRevDomainname': univention.admin.property(
			short_description=_('DDNS Reverse Domainname'),
			long_description=_("Domain name that will be appended to the client's hostname to produce a name for use in the client's PTR record"),
			syntax=univention.admin.syntax.string,
			multivalue=0,
			options=[],
			required=0,
			may_change=1,
			identifies=0
			),
	'ddnsUpdates': univention.admin.property(
			short_description=_('DDNS Updates'),
			long_description=_("Attempt to do a DNS update when a DHCP lease is confirmed"),
			syntax=univention.admin.syntax.ddnsUpdates,
			multivalue=0,
			options=[],
			required=0,
			may_change=1,
			identifies=0
			),
	'ddnsUpdateStyle': univention.admin.property(
			short_description=_('DDNS Update Style'),
			long_description=_("Specify the DDNS Update Style to use for a DHCP Service"),
			syntax=univention.admin.syntax.ddnsUpdateStyle,
			multivalue=0,
			options=[],
			required=0,
			may_change=1,
			identifies=0
			),
	'ddnsDoForwardUpdate': univention.admin.property(
			short_description=_('DDNS Do Forward Update'),
			long_description=_("Attempt to update a DHCP client's A record when the client acquires or renews a lease"),
			syntax=univention.admin.syntax.TrueFalse,
			multivalue=0,
			options=[],
			required=0,
			may_change=1,
			identifies=0
			),
	'updateStaticLeases': univention.admin.property(
			short_description=_('Update Static Leases'),
			long_description=_("Do DNS updates for clients even their IP addresses are assigned using fixed addresses"),
			syntax=univention.admin.syntax.TrueFalse,
			multivalue=0,
			options=[],
			required=0,
			may_change=1,
			identifies=0
			),
	'clientUpdates': univention.admin.property(
			short_description=_('Client Updates'),
			long_description=_("Honor the client's intention to do its own update of its A record"),
			syntax=univention.admin.syntax.AllowDeny,
			multivalue=0,
			options=[],
			required=0,
			may_change=1,
			identifies=0
		),
	'requiredObjectClasses': univention.admin.property(
			short_description=_('Required Object Classes'),
			long_description='',
			syntax=univention.admin.syntax.string,
			multivalue=1,
			options=[],
			required=0,
			may_change=1,
			identifies=0
			),
	'prohibitedObjectClasses': univention.admin.property(
			short_description=_('Prohibited Object Classes'),
			long_description='',
			syntax=univention.admin.syntax.string,
			multivalue=1,
			options=[],
			required=0,
			may_change=1,
			identifies=0
			),
	'fixedAttributes': univention.admin.property(
			short_description=_('Fixed Attributes'),
			long_description='',
			syntax=dhcp_dnsupdateFixedAttributes,
			multivalue=1,
			options=[],
			required=0,
			may_change=1,
			identifies=0
			),
	'emptyAttributes': univention.admin.property(
			short_description=_('Empty Attributes'),
			long_description='',
			syntax=dhcp_dnsupdateFixedAttributes,
			multivalue=1,
			options=[],
			required=0,
			may_change=1,
			identifies=0
			),
	'filler': univention.admin.property(
			short_description='',
			long_description='',
			syntax=univention.admin.syntax.none,
			multivalue=0,
			required=0,
			may_change=1,
			identifies=0,
			dontsearch=1
		)
}
layout=[
	univention.admin.tab(_('DNS Update'), _('Dynamic DNS Update'), [
		[univention.admin.field('name', hide_in_resultmode=1), univention.admin.field('ddnsHostname'), univention.admin.field('filler', hide_in_normalmode=1)],
		[univention.admin.field('ddnsDomainname'), univention.admin.field('ddnsRevDomainname')],
		[univention.admin.field('ddnsUpdates'), univention.admin.field('ddnsUpdateStyle')],
		[univention.admin.field('ddnsDoForwardUpdate'), univention.admin.field('updateStaticLeases')],
		[univention.admin.field('clientUpdates'), univention.admin.field('filler')]
	]),
	univention.admin.tab(_('Object'),_('Object'), [
		[univention.admin.field('requiredObjectClasses') , univention.admin.field('prohibitedObjectClasses') ],
		[univention.admin.field('fixedAttributes'), univention.admin.field('emptyAttributes')]
	], advanced = True),
]

mapping=univention.admin.mapping.mapping()
mapping.register('name', 'cn', None, univention.admin.mapping.ListToString)
mapping.register('ddnsHostname', 'univentionDhcpDdnsHostname', None, univention.admin.mapping.ListToString)
mapping.register('ddnsDomainname', 'univentionDhcpDdnsDomainname', None, univention.admin.mapping.ListToString)
mapping.register('ddnsRevDomainname', 'univentionDhcpDdnsRevDomainname', None, univention.admin.mapping.ListToString)
mapping.register('ddnsUpdates', 'univentionDhcpDdnsUpdates', None, univention.admin.mapping.ListToString)
mapping.register('ddnsUpdateStyle', 'univentionDhcpDdnsUpdateStyle', None, univention.admin.mapping.ListToString)
mapping.register('ddnsDoForwardUpdate', 'univentionDhcpDoForwardUpdates', None, univention.admin.mapping.ListToString)
mapping.register('updateStaticLeases', 'univentionDhcpUpdateStaticLeases', None, univention.admin.mapping.ListToString)
mapping.register('clientUpdates', 'univentionDhcpClientUpdates', None, univention.admin.mapping.ListToString)

mapping.register('requiredObjectClasses', 'requiredObjectClasses')
mapping.register('prohibitedObjectClasses', 'prohibitedObjectClasses')
mapping.register('fixedAttributes', 'fixedAttributes')
mapping.register('emptyAttributes', 'emptyAttributes')

class object(univention.admin.handlers.simplePolicy):
	module=module

	def __init__(self, co, lo, position, dn='', superordinate=None, arg=None):
		global mapping
		global property_descriptions

		self.co=co
		self.lo=lo
		self.dn=dn
		self.position=position
		self._exists=0
		self.mapping=mapping
		self.descriptions=property_descriptions

		univention.admin.handlers.simplePolicy.__init__(self, co, lo, position, dn, superordinate)

	def exists(self):
		return self._exists

	def _ldap_pre_create(self):
		self.dn='%s=%s,%s' % (mapping.mapName('name'), mapping.mapValue('name', self.info['name']), self.position.getDn())

	def _ldap_addlist(self):
		return [
			('objectClass', ['top', 'univentionPolicy', 'univentionPolicyDhcpDnsUpdate'])
		]

def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub', unique=0, required=0, timeout=-1, sizelimit=0):

	filter=univention.admin.filter.conjunction('&', [
		univention.admin.filter.expression('objectClass', 'univentionPolicyDhcpDnsUpdate'),
		])

	if filter_s:
		filter_p=univention.admin.filter.parse(filter_s)
		univention.admin.filter.walk(filter_p, univention.admin.mapping.mapRewrite, arg=mapping)
		filter.expressions.append(filter_p)

	res=[]
	try:
		for dn in lo.searchDn(unicode(filter), base, scope, unique, required, timeout, sizelimit):
			res.append(object(co, lo, None, dn))
	except:
		pass
	return res

def identify(dn, attr, canonical=0):

	return 'univentionPolicyDhcpDnsUpdate' in attr.get('objectClass', [])
