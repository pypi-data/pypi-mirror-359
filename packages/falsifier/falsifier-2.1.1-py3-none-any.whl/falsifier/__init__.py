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


''' Production of falsey objects.

    Provides a base class for creating objects that evaluate to ``False`` in
    boolean contexts. This functionality is useful for creating sentinel
    objects, absence indicators, and other specialized falsey types which need
    distinct identities and proper comparison behavior.
'''


from . import __
# --- BEGIN: Injected by Copier ---
# --- END: Injected by Copier ---

from .classes import *


__version__ = '2.1.1'


__.ccstd.finalize_module( __name__, recursive = True )
