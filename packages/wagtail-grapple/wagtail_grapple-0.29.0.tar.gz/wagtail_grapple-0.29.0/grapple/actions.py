import inspect

from collections.abc import Iterable
from types import MethodType
from typing import Any, Union

import graphene

from django.apps import apps
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from graphene_django.types import DjangoObjectType
from wagtail.blocks import StructValue, stream_block
from wagtail.contrib.settings.models import BaseGenericSetting, BaseSiteSetting
from wagtail.documents.models import AbstractDocument
from wagtail.fields import RichTextField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.models import AbstractImage, AbstractRendition
from wagtail.models import Page as WagtailPage
from wagtail.rich_text import RichText
from wagtail.snippets.models import get_snippet_models

from .helpers import field_middlewares, streamfield_types
from .registry import registry
from .settings import grapple_settings
from .types.documents import DocumentObjectType
from .types.images import ImageObjectType, ImageRenditionObjectType
from .types.pages import Page, get_page_interface
from .types.rich_text import RichText as RichTextType
from .types.snippets import get_snippet_interface
from .types.streamfield import generate_streamfield_union


if apps.is_installed("wagtailmedia"):
    from wagtailmedia.models import AbstractMedia

    from .types.media import MediaObjectType

    has_wagtail_media = True

else:
    # TODO: find a better way to have this as an optional dependency
    class AbstractMedia:
        def __init__(self):
            pass

        def __add__(self, other):
            pass

        def __name__(self):
            pass

    MediaObjectType = None
    has_wagtail_media = False


def import_apps():
    """
    Add each django app set in the settings file
    """

    # Register each app in the django project.
    if isinstance(grapple_settings.APPS, (list, tuple)):
        for name in grapple_settings.APPS:
            add_app(name)
            registry.apps.append(name)
    else:
        apps = grapple_settings.APPS.items()
        for name, prefix in apps:
            add_app(name, prefix)
            registry.apps.append(name)

    # Register any 'decorated' StreamField structs.
    for streamfield_type in streamfield_types:
        cls = streamfield_type["cls"]
        base_type = streamfield_type["base_type"]

        if hasattr(cls, "graphql_types"):
            base_type = generate_streamfield_union(cls.graphql_types)

        node_type = build_streamfield_type(
            cls,
            streamfield_type["type_prefix"],
            streamfield_type["interfaces"],
            base_type,
        )

        registry.streamfield_blocks[streamfield_type["cls"]] = node_type

    registry.field_middlewares = field_middlewares


def add_app(app_label: str, prefix: str = ""):
    """
    Iterate through each model in the app and pass it to node type creators.
    """
    from django.apps import apps

    # Get the required django app.
    app = apps.get_app_config(app_label)

    # Create a collection of models of standard models (Pages, Images, Documents).
    models = list(app.get_models())

    # Add snippet models to the model collection.
    for snippet in get_snippet_models():
        if snippet._meta.app_label == app_label:
            models.append(snippet)

    # Create add each model to correct section of registry.
    for model in models:
        register_model(model, prefix)


def register_model(cls: type, type_prefix: str):
    """
    Pass model to the right node type creator based on it's base class.
    """

    # Pass class to correct type creator.
    if cls is not None:
        if issubclass(cls, WagtailPage):
            register_page_model(cls, type_prefix)
        elif issubclass(cls, AbstractDocument):
            register_document_model(cls, type_prefix)
        elif issubclass(cls, AbstractImage):
            register_image_model(cls, type_prefix)
        elif issubclass(cls, AbstractRendition):
            register_image_rendition_model(cls, type_prefix)
        elif has_wagtail_media and issubclass(cls, AbstractMedia):
            register_media_model(cls, type_prefix)
        elif issubclass(cls, (BaseSiteSetting, BaseGenericSetting)):
            register_settings_model(cls, type_prefix)
        elif cls in get_snippet_models():
            register_snippet_model(cls, type_prefix)
        else:
            register_django_model(cls, type_prefix)


def get_fields_and_properties(cls):
    """
    Return all fields and @property methods for a model.
    """
    from graphene_django.utils import get_model_fields

    # Note: graphene-django use this method to get the model fields
    # cls._meta.get_fields(include_parents=False) includes symmetrical ManyToMany fields, while get_model_fields doesn't
    fields = [field for field, instance in get_model_fields(cls)]

    properties = [
        method[0]
        for method in inspect.getmembers(cls, lambda o: isinstance(o, property))
    ]

    return fields + properties


