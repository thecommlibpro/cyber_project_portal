from rest_framework import permissions, viewsets

from members.models import Member
from members.serializers import MemberReadOnlySerializer


class MemberViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Member.objects.all()
    permission_classes = [
        permissions.IsAdminUser,
    ]
    serializer_class = MemberReadOnlySerializer
    filterset_fields = [
        'member_id',
        'member_name',
    ]
    lookup_field = 'member_id'

    def get_object(self) -> Member:
        member = Member.get(self.kwargs[self.lookup_field])

        return member.refresh_from_koha()
