from django.contrib import admin

from reviews.models import Comment, Review, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'bio',
        'role',
    )


admin.site.register(User)
admin.site.register(Review)
admin.site.register(Comment)
