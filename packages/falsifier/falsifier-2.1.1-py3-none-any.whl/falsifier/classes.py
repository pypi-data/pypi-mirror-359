# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Falsifier production. '''


from . import __


class Falsifier:
    ''' Produces falsey objects. '''

    def __bool__( self ) -> bool: return False

    def __hash__( self ) -> int: return id( self )

    def __repr__( self ) -> str:
        return "{fqname}( )".format(
            fqname = __.ccutils.qualify_class_name( type( self ) ) )

    def __str__( self ) -> str: return 'False_'

    def __lt__( self, other: __.typx.Any ) -> __.ComparisonResult:
        return NotImplemented

    def __le__( self, other: __.typx.Any ) -> __.ComparisonResult:
        return NotImplemented

    def __eq__( self, other: __.typx.Any ) -> __.ComparisonResult:
        return self is other

    def __ge__( self, other: __.typx.Any ) -> __.ComparisonResult:
        return NotImplemented

    def __gt__( self, other: __.typx.Any ) -> __.ComparisonResult:
        return NotImplemented

    def __ne__( self, other: __.typx.Any ) -> __.ComparisonResult:
        return self is not other
