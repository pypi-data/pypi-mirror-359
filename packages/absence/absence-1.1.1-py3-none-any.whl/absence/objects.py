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


''' Absence sentinel factory, global singleton, and helper functions. '''


from __future__ import annotations

import falsifier as _falsifier

from . import __


class AbsenceFactory( _falsifier.Falsifier ):
    ''' Produces arbitrary absence sentinels. '''

    def __init__(
        self,
        repr_function: __.typx.Annotated[
            __.typx.Optional[ __.cabc.Callable[ [ __.typx.Self ], str ] ],
            __.dynadoc.Doc( ''' Function for __repr__. ''' )
        ] = None,
        str_function: __.typx.Annotated[
            __.typx.Optional[ __.cabc.Callable[ [ __.typx.Self ], str ] ],
            __.dynadoc.Doc( ''' Function for __str__. ''' )
        ] = None,
    ) -> None:
        self._repr_function = repr_function
        self._str_function = str_function
        super( ).__init__( )

    def __repr__( self ) -> str:
        if self._repr_function is not None:
            return self._repr_function( self )
        return 'absence.AbsenceFactory( )'

    def __str__( self ) -> str:
        if self._str_function is not None:
            return self._str_function( self )
        return 'absence'

    def __reduce__( self ) -> __.typx.Never:
        from .exceptions import OperationValidityError
        raise OperationValidityError( 'pickle' )


class AbsentSingleton( AbsenceFactory ):
    ''' Produces global absence sentinel. '''
    # TODO: Instance immutability after initialization.

    def __new__( selfclass ) -> __.typx.Self:
        absent_ = globals( ).get( 'absent' )
        if isinstance( absent_, selfclass ): return absent_
        return super( ).__new__( selfclass )

    def __repr__( self ) -> str:
        return 'absence.absent'

    def __str__( self ) -> str:
        return 'absent'


absent: __.typx.Annotated[
    AbsentSingleton, __.dynadoc.Doc( ''' Global absence sentinel. ''' )
] = AbsentSingleton( )


def is_absence( value: object ) -> __.typx.TypeIs[ AbsenceFactory ]:
    ''' Checks if value is an absence sentinel. '''
    return isinstance( value, AbsenceFactory )


def is_absent( value: object ) -> __.typx.TypeIs[ AbsentSingleton ]:
    ''' Checks if value is the global absence sentinel. '''
    return absent is value


# Note: Separate typevar definition because it is less confusing to Pyright.
_V = __.typx.TypeVar( '_V' )
Absential: __.typx.TypeAlias = _V | AbsentSingleton


def _typecheck_me( arg: Absential[ int ] = absent ): # pragma: no cover
    # Note: Not part of public interface.
    #       Exists to help identify type issues
    #       since test code is exempt from type checking at this time.
    if is_absent( arg ): return 'absent'
    return arg
