import logging

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_haystack.filters import (
    HaystackFacetFilter,
    HaystackOrderingFilter,
)
from drf_haystack.mixins import FacetMixin
from drf_haystack.viewsets import HaystackViewSet
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from haystack.query import RelatedSearchQuerySet

from api_v2.models.Credential import Credential
from api_v2.search.filters import (
    AutocompleteFilter,
    CategoryFilter,
    CredNameFilter,
    StatusFilter,
)
from api_v2.serializers.search import (
    CredentialAutocompleteSerializer,
    CredentialSearchSerializer,
    CredentialFacetSerializer,
    CredentialTopicSearchSerializer,
)
from tob_api.pagination import ResultLimitPagination

LOGGER = logging.getLogger(__name__)


class NameAutocompleteView(HaystackViewSet):
    """
    Return autocomplete results for a query string
    """
    permission_classes = (permissions.AllowAny,)
    pagination_class = ResultLimitPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "q",
                openapi.IN_QUERY,
                description="Query string",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "inactive",
                openapi.IN_QUERY,
                description="Show inactive credentials",
                type=openapi.TYPE_STRING,
                enum=["any", "false", "true"],
                default="any",
            ),
            openapi.Parameter(
                "latest",
                openapi.IN_QUERY,
                description="Show only latest credentials",
                type=openapi.TYPE_STRING,
                enum=["any", "false", "true"],
                default="true",
            ),
            openapi.Parameter(
                "revoked",
                openapi.IN_QUERY,
                description="Show revoked credentials",
                type=openapi.TYPE_STRING,
                enum=["any", "false", "true"],
                default="false",
            ),
            #openapi.Parameter(
            #    "hl", openapi.IN_QUERY, description="Highlight search term", type=openapi.TYPE_BOOLEAN
            #),
        ])
    def list(self, *args, **kwargs):
        return super(NameAutocompleteView, self).list(*args, **kwargs)
    retrieve = None

    index_models = [Credential]
    load_all = True
    serializer_class = CredentialAutocompleteSerializer
    # enable normal filtering
    filter_backends = [
        AutocompleteFilter,
        CategoryFilter,
        StatusFilter,
        HaystackOrderingFilter,
    ]
    ordering_fields = ('effective_date', 'revoked_date', 'score')
    ordering = ('-score')


class CredentialSearchView(HaystackViewSet, FacetMixin):
    """
    Provide credential search via Solr with both faceted (/facets) and unfaceted results
    """

    permission_classes = (permissions.AllowAny,)

    _swagger_params = [
        openapi.Parameter(
            "name",
            openapi.IN_QUERY,
            description="Filter credentials by related name or topic source ID",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "inactive",
            openapi.IN_QUERY,
            description="Show inactive credentials",
            type=openapi.TYPE_STRING,
            enum=["any", "false", "true"],
            default="false",
        ),
        openapi.Parameter(
            "latest",
            openapi.IN_QUERY,
            description="Show only latest credentials",
            type=openapi.TYPE_STRING,
            enum=["any", "false", "true"],
            default="true",
        ),
        openapi.Parameter(
            "revoked",
            openapi.IN_QUERY,
            description="Show revoked credentials",
            type=openapi.TYPE_STRING,
            enum=["any", "false", "true"],
            default="false",
        ),
    ]
    list = swagger_auto_schema(
        manual_parameters=_swagger_params,
    )(HaystackViewSet.list)
    retrieve = swagger_auto_schema(
        manual_parameters=_swagger_params,
    )(HaystackViewSet.retrieve)

    index_models = [Credential]
    load_all = True
    serializer_class = CredentialSearchSerializer
    # enable normal filtering
    filter_backends = [
        CredNameFilter,
        CategoryFilter,
        StatusFilter,
        HaystackOrderingFilter,
    ]
    facet_filter_backends = [
        CredNameFilter,
        CategoryFilter,
        StatusFilter,
        HaystackOrderingFilter,
        HaystackFacetFilter,
    ]
    facet_serializer_class = CredentialFacetSerializer
    facet_objects_serializer_class = CredentialSearchSerializer
    ordering_fields = ('effective_date', 'revoked_date', 'score')
    ordering = ('-score')

    # FacetMixin provides /facets


class TopicSearchQuerySet(RelatedSearchQuerySet):
    """
    Optimize queries when fetching topic-oriented credential search results
    """

    def __init__(self, *args, **kwargs):
        super(TopicSearchQuerySet, self).__init__(*args, **kwargs)
        self._load_all_querysets[Credential] = self.topic_queryset()

    def topic_queryset(self):
        return Credential.objects.select_related(
            "credential_type",
            "credential_type__issuer",
            "credential_type__schema",
            "topic",
        ).all()


class CredentialTopicSearchView(CredentialSearchView):

    object_class = TopicSearchQuerySet
    serializer_class = CredentialTopicSearchSerializer
    facet_objects_serializer_class = CredentialTopicSearchSerializer
