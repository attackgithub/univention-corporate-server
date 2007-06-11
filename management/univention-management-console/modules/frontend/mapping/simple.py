#!/usr/bin/python2.4 -OO
#
# Univention Management Console
#  maps dynamic elements
#
# Copyright (C) 2007 Univention GmbH
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

import mapper
import utils

import univention.management.console.tools as umc_tools

import univention.management.console.dialog as umcd
import univention.management.console as umc

from uniparts import *

_ = umc.Translation( 'univention.management.console.frontend' ).translate

def text_map( storage, umcp_part ):
	return text( '', utils.layout_attrs( storage, umcp_part ),
				 { 'text' : [ umcp_part.get_text() ] } )

for t in umcd.TextTypes:
	mapper.add( t, text_map )


def icon_map( storage, umcp_part ):
	return icon( '', { 'url' : umcp_part.get_image() }, {} )

mapper.add( umcd.Image, icon_map )

def link_map( storage, umcp_part ):
	attributes = utils.attributes( umcp_part )
	if umcp_part.get_icon():
		html = ' <a href="%s" target="_blank"><img class="button_icon" src="/umc/%s" alt="%s"></a>' % \
			   ( umcp_part.get_link(), umc_tools.image_get( umcp_part.get_icon(),
															umc_tools.SIZE_MEDIUM ), umcp_part.get_text() )
	else:
		html = ' <a href="%s" target="_blank">%s</a>' % ( umcp_part.get_link(), umcp_part )
	text = htmltext( '', attributes, { 'htmltext' : [ html ] } )
	storage[ umcp_part.id() ] = ( text, umcp_part )

	return text

mapper.add( umcd.Link, link_map )

def _input_map( storage, umcp_part, attributes ):
	default = utils.default( umcp_part )
	quest = question_text( unicode( umcp_part ), attributes,
						   { 'usertext' : default,
							 'helptext' : '' } )
	storage[ umcp_part.id() ] = ( quest, umcp_part )

	return quest

def textinput_map( storage, umcp_part ):
	return _input_map( storage, umcp_part, utils.layout_attrs( storage, umcp_part ) )

def readonlyinput_map( storage, umcp_part ):
	attributes = utils.attributes( umcp_part )
	attributes.update( { 'passive' : 'true' } )

	return _input_map( storage, umcp_part, attributes )

mapper.add( umcd.TextInput, textinput_map )
mapper.add( umcd.ReadOnlyInput, readonlyinput_map )

def longtext_map( storage, umcp_part ):
	default = utils.default( umcp_part )
	attributes = utils.layout_attrs( storage, umcp_part )
	quest = question_ltext( unicode( umcp_part ), attributes,
						   { 'usertext' : default, 'helptext' : '' } )
	storage[ umcp_part.id() ] = ( quest, umcp_part )

	return quest

mapper.add( umcd.MultiLineInput, longtext_map )

def checkbox_map( storage, umcp_part ):
	attributes = utils.attributes( umcp_part )
	if utils.default( umcp_part ):
		value = '1'
	else:
		value = ''

	attributes.update( { 'usertext' : value, 'helptext' : '' } )
	quest = question_bool( unicode( umcp_part ), utils.layout_attrs( storage, umcp_part ),
						   attributes )
	storage[ umcp_part.id() ] = ( quest, umcp_part )

	return quest

mapper.add( umcd.Checkbox, checkbox_map )

def selection_map( storage, umcp_part ):
	default = utils.default( umcp_part )
	attributes = utils.attributes( umcp_part )
	choices = []
	for key, name in umcp_part.choices():
		if default and key == default:
			choices.append( { 'name' : key, 'description' : name, 'selected' : '1' } )
		else:
			choices.append( { 'name' : key, 'description' : name } )
	attributes.update( { 'choicelist' : choices } )
	quest = question_select( str( umcp_part ), utils.layout_attrs( storage, umcp_part ), attributes )
	storage[ umcp_part.id() ] = ( quest, umcp_part )

	return quest

mapper.add( umcd.Selection, selection_map )
