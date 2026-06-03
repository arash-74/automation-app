from django.contrib import admin

from dataentry.models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'author')
    ordering = ('id',)
