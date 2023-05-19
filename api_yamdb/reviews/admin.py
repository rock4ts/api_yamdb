from django.contrib import admin

from .models import Category, Comment, Genre, GenreTitle, Review, Title, User


class AdminUser(admin.ModelAdmin):
    model = User
    list_display = (
        'pk', 'username', 'email', 'first_name', 'last_name', 'bio', 'role'
    )
    list_editable = ('role',)
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('role',)
    empty_value_display = '-пусто-'


class AdminCategory(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('pk', 'name', 'slug')


class AdminGenre(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('pk', 'name', 'slug')


class AdminGenreInline(admin.TabularInline):
    model = GenreTitle


# class AdminGenreTitle(admin.ModelAdmin):
#     list_display = ('pk', 'genre', 'title')
#     model = GenreTitle


class AdminTitle(admin.ModelAdmin):
    fields = ('name', 'category', 'year')
    inlines = (AdminGenreInline,)
    list_display = ('pk', 'name', 'year', 'category', 'get_genres')
    search_fields = ('pk', 'name', 'year', 'category__name', 'genre__name')
    list_filter = ('category', 'genre',)

    def get_genres(self, obj):
        fetch_genres = Genre.objects.all()
        return [
            fetch_genres.filter(pk=genre.genre_id)[0].name
            for genre in obj.genres.all()
        ]
    get_genres.short_description = 'Жанр'


class AdminReview(admin.ModelAdmin):
    list_display = ('pk', 'title_id', 'text', 'author', 'score')
    list_editable = ('score',)
    search_fields = ('text', 'author', 'score', 'title_id',)
    list_filter = ('score',)


class AdminComment(admin.ModelAdmin):
    list_display = ('pk', 'get_title_id', 'review_id', 'text', 'author')
    search_fields = ('text', 'author', 'review_id',)

    def get_title_id(self, obj):
        fetch_titles = Title.objects.all()
        return fetch_titles.get(pk=obj.review.title_id).id
    get_title_id.short_description = 'Title ID'


admin.site.register(User, AdminUser)
admin.site.register(Category, AdminCategory)
admin.site.register(Genre, AdminGenre)
admin.site.register(Title, AdminTitle)
admin.site.register(Review, AdminReview)
admin.site.register(Comment, AdminComment)
# admin.site.register(GenreTitle, AdminGenreTitle)
