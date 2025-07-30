from __future__ import annotations

import sys
import types
import typing
import warnings
from collections.abc import Callable, Mapping

import typing_extensions

from streamlit_typed_session.descriptors import DefaultSessionVariableDescriptor, SessionVariableDescriptor
from streamlit_typed_session.mytypes import (
    SessionStateKey,
    SessionStateLike,
    SessionStateProvider,
    SessionStateValue,
    Unset,
    UnsetType,
)
from streamlit_typed_session.providers import streamlit_session_provider

_IGNORED_TYPES: tuple[type, ...] = (
    types.FunctionType,
    types.BuiltinFunctionType,
    types.BuiltinMethodType,
    property,
    classmethod,
    staticmethod,
    typing_extensions.TypeAliasType,
)
if sys.version_info >= (3, 12):
    _IGNORED_TYPES = (*_IGNORED_TYPES, typing.TypeAliasType)

__all__ = ["SessionBase"]


class _SessionModelMetaclass(type):
    def __new__(
        cls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, typing.Any],
        *,
        mute_warnings: bool = False,
        state: SessionStateLike | SessionStateProvider = streamlit_session_provider,
    ) -> _SessionModelMetaclass:
        if isinstance(state, Callable):
            state = state()

        namespace["__state__"] = state

        descriptors: dict[str, SessionVariableDescriptor[typing.Any]] = {}
        namespace["__session_variables__"] = descriptors

        annotations = typing.cast("dict[str, typing.Any]", namespace.get("__annotations__", {}))

        for attribute, annotation in annotations.items():
            if attribute.startswith("_"):  # Skip private attributes
                continue
            session_key = f"__{namespace['__module__']}.{namespace['__qualname__']}.{attribute}__"

            if isinstance(annotation, str):
                annotation = typing.ForwardRef(annotation, is_argument=False, is_class=True)  # noqa: PLW2901
            annotation = cls._eval_type(annotation, globals(), namespace)  # noqa: PLW2901

            is_type_state_var = cls._is_type_state_var(annotation)
            if attribute in namespace and is_type_state_var and not mute_warnings:
                warnings.warn(
                    f"Attribute '{attribute}' defines a default value but also has type-hint for '{Unset.__name__}'."
                    " Session variables with default values will never be unset so this type-hint is not required."
                    f" To suppress this warning remove the '{Unset.__name__}' type annotation or"
                    f" set 'no_warnings' to 'True' when inheriting '{SessionBase.__name__}'.",
                    stacklevel=3,
                )
            elif attribute not in namespace and not is_type_state_var and not mute_warnings:
                warnings.warn(
                    f"Attribute '{attribute}' does not have '{Unset.__name__}' in its type annotation"
                    " and does not have a default value either."
                    " This causes issues with type-checkers. "
                    f" To suppress this warning add '{Unset.__name__}' into the type annotation or"
                    f" set 'no_warnings' to 'True' when inheriting '{SessionBase.__name__}'.",
                    stacklevel=3,
                )

            descriptor = (
                DefaultSessionVariableDescriptor[typing.Any](state, session_key, default=namespace[attribute])
                if attribute in namespace
                else SessionVariableDescriptor[typing.Any](state, session_key)
            )
            namespace[attribute] = descriptor
            descriptors[attribute] = descriptor

        for attribute, value in namespace.items():
            if attribute.startswith("_"):  # Skip private attributes
                continue

            if attribute in descriptors:
                continue

            if any(isinstance(value, t) for t in _IGNORED_TYPES):
                continue

            session_key = f"__{namespace['__module__']}.{namespace['__qualname__']}.{attribute}__"

            descriptor = DefaultSessionVariableDescriptor(state, session_key, default=value)
            namespace[attribute] = descriptor
            descriptors[attribute] = descriptor

        return super().__new__(cls, name, bases, namespace)

    @staticmethod
    def _is_type_state_var(inspected: type | types.UnionType) -> bool:
        origin = typing.get_origin(inspected)
        if origin is not typing.Union and origin is not types.UnionType:
            return False

        return UnsetType in typing.get_args(inspected)

    @staticmethod
    def _eval_type(
        t: typing.ForwardRef | types.GenericAlias | types.UnionType,
        globalns: dict[str, typing.Any] | None,
        localns: Mapping[str, typing.Any] | None,
        type_params: object = (),
        *,
        recursive_guard: frozenset[str] = frozenset(),
    ) -> typing.Any:  # noqa: ANN401
        # TODO: fix type_params
        return typing._eval_type(  # noqa: SLF001
            t,
            globalns,
            localns,
            type_params,
            recursive_guard=recursive_guard,
        )


class SessionBase(metaclass=_SessionModelMetaclass):
    __session_variables__: typing.ClassVar[dict[str, SessionVariableDescriptor[typing.Any]]]
    __state__: typing.ClassVar[SessionStateLike]

    @typing.final
    def __init__(self) -> None: ...

    @classmethod
    def get_session_variables(
        cls,
    ) -> list[SessionVariableDescriptor[typing.Any]]:
        return list(cls.__session_variables__.values())

    @classmethod
    def get_session_variable(cls, name: str) -> SessionVariableDescriptor[typing.Any]:
        if name not in cls.__session_variables__:
            msg = f"attribute '{name}' is not a session variable"
            raise AttributeError(msg)

        return cls.__session_variables__[name]

    @typing.overload
    @classmethod
    def get_state(
        cls,
    ) -> types.MappingProxyType[SessionStateKey, SessionStateValue]: ...

    @typing.overload
    @classmethod
    def get_state(cls, read_only: typing.Literal[False]) -> SessionStateLike: ...

    @typing.overload
    @classmethod
    def get_state(
        cls, *, read_only: bool = True
    ) -> types.MappingProxyType[SessionStateKey, SessionStateValue] | SessionStateLike: ...

    @classmethod
    def get_state(
        cls, *, read_only: bool = True
    ) -> types.MappingProxyType[SessionStateKey, SessionStateValue] | SessionStateLike:
        if read_only:
            return types.MappingProxyType(cls.__state__)

        return cls.__state__
