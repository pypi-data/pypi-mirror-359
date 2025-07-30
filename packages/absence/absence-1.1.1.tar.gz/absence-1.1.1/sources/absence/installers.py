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


''' Convenience to expose global sentinel and sentinel checker in builtins. '''


from __future__ import annotations

from . import __


def install(
    sentinel_name: __.typx.Annotated[
        str | None,
        __.dynadoc.Doc(
            ''' Name to use for sentinel in builtins. ``None`` to skip. ''' )
    ] = 'Absent', # Follows builtins convention: Ellipsis, None, NotImplemented
    predicate_name: __.typx.Annotated[
        str | None,
        __.dynadoc.Doc(
            ''' Name to use for predicate in builtins. ``None`` to skip. ''' )
    ] = 'isabsent', # Follows builtins convention: isinstance, issubclass
) -> None:
    ''' Installs absence sentinel and predicate as builtins. '''
    builtins = __import__( 'builtins' )
    from .objects import absent, is_absent
    if sentinel_name: setattr( builtins, sentinel_name, absent )
    if predicate_name: setattr( builtins, predicate_name, is_absent )
