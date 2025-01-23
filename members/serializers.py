from rest_framework import serializers

from members.models import Member


class MemberReadOnlySerializer(serializers.ModelSerializer):
    last_login = serializers.SerializerMethodField(read_only=True)

    def get_last_login(self, member: Member):
        return member.member_logs.order_by('-entered_date').values_list('entered_date').first()

    class Meta:
        model = Member
        fields = [
            'member_id',
            'member_name',
            'age',
            'gender',
            'first_login_at',
            'last_login',
        ]