def get_field_type(field):
    # If a tuple is returned then obj[1] wraps obj[0]
    field_wrapper = None
    if isinstance(field, tuple):
        field, field_wrapper = field
        if callable(field):
            field = field()

    field_type = field.field_type
    if field_type is not None:
        if field_wrapper:
            return field, field_wrapper(field_type)
        else:
            return field, graphene.Field(
                field_type,
                description=field.description,
                deprecation_reason=field.deprecation_reason,
            )


def model_resolver(field):
    def mixin(self, instance, info, **kwargs):
        from .utils import resolve_queryset

        cls_field = getattr(instance, field.field_source)

        # If queryset then call .all() method
        if issubclass(type(cls_field), models.Manager):
            # Shortcut to extract one nested field from an list of objects
            def get_nested_field(cls, extract_key):
                # If last value in list then return that from the class.
                if len(extract_key) == 1:
                    return getattr(cls, extract_key[0])

                # Get data from nested field
                nested_field = getattr(cls, extract_key[0])
                if nested_field is None:
                    return None
                if issubclass(type(nested_field), models.Manager):
                    nested_field = nested_field.all()

                # If field data is a list then iterate over it
                if isinstance(nested_field, Iterable):
                    return [
                        get_nested_field(nested_cls, extract_key[1:])
                        for nested_cls in nested_field
                    ]

                # If single value then return it.
                return get_nested_field(nested_field, extract_key[1:])

            if field.extract_key:
                return [
                    get_nested_field(cls, field.extract_key) for cls in cls_field.all()
                ]

            # Check if any queryset params:
            if not kwargs:
                return cls_field.all()
            return resolve_queryset(cls_field, info, **kwargs)

        # If method then call and return result
        if callable(cls_field):
            return cls_field(info, **kwargs)

        # Expand HTML if the value's field is richtext
        if field.field_type is RichTextType:
            # Rendering of html will be handled by the GraphQL executor calling
            # RichText.serialize, due to being declared as GraphQLRichText rather than
            # GraphQLString
            return cls_field
        try:
            if hasattr(instance._meta, "get_field"):
                field_model = instance._meta.get_field(field.field_source)
            else:
                field_model = instance._meta.fields[field.field_source]
        except FieldDoesNotExist:
            return cls_field

        if type(field_model) is RichTextField:
            return RichTextType.serialize(cls_field)

        # If none of those then just return field
        return cls_field

    return mixin


def build_node_type(
    cls: type,
    type_prefix: str,
    interface: graphene.Interface,
    base_type: type[DjangoObjectType] = DjangoObjectType,
):
    """
    Build a graphene node type from a model class and associate
    with an interface. If it has custom fields then implement them.
    """
    type_name = type_prefix + cls.__name__

    # Create a temporary model and temporary node that will be replaced later on.
    class UnmanagedMeta:
        app_label = type_name
        managed = False

    stub_model = type(
        type_name, (models.Model,), {"__module__": "", "Meta": UnmanagedMeta}
    )

    class StubMeta:
        model = stub_model

    # Gather any interfaces, and discard None values
    interfaces = {interface, *getattr(cls, "graphql_interfaces", ())}
    interfaces.discard(None)

    type_meta = {
        "Meta": StubMeta,
        "type": lambda: {
            "cls": cls,
            "lazy": True,
            "name": type_name,
            "base_type": base_type,
            "interfaces": tuple(interfaces),
        },
    }

    return type(f"Stub{type_name}", (base_type,), type_meta)


