from django import forms

from posts.models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        help_texts = {
            'text': ('Введите текст поста'),
            'group': ('Выберите группу для поста'),
            'image': ('Добавьте картинку к посту'),
        }

    def clean_text(self):
        data = self.cleaned_data['text']
        if data == '':
            raise forms.ValidationError('Поле не может быть пустым')
        return data