def load_type_fields():
    for list_name in registry.lazy_types:
        type_list = getattr(registry, list_name)

        for key, node in type_list.items():
            type_definition = node.type()
            if type_definition.get("lazy"):
                # Get the original django model data
                cls = type_definition.get("cls")
                base_type = type_definition.get("base_type")
                type_name = type_definition.get("name")
                _interfaces = type_definition.get("interfaces")

                # Recreate the graphene type with the fields set
                class Meta:
                    model = cls
                    interfaces = _interfaces if _interfaces is not None else ()

                type_meta = {"Meta": Meta, "id": graphene.ID(), "name": type_name}

                exclude_fields = []
                base_type_for_exclusion_checks = (
                    base_type if not issubclass(cls, WagtailPage) else WagtailPage
                )
                for field in get_fields_and_properties(cls):
                    # Filter out any fields that are defined on the interface of base type to prevent the
                    # 'Excluding the custom field "<field>" on DjangoObjectType "<cls>" has no effect.
                    # Either remove the custom field or remove the field from the "exclude" list.' warning
                    if (
                        field == "id"
                        or hasattr(base_type_for_exclusion_checks, field)
                        or any(hasattr(interface, field) for interface in _interfaces)
                    ):
                        continue

                    exclude_fields.append(field)

                # Add any custom fields to node if they are defined.
                methods = {}
                if hasattr(cls, "graphql_fields"):
                    for field in cls.graphql_fields:
                        if callable(field):
                            field = field()

                        # Add field to GQL type with correct field-type
                        field, field_type = get_field_type(field)
                        type_meta[field.field_name] = field_type

                        # Remove field from excluded list
                        if field.field_name in exclude_fields:
                            exclude_fields.remove(field.field_name)

                        # Add a custom resolver for each field
                        methods[f"resolve_{field.field_name}"] = model_resolver(field)

                # Replace stud node with real thing
                type_meta["Meta"].exclude_fields = exclude_fields
                node = type(type_name, (base_type,), type_meta)

                # Add custom resolvers for fields
                for name, method in methods.items():
                    setattr(node, name, MethodType(method, node))

                # Update list with new node
                type_list[key] = node


def convert_to_underscore(name):
    import re

    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def get_field_value(instance, field_name: str):
    """
    Returns the value of a given field on an object of a StreamField.

    Different types of objects require different ways to access the values.
    """
    if isinstance(instance, StructValue):
        return instance[field_name]
    elif isinstance(instance.value, RichText):
        return RichTextType.serialize(instance.value.source)
    elif isinstance(instance.value, stream_block.StreamValue):
        stream_data = dict(instance.value.stream_data)
        return stream_data[field_name]
    else:
        return instance.value[field_name]


def get_all_field_values(*, instance, cls) -> dict[str, Any]:
    """
    Returns a dictionary of all fields and their values within a given stream
    block instance.
    """

    values: dict[str, Any] = {}
    for item in cls.base_blocks.items():
        field_name: str = item[0]
        values[field_name] = get_field_value(
            instance=instance,
            field_name=field_name,
        )

    return values


def streamfield_resolver(self, instance, info, **kwargs):
    value = None
    if hasattr(instance, "block"):
        field_name = convert_to_underscore(info.field_name)
        block = instance.block.child_blocks[field_name]

        if not block:
            return None

        value = get_field_value(instance, field_name)
        if issubclass(type(block), ImageChooserBlock) and isinstance(value, int):
            return block.to_python(value)

    return value


def custom_cls_resolver(*, cls, graphql_field):
    klass = cls()

    # If we've defined a `source` kwarg: use it.
    if hasattr(graphql_field, "field_source") and hasattr(
        klass, graphql_field.field_source
    ):
        if isinstance(getattr(type(cls()), graphql_field.field_source), property):
            return lambda self, instance, info, **kwargs: getattr(
                klass, graphql_field.field_source
            )
        elif callable(getattr(cls, graphql_field.field_source)):
            return lambda self, instance, info, **kwargs: getattr(
                klass, graphql_field.field_source
            )(
                info=info,
                values=get_all_field_values(instance=instance, cls=cls),
                **kwargs,
            )

    # If the `field_name` is a property or method of the class: use it.
    if hasattr(graphql_field, "field_name") and hasattr(
        klass, graphql_field.field_name
    ):
        if isinstance(getattr(type(cls()), graphql_field.field_name), property):
            return lambda self, instance, info, **kwargs: getattr(
                klass, graphql_field.field_name
            )
        elif callable(getattr(cls, graphql_field.field_name)):
            return lambda self, instance, info, **kwargs: getattr(
                klass, graphql_field.field_name
            )(
                info=info,
                values=get_all_field_values(instance=instance, cls=cls),
                **kwargs,
            )

    # No match found - fall back to the streamfield_resolver() later.
    return None


def build_streamfield_type(
    cls: type,
    type_prefix: str,
    interfaces: tuple[graphene.Interface],
    base_type=graphene.ObjectType,
):
    """
    Build a graphql type for a StreamBlock or StructBlock class
    If it has custom fields then implement them.
    """

    # Alias the argument name so we can use it in the class block
    _interfaces = interfaces

    # Create a new blank node type
    class Meta:
        if hasattr(cls, "graphql_types"):
            types = [
                registry.streamfield_blocks.get(block) for block in cls.graphql_types
            ]
        else:
            interfaces = _interfaces if _interfaces is not None else ()
        # Add description to type if the Meta class declares it
        description = getattr(cls._meta_class, "graphql_description", None)

    methods = {}
    type_name = type_prefix + cls.__name__
    type_meta = {"Meta": Meta, "id": graphene.String()}

    # Add any custom fields to node if they are defined.
    if hasattr(cls, "graphql_fields"):
        for item in cls.graphql_fields:
            if callable(item):
                item = item()

            # Get correct types from field
            field, field_type = get_field_type(item)

            # Add support for `graphql_fields`
            methods[f"resolve_{field.field_name}"] = (
                custom_cls_resolver(cls=cls, graphql_field=field)
                or streamfield_resolver
            )

            # Add field to GQL type with correct field-type
            type_meta[field.field_name] = field_type

    # Set excluded fields to stop errors cropping up from unsupported field types.
    graphql_node = type(type_name, (base_type,), type_meta)

    for name, method in methods.items():
        setattr(graphql_node, name, MethodType(method, graphql_node))

    return graphql_node


def register_page_model(cls: type[WagtailPage], type_prefix: str):
    """
    Create graphene node type for models than inherit from Wagtail Page model.
    """

    # Avoid gql type duplicates
    if cls in registry.pages:
        return

    # Create a GQL type derived from the page model.
    if page_node_type := build_node_type(cls, type_prefix, get_page_interface(), Page):
        # Add page type to registry.
        registry.pages[cls] = page_node_type


def register_document_model(cls: type[AbstractDocument], type_prefix: str):
    """
    Create graphene node type for a model than inherits from AbstractDocument.
    Only one model will actually be generated because a default document model
    needs to be set in settings.
    """

    # Avoid gql type duplicates
    if cls in registry.documents:
        return

    # Create a GQL type derived from the document model.
    if document_node_type := build_node_type(
        cls, type_prefix, None, DocumentObjectType
    ):
        # Add document type to registry.
        registry.documents[cls] = document_node_type


def register_image_model(cls: type[AbstractImage], type_prefix: str):
    """
    Create a graphene node type for a model than inherits from AbstractImage.
    Only one type will actually be generated because a default image model
    needs to be set in settings.
    """

    # Avoid gql type duplicates
    if cls in registry.images:
        return

    # Create a GQL type derived from the image model.
    if image_node_type := build_node_type(cls, type_prefix, None, ImageObjectType):
        # Add image type to registry.
        registry.images[cls] = image_node_type


def register_image_rendition_model(cls: type[AbstractRendition], type_prefix: str):
    """
    Create a graphene node type for a model than inherits from AbstractImageRendition.
    Only one type will actually be generated because a default image model
    needs to be set in settings.
    """

    if cls in registry.images:
        return

    # Create a GQL type derived from the image rendition model.
    if rendition_type := build_node_type(
        cls, type_prefix, None, ImageRenditionObjectType
    ):
        registry.images[cls] = rendition_type


def register_media_model(cls: type[AbstractMedia], type_prefix: str):
    """
    Create graphene node type for a model than inherits from AbstractDocument.
    Only one model will actually be generated because a default document model
    needs to be set in settings.
    """

    if cls in registry.media:
        return

    # Create a GQL type derived from the media model.
    if media_node_type := build_node_type(cls, type_prefix, None, MediaObjectType):
        registry.media[cls] = media_node_type


def register_settings_model(
    cls: Union[type[BaseSiteSetting], type[BaseGenericSetting]], type_prefix: str
):
    """
    Create a graphene node type for a settings page.
    """

    if cls in registry.settings:
        return

    # Create a GQL type that for the Settings model
    if settings_node_type := build_node_type(cls, type_prefix, None):
        registry.settings[cls] = settings_node_type


def register_snippet_model(cls: type[models.Model], type_prefix: str):
    """
    Create a graphene type for a snippet model.
    """

    if cls in registry.snippets:
        return

    # Create a GQL type that implements Snippet Interface
    snippet_node_type = build_node_type(cls, type_prefix, get_snippet_interface())

    if snippet_node_type:
        registry.snippets[cls] = snippet_node_type


def register_django_model(cls: type[models.Model], type_prefix: str):
    """
    Create a graphene type for (non-specific) Django model.
    Used for Orderables and other foreign keys.
    """

    # Avoid gql type duplicates
    if cls in registry.django_models:
        return

    # Create a GQL type for the non-specific Django model.
    if django_node_type := build_node_type(cls, type_prefix, None):
        registry.django_models[cls] = django_node_type
